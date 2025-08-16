from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from ..domain.models.enums import ContentType, PromptType, Role, SourceType


# 基础接口响应模型
class ResponseBase(BaseModel):
    """API响应基类"""
    code: int = Field(default=0, description="状态码，0表示成功")
    msg: str = Field(default="success", description="响应消息")

# Source模型
class SourceBase(BaseModel):
    """源基础模型"""
    name: str = Field(..., description="源名称")
    description: str | None = Field(None, description="源描述")
    type: int = Field(default=SourceType.CHAT, description="源类型")
    welcome_text: str | None = Field(None, description="欢迎文本")
    status: int = Field(default=0, description="状态")

class SourceCreate(SourceBase):
    """源创建模型"""
    pass

class SourceUpdate(SourceBase):
    """源更新模型"""
    pass

class Source(SourceBase):
    """源响应模型"""
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Prompt模型
class PromptBase(BaseModel):
    """提示词基础模型"""
    name: str = Field(..., description="提示词名称")
    content: str = Field(..., description="提示词内容")
    type: PromptType = Field(..., description="提示词类型")
    source_id: int = Field(..., description="关联的源ID")
    extra: dict[str, Any] | None = Field(None, description="额外参数")

class PromptCreate(PromptBase):
    """提示词创建模型"""
    pass

class PromptUpdate(PromptBase):
    """提示词更新模型"""
    pass

class Prompt(PromptBase):
    """提示词响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Tool模型
class ToolBase(BaseModel):
    """工具基础模型"""
    name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")
    parameters: dict[str, Any] = Field(default_factory=dict, description="工具参数")
    source_id: int = Field(..., description="关联的源ID")

class ToolCreate(ToolBase):
    """工具创建模型"""
    pass

class ToolUpdate(ToolBase):
    """工具更新模型"""
    pass

class Tool(ToolBase):
    """工具响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Chat模型
class ChatBase(BaseModel):
    """聊天基础模型"""
    name: str = Field(..., description="聊天名称")
    user_id: int = Field(..., description="用户ID")
    source_id: int = Field(..., description="源ID")
    system_prompt: str | None = Field(None, description="系统提示词")
    extra: dict[str, Any] | None = Field(None, description="额外参数")

class ChatCreate(ChatBase):
    """聊天创建模型"""
    pass

class ChatUpdate(ChatBase):
    """聊天更新模型"""
    pass

class Chat(ChatBase):
    """聊天响应模型"""
    id: int
    chat_id: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# ChatData模型
class ChatDataBase(BaseModel):
    """聊天数据基础模型"""
    chat_id: int = Field(..., description="聊天ID")
    content: str = Field(..., description="内容")
    content_type: ContentType = Field(default=ContentType.MSG, description="内容类型")
    role: Role = Field(..., description="角色")
    extra: dict[str, Any] | None = Field(None, description="额外参数")

class ChatDataCreate(ChatDataBase):
    """聊天数据创建模型"""
    pass

class ChatData(ChatDataBase):
    """聊天数据响应模型"""
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# ChatTool模型
class ChatToolBase(BaseModel):
    """聊天工具基础模型"""
    chat_id: int = Field(..., description="聊天ID")
    tool_id: int = Field(..., description="工具ID")
    parameters: dict[str, Any] = Field(default_factory=dict, description="参数")

class ChatToolCreate(ChatToolBase):
    """聊天工具创建模型"""
    pass

class ChatTool(ChatToolBase):
    """聊天工具响应模型"""
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# API请求模型
class SendMessageRequest(BaseModel):
    """发送消息请求"""
    chat_id: str = Field(..., description="聊天ID")
    content: str = Field(..., description="消息内容")

class EnableToolRequest(BaseModel):
    """启用工具请求"""
    chat_id: str = Field(..., description="聊天ID")
    tool_id: int = Field(..., description="工具ID")
    parameters: dict[str, Any] = Field(default_factory=dict, description="参数")

# API响应模型
class MessageResponse(ResponseBase):
    """消息响应"""
    data: ChatData

class ChatResponse(ResponseBase):
    """聊天响应"""
    data: Chat

class ChatListResponse(ResponseBase):
    """聊天列表响应"""
    data: list[Chat]
    total: int

class MessageListResponse(ResponseBase):
    """消息列表响应"""
    data: list[ChatData]
    total: int

class SourceResponse(ResponseBase):
    """源响应"""
    data: Source

class SourceListResponse(ResponseBase):
    """源列表响应"""
    data: list[Source]
    total: int

class StreamResponse(BaseModel):
    """流式响应"""
    content: str
    content_type: ContentType
