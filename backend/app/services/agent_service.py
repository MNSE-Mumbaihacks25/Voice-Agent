from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class AgentService:
    def __init__(self):
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    async def get_all_agents(self):
        try:
            response = self.supabase.table("agents").select("agent_id, name").execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching agents: {e}")
            return []

    async def get_leads_by_agent(self, agent_id: str):
        try:
            # Fetch leads from ai_dispatch_logs where assigned_agent matches agent_id
            # Note: The schema says 'assigned_agent' in ai_dispatch_logs is text.
            # Assuming it stores the agent's name or ID. Based on user request "mapped wth that agent",
            # and typical foreign key relationships, we should check if it matches agent_id or name.
            # The schema doesn't explicitly link them via FK in ai_dispatch_logs, but let's assume agent_id for now 
            # or try to match on name if that fails. 
            # However, usually 'assigned_agent' would be the ID.
            
            # Let's try to filter by assigned_agent = agent_id first.
            response = self.supabase.table("ai_dispatch_logs")\
                .select("*")\
                .eq("assigned_agent", agent_id)\
                .execute()
            
            return response.data
        except Exception as e:
            logger.error(f"Error fetching leads for agent {agent_id}: {e}")
            return []
