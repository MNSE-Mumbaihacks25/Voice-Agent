from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_service import RAGService

router = APIRouter()

class AssistRequest(BaseModel):
    session_id: str
    trigger_word: str | None = None

@router.post("/assist")
async def assist_agent(request: AssistRequest):
    print(f"Assist request received for session: {request.session_id} (Trigger: {request.trigger_word})")
    service = RAGService()
    try:
        result = await service.process_assist_request(request.session_id, request.trigger_word)
        print(f"RAG Result: {result}")
        return result
    except Exception as e:
        print(f"RAG Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
