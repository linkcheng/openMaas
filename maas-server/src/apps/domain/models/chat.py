import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ...domain.models.enums import ContentType, PromptType, Role, SourceType


@dataclass
class SourceEntity:
    """源实体 - 聊天知识源/工具源头"""
    id: int | None = None
    name: str = ""
    description: str | None = None
    type: int = SourceType.CHAT
    welcome_text: str | None = None
    status: int = 0
    is_deleted: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PromptEntity:
    """提示词实体"""
    id: int | None = None
    name: str = ""
    content: str = ""
    type: PromptType = PromptType.SYSTEM
    source_id: int = 0
    extra: dict[str, Any] | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ChatToolConfig:
    """聊天工具配置实体"""
    id: int | None = None
    name: str = ""
    description: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    source_id: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ChatEntity:
    """聊天实体 - 代表一个聊天会话"""
    id: int | None = None
    name: str = ""
    chat_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    source_id: int = 0
    user_id: int = 0
    system_prompt: str | None = None
    is_deleted: bool = False
    extra: dict[str, Any] | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def get_formatted_system_prompt(self) -> str:
        """获取格式化后的系统提示词"""
        if not self.system_prompt:
            return ""
        if self.extra:
            try:
                return self.system_prompt.format(**self.extra)
            except (KeyError, ValueError):
                return self.system_prompt
        return self.system_prompt

@dataclass
class ChatDataEntity:
    """聊天数据实体 - 代表聊天中的一条消息"""
    id: int | None = None
    chat_id: int = 0
    content: str = ""
    content_type: ContentType = ContentType.MSG
    role: Role = Role.USER
    extra: dict[str, Any] | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ChatToolEntity:
    """聊天工具实体 - 代表聊天关联的一个工具"""
    id: int | None = None
    chat_id: int = 0
    tool_id: int = 0
    parameters: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
