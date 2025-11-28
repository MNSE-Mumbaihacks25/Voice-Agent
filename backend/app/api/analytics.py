from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.analytics_service import AnalyticsService

router = APIRouter()

class ReportRequest(BaseModel):
    session_id: str

@router.post("/end-call")
async def end_call(request: ReportRequest):
    service = AnalyticsService()
    try:
        report = await service.generate_report(request.session_id)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
