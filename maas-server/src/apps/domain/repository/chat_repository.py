from abc import ABC, abstractmethod

from ..models.chat import (
    ChatDataEntity,
    ChatEntity,
    ChatToolConfig,
    ChatToolEntity,
    PromptEntity,
    SourceEntity,
)


class IChatRepository(ABC):
    """聊天仓储接口"""

    @abstractmethod
    async def create_chat(self, chat: ChatEntity) -> ChatEntity:
        """创建聊天"""
        pass

    @abstractmethod
    async def get_chat(self, chat_id: int) -> ChatEntity | None:
        """根据ID获取聊天"""
        pass

    @abstractmethod
    async def get_chat_by_chat_id(self, chat_id: str) -> ChatEntity | None:
        """根据chat_id获取聊天"""
        pass

    @abstractmethod
    async def get_chats_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[ChatEntity]:
        """获取用户的所有聊天"""
        pass

    @abstractmethod
    async def update_chat(self, chat: ChatEntity) -> ChatEntity:
        """更新聊天"""
        pass

    @abstractmethod
    async def delete_chat(self, chat_id: int) -> bool:
        """删除聊天(软删除)"""
        pass

class IChatDataRepository(ABC):
    """聊天数据仓储接口"""

    @abstractmethod
    async def create_chat_data(self, chat_data: ChatDataEntity) -> ChatDataEntity:
        """创建聊天数据"""
        pass

    @abstractmethod
    async def get_chat_data(self, chat_id: int, skip: int = 0, limit: int = 100) -> list[ChatDataEntity]:
        """获取聊天数据"""
        pass

class IChatToolRepository(ABC):
    """聊天工具仓储接口"""

    @abstractmethod
    async def create_chat_tool(self, chat_tool: ChatToolEntity) -> ChatToolEntity:
        """创建聊天工具"""
        pass

    @abstractmethod
    async def get_chat_tools(self, chat_id: int) -> list[ChatToolEntity]:
        """获取聊天工具"""
        pass

class ISourceRepository(ABC):
    """源仓储接口"""

    @abstractmethod
    async def create_source(self, source: SourceEntity) -> SourceEntity:
        """创建源"""
        pass

    @abstractmethod
    async def get_source(self, source_id: int) -> SourceEntity | None:
        """获取源"""
        pass

    @abstractmethod
    async def get_sources(self, skip: int = 0, limit: int = 100) -> list[SourceEntity]:
        """获取所有源"""
        pass

    @abstractmethod
    async def update_source(self, source: SourceEntity) -> SourceEntity:
        """更新源"""
        pass

    @abstractmethod
    async def delete_source(self, source_id: int) -> bool:
        """删除源"""
        pass

class IPromptRepository(ABC):
    """提示词仓储接口"""

    @abstractmethod
    async def create_prompt(self, prompt: PromptEntity) -> PromptEntity:
        """创建提示词"""
        pass

    @abstractmethod
    async def get_prompt(self, prompt_id: int) -> PromptEntity | None:
        """获取提示词"""
        pass

    @abstractmethod
    async def get_prompts_by_source(self, source_id: int, skip: int = 0, limit: int = 100) -> list[PromptEntity]:
        """获取源的所有提示词"""
        pass

class IToolRepository(ABC):
    """工具仓储接口"""

    @abstractmethod
    async def create_tool(self, tool: ChatToolConfig) -> ChatToolConfig:
        """创建工具"""
        pass

    @abstractmethod
    async def get_tool(self, tool_id: int) -> ChatToolConfig | None:
        """获取工具"""
        pass

    @abstractmethod
    async def get_tools_by_source(self, source_id: int, skip: int = 0, limit: int = 100) -> list[ChatToolConfig]:
        """获取源的所有工具"""
        pass
