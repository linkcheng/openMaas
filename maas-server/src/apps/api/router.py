from chat.application.chat_service import ChatApplicationService
from chat.application.schemas import (
    Chat,
    ChatCreate,
    ChatData,
    ChatListResponse,
    ChatResponse,
    EnableToolRequest,
    MessageListResponse,
    MessageResponse,
    SendMessageRequest,
    Source,
    SourceCreate,
    SourceListResponse,
    SourceResponse,
    SourceUpdate,
    StreamResponse,
)
from chat.domain.models.chat import SourceEntity
from chat.infrastructure.repositories import SourceRepository
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from infra.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

# 导入配置
from ...config import get_chat_config

# 获取聊天配置
chat_config = get_chat_config()

# 应用服务实例，使用配置
chat_app_service = ChatApplicationService(
    mcp_server_url=chat_config.mcp_server_url,
    model=chat_config.default_model,
    api_key=chat_config.available_models[0].api_key if chat_config.available_models else "your-api-key",
    api_base=chat_config.available_models[0].api_base if chat_config.available_models else "https://api.openai.com/v1"
)

# Source endpoints
@router.post("/sources", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(
    source: SourceCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建源"""
    source_repo = SourceRepository(db)
    source_entity = SourceEntity(
        name=source.name,
        description=source.description,
        type=source.type,
        welcome_text=source.welcome_text,
        status=source.status
    )
    created = await source_repo.create_source(source_entity)
    return SourceResponse(data=Source.from_orm(created))

@router.get("/sources", response_model=SourceListResponse)
async def list_sources(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取源列表"""
    source_repo = SourceRepository(db)
    sources = await source_repo.get_sources(skip, limit)
    return SourceListResponse(
        data=[Source.from_orm(s) for s in sources],
        total=len(sources)
    )

@router.get("/sources/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取源详情"""
    source_repo = SourceRepository(db)
    source = await source_repo.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return SourceResponse(data=Source.from_orm(source))

@router.put("/sources/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: int,
    source: SourceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新源"""
    source_repo = SourceRepository(db)
    source_entity = await source_repo.get_source(source_id)
    if not source_entity:
        raise HTTPException(status_code=404, detail="Source not found")

    # 更新属性
    for key, value in source.dict().items():
        setattr(source_entity, key, value)

    updated = await source_repo.update_source(source_entity)
    return SourceResponse(data=Source.from_orm(updated))

@router.delete("/sources/{source_id}")
async def delete_source(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除源"""
    source_repo = SourceRepository(db)
    result = await source_repo.delete_source(source_id)
    if not result:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"message": "Source deleted successfully"}

# Chat endpoints
@router.post("/chats", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat: ChatCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建聊天"""
    chat_entity, _ = await chat_app_service.create_chat(
        session=db,
        name=chat.name,
        user_id=chat.user_id,
        source_id=chat.source_id,
        extra=chat.extra
    )
    return ChatResponse(data=Chat.from_orm(chat_entity))

@router.get("/users/{user_id}/chats", response_model=ChatListResponse)
async def list_user_chats(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取用户聊天列表"""
    chats = await chat_app_service.list_user_chats(
        session=db,
        user_id=user_id,
        skip=skip,
        limit=limit
    )
    return ChatListResponse(
        data=[Chat.from_orm(c) for c in chats],
        total=len(chats)
    )

@router.get("/chats/{chat_id}/messages", response_model=MessageListResponse)
async def list_chat_messages(
    chat_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取聊天消息列表"""
    messages = await chat_app_service.list_messages(
        session=db,
        chat_id=chat_id
    )
    return MessageListResponse(
        data=[ChatData.from_orm(m) for m in messages],
        total=len(messages)
    )

@router.post("/chat-tools", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def enable_tool(
    request: EnableToolRequest,
    db: AsyncSession = Depends(get_db)
):
    """为聊天添加工具"""
    chat_tool = await chat_app_service.create_chat_tool(
        session=db,
        chat_id=request.chat_id,
        tool_id=request.tool_id,
        parameters=request.parameters
    )
    if not chat_tool:
        raise HTTPException(status_code=404, detail="Chat not found")

    # 这里返回的是ChatTool，但为了兼容前端，转换为MessageResponse
    # 实际项目中应根据需求调整
    return MessageResponse(
        data=ChatData(
            id=chat_tool.id,
            chat_id=chat_tool.chat_id,
            content=f"工具已启用: {chat_tool.tool_id}",
            role="system",
            content_type="tool",
            created_at=chat_tool.created_at
        )
    )

@router.post("/chat-data")
async def send_message(
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """发送消息，返回流式响应"""

    # 创建一个异步生成器，将应用服务的响应转换为适合流式响应的格式
    async def response_generator():
        async for response in chat_app_service.send_message(
            session=db,
            chat_id=request.chat_id,
            message_content=request.content
        ):
            # 将应用服务响应转换为JSON字符串
            yield StreamResponse(
                content=response["content"],
                content_type=response["content_type"]
            ).json() + "\n"

    # 返回流式响应
    return StreamingResponse(
        response_generator(),
        media_type="application/x-ndjson"
    )
