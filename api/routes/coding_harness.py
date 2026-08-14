
import logging

from fastapi import APIRouter, status, HTTPException
from fastapi.sse import EventSourceResponse

from services.chat_session import process_user_request, process_user_request_streaming
from api.models.chat import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/request_agent")
async def request_to_agent(request: ChatRequest):
    try:
        result = await process_user_request(
            user_query=request.user_query,
            session_id=request.session_id
        )
        return ChatResponse(
            session_id=request.session_id,
            ai_response=result
        )
    except Exception as e:
        logger.error("Error while processing request", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing user request"
        )


@router.post("/request_agent/stream", response_class=EventSourceResponse)
async def request_to_agent(request: ChatRequest):
    try:
        async for chunk in process_user_request_streaming(
            user_query=request.user_query,
            session_id=request.session_id
        ):
            print(chunk)
            yield chunk
        
    except Exception as e:
        logger.error("Error while processing request", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing user request"
        )