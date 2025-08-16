import uuid
from datetime import datetime

from service.database.mysql_database import Base
from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...domain.models.enums import (
    ContentType,
    PromptType,
    Role,
    SourceType,
)


class Apps(Base):
    """源ORM模型"""
    __tablename__ = "apps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    type: Mapped[int] = mapped_column(Integer, default=SourceType.CHAT, nullable=False)
    welcome_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    prompts: Mapped[list["Prompt"]] = relationship("Prompt", back_populates="source", cascade="all, delete-orphan")
    tools: Mapped[list["Tool"]] = relationship("Tool", back_populates="source", cascade="all, delete-orphan")
    chats: Mapped[list["Chat"]] = relationship("Chat", back_populates="source", cascade="all, delete-orphan")

class Prompt(Base):
    """提示词ORM模型"""
    __tablename__ = "prompt"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[PromptType] = mapped_column(Enum(PromptType), nullable=False)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("source.id", ondelete="CASCADE"), nullable=False)
    extra: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    source: Mapped["Source"] = relationship("Source", back_populates="prompts")

class Tool(Base):
    """工具ORM模型"""
    __tablename__ = "tool"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    parameters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("source.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    source: Mapped["Source"] = relationship("Source", back_populates="tools")
    chat_tools: Mapped[list["ChatTool"]] = relationship("ChatTool", back_populates="tool", cascade="all, delete-orphan")

class Chat(Base):
    """聊天ORM模型"""
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    chat_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False, default=lambda: uuid.uuid4().hex)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("source.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    extra: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    source: Mapped["Source"] = relationship("Source", back_populates="chats")
    chat_data: Mapped[list["ChatData"]] = relationship("ChatData", back_populates="chat", cascade="all, delete-orphan")
    chat_tools: Mapped[list["ChatTool"]] = relationship("ChatTool", back_populates="chat", cascade="all, delete-orphan")

    def get_formatted_system_prompt(self) -> str:
        """获取格式化后的系统提示词"""
        return self.system_prompt.format(**self.extra) if self.extra and self.system_prompt else self.system_prompt

class ChatData(Base):
    """聊天数据ORM模型"""
    __tablename__ = "chat_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(Integer, ForeignKey("mpc_chat.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    content_type: Mapped[ContentType] = mapped_column(Enum(ContentType), default=ContentType.MSG, nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False)
    extra: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    chat: Mapped["Chat"] = relationship("Chat", back_populates="chat_data")

class ChatTool(Base):
    """聊天工具ORM模型"""
    __tablename__ = "chat_tool"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(Integer, ForeignKey("mpc_chat.id", ondelete="CASCADE"), nullable=False)
    tool_id: Mapped[int] = mapped_column(Integer, ForeignKey("tool.id", ondelete="CASCADE"), nullable=False)
    parameters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    chat: Mapped["Chat"] = relationship("Chat", back_populates="chat_tools")
    tool: Mapped["Tool"] = relationship("Tool", back_populates="chat_tools")
