import logging
from collections.abc import AsyncGenerator
from typing import Any

import ujson
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from litellm import completion

from ..models.chat import ChatDataEntity, ChatEntity
from ..models.enums import ContentType, Role
from .chat_service import ChatDomainService

logger = logging.getLogger(__name__)

class LLMDomainService:
    """LLM领域服务，处理与大模型交互的核心逻辑"""

    def __init__(
        self,
        mcp_server_url: str,
        model: str,
        api_key: str,
        api_base: str,
        chat_domain_service: ChatDomainService
    ):
        self.client = Client(transport=StreamableHttpTransport(url=mcp_server_url))
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.chat_service = chat_domain_service

    async def gen_chat_data(
        self,
        chat_id: int,
        content: str,
        role: str = Role.ASSISTANT,
        content_type: str = ContentType.MSG,
        extra: dict = None
    ) -> dict[str, Any] | None:
        """
        生成聊天数据
        
        Args:
            chat_id: 聊天ID
            content: 内容
            role: 角色
            content_type: 内容类型
            extra: 额外参数
            
        Returns:
            内容和类型
        """
        content = content.lstrip("\n")
        if content:
            await self.chat_service.create_message(
                chat_id=chat_id,
                content=content,
                role=role,
                content_type=content_type,
                extra=extra
            )
            return {"content": content, "content_type": content_type}
        return None

    async def chat(
        self,
        chat: ChatEntity,
        messages: list[ChatDataEntity]
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        与LLM进行对话
        
        Args:
            chat: 聊天实体
            messages: 历史消息列表
            
        Yields:
            响应内容
        """
        formatted_messages = await self._build_messages(chat, messages)
        tools = await self._get_tools()

        # 首次请求
        response = await self._chat_llm(formatted_messages, tools)
        message = response.choices[0].message
        tool_calls = message.tool_calls

        # 生成主要回复内容
        data = await self.gen_chat_data(chat.id, message.content)
        if data:
            yield data

        # 生成推理内容(如果有)
        if hasattr(message, "reasoning_content"):
            data = await self.gen_chat_data(
                chat.id,
                message.reasoning_content,
                content_type=ContentType.REASONING
            )
            if data:
                yield data

        # 如果没有工具调用，结束
        if not tool_calls:
            return

        # 将LLM回复添加到消息历史
        formatted_messages.append(message)

        # 处理工具调用
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            try:
                # 调用工具函数
                function_response = await self._function_call(tool_call)
                message = {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            except Exception as e:
                logger.error(f"tool_call error: {e!s}")
                message = {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": f"调用工具时出错: {e!s}",
                }

            # 记录工具调用结果
            extra = {
                "tool_call_id": tool_call.id,
                "name": function_name,
            }
            data = await self.gen_chat_data(
                chat.id,
                message.get("content"),
                role=Role.TOOL,
                content_type=ContentType.TOOL,
                extra=extra
            )
            if data:
                yield data

            formatted_messages.append(message)

        # 二次调用LLM，处理工具结果
        second_response = await self._chat_llm(formatted_messages)
        data = await self.gen_chat_data(chat.id, second_response.choices[0].message.content)
        if data:
            yield data

    async def _function_call(self, tool_call) -> str:
        """
        调用工具函数
        
        Args:
            tool_call: 工具调用对象
            
        Returns:
            工具调用结果
        """
        async with self.client as client:
            function_name = tool_call.function.name
            arguments = ujson.loads(tool_call.function.arguments)
            logger.info(f"tool_call function name: {function_name}")
            logger.info(f"tool_call arguments: {arguments}")
            result = await client.call_tool(function_name, arguments)
            return result[0].text

    async def _chat_llm(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] = None
    ):
        """
        调用LLM进行对话
        
        Args:
            messages: 消息列表
            tools: 工具列表
            
        Returns:
            LLM响应
        """
        response = completion(
            model=self.model,
            api_key=self.api_key,
            api_base=self.api_base,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        return response

    async def _build_messages(
        self,
        chat: ChatEntity,
        messages: list[ChatDataEntity]
    ) -> list[dict[str, Any]]:
        """
        构建消息列表
        
        Args:
            chat: 聊天实体
            messages: 聊天数据列表
            
        Returns:
            格式化后的消息列表
        """
        formatted_messages = [
            {"role": "system", "content": chat.get_formatted_system_prompt()},
        ]

        for message in messages:
            formatted_messages.append({
                "role": message.role,
                "content": message.content
            })

        return formatted_messages

    async def _get_tools(self) -> list[dict[str, Any]]:
        """
        获取工具列表
        
        Returns:
            格式化后的工具列表
        """
        async with self.client as client:
            tools = await client.list_tools()
            return [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                }
                for tool in tools
            ]
