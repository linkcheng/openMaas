from typing import Any

from ..models.chat import (
    ChatDataEntity,
    ChatEntity,
    ChatToolEntity,
)
from ..models.enums import ContentType, PromptType, Role
from ..repositories.chat_repository import (
    IChatDataRepository,
    IChatRepository,
    IChatToolRepository,
    IPromptRepository,
    ISourceRepository,
)


class ChatDomainService:
    """聊天领域服务，实现核心业务逻辑"""

    def __init__(
        self,
        chat_repo: IChatRepository,
        chat_data_repo: IChatDataRepository,
        chat_tool_repo: IChatToolRepository,
        source_repo: ISourceRepository,
        prompt_repo: IPromptRepository
    ):
        self.chat_repo = chat_repo
        self.chat_data_repo = chat_data_repo
        self.chat_tool_repo = chat_tool_repo
        self.source_repo = source_repo
        self.prompt_repo = prompt_repo

    async def create_chat(
        self,
        name: str,
        user_id: int,
        source_id: int,
        extra: dict[str, Any] | None = None
    ) -> tuple[ChatEntity, ChatDataEntity | None]:
        """
        创建聊天会话
        
        Args:
            name: 聊天名称
            user_id: 用户ID
            source_id: 源ID
            extra: 额外参数
            
        Returns:
            聊天实体和可能的欢迎消息
        """
        # 获取系统提示词
        prompts = await self.prompt_repo.get_prompts_by_source(source_id)
        system_prompt = next((p for p in prompts if p.type == PromptType.SYSTEM), None)
        system_prompt_content = system_prompt.content if system_prompt else ""

        # 获取源
        source = await self.source_repo.get_source(source_id)

        # 创建聊天
        chat = ChatEntity(
            name=name,
            user_id=user_id,
            source_id=source_id,
            system_prompt=system_prompt_content,
            extra=extra
        )
        chat = await self.chat_repo.create_chat(chat)

        # 如果有欢迎消息，创建它
        welcome_message = None
        if source and source.welcome_text:
            welcome_message = ChatDataEntity(
                chat_id=chat.id,
                content=source.welcome_text,
                role=Role.ASSISTANT
            )
            welcome_message = await self.chat_data_repo.create_chat_data(welcome_message)

        return chat, welcome_message

    async def create_message(
        self,
        chat_id: int,
        content: str,
        role: str = Role.USER,
        content_type: str = ContentType.MSG,
        extra: dict[str, Any] | None = None
    ) -> ChatDataEntity:
        """
        创建聊天消息
        
        Args:
            chat_id: 聊天ID
            content: 消息内容
            role: 角色
            content_type: 内容类型
            extra: 额外参数
            
        Returns:
            聊天数据实体
        """
        chat_data = ChatDataEntity(
            chat_id=chat_id,
            content=content,
            role=role,
            content_type=content_type,
            extra=extra
        )
        return await self.chat_data_repo.create_chat_data(chat_data)

    async def create_tool(
        self,
        chat_id: int,
        tool_id: int,
        parameters: dict[str, Any]
    ) -> ChatToolEntity:
        """
        创建聊天工具
        
        Args:
            chat_id: 聊天ID
            tool_id: 工具ID
            parameters: 参数
            
        Returns:
            聊天工具实体
        """
        chat_tool = ChatToolEntity(
            chat_id=chat_id,
            tool_id=tool_id,
            parameters=parameters
        )
        return await self.chat_tool_repo.create_chat_tool(chat_tool)

    async def get_messages(self, chat_id_str: str) -> list[ChatDataEntity]:
        """
        获取聊天消息列表
        
        Args:
            chat_id_str: 聊天ID字符串
            
        Returns:
            聊天消息列表
        """
        chat = await self.chat_repo.get_chat_by_chat_id(chat_id_str)
        if not chat:
            return []

        return await self.chat_data_repo.get_chat_data(chat.id)

    async def get_chat_with_messages(self, chat_id: int) -> tuple[ChatEntity | None, list[ChatDataEntity]]:
        """
        获取聊天及其消息
        
        Args:
            chat_id: 聊天ID
            
        Returns:
            聊天实体和消息列表
        """
        chat = await self.chat_repo.get_chat(chat_id)
        if not chat:
            return None, []

        messages = await self.chat_data_repo.get_chat_data(chat_id)
        return chat, messages

    async def get_chat_by_chat_id(self, chat_id: str) -> ChatEntity | None:
        """
        通过chat_id获取聊天
        
        Args:
            chat_id: 聊天ID字符串
            
        Returns:
            聊天实体
        """
        return await self.chat_repo.get_chat_by_chat_id(chat_id)
