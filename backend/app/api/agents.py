from fastapi import APIRouter, HTTPException
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("/")
async def get_agents():
    service = AgentService()
    agents = await service.get_all_agents()
    return agents

@router.get("/{agent_id}/leads")
async def get_agent_leads(agent_id: str):
    service = AgentService()
    leads = await service.get_leads_by_agent(agent_id)
    return leads
