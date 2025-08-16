from enum import Enum


class SourceType(int, Enum):
    """源类型枚举"""
    CHAT = 1  # 聊天类型
    TOOL = 2  # 工具类型

class PromptType(str, Enum):
    """提示词类型枚举"""
    SYSTEM = "system"   # 系统提示词
    USER = "user"       # 用户提示词
    ASSISTANT = "assistant"  # 助手提示词

class Role(str, Enum):
    """角色枚举"""
    USER = "user"           # 用户
    ASSISTANT = "assistant"  # 助手
    SYSTEM = "system"       # 系统
    TOOL = "tool"           # 工具

class ContentType(str, Enum):
    """内容类型枚举"""
    MSG = "message"        # 普通消息
    REASONING = "reasoning"  # 推理过程
    TOOL = "tool"          # 工具调用
