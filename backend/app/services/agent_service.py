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
            # 1. Fetch Agent Name from agents table
            agent_response = self.supabase.table("agents")\
                .select("name")\
                .eq("agent_id", agent_id)\
                .execute()
                
            if not agent_response.data:
                logger.error(f"Agent not found: {agent_id}")
                return []
                
            agent_name = agent_response.data[0].get("name")
            
            # 2. Fetch leads from ai_dispatch_logs using assigned_agent (which stores Name)
            response = self.supabase.table("ai_dispatch_logs")\
                .select("*")\
                .eq("assigned_agent", agent_name)\
                .execute()
            
            return response.data
        except Exception as e:
            logger.error(f"Error fetching leads for agent {agent_id}: {e}")
            return []

    async def update_chat_history(self, lead_id: str, history_entry: dict, lead_name: str = None):
        try:
            # 1. Determine Lead Name
            if not lead_name:
                # Get lead_name from ai_dispatch_logs using lead_id
                log_response = self.supabase.table("ai_dispatch_logs")\
                    .select("lead_name")\
                    .eq("id", lead_id)\
                    .execute()
                
                if not log_response.data:
                    logger.error(f"Lead not found in dispatch logs: {lead_id}")
                    # If we don't have a name, we can't check investors table.
                    # But we can try fallback to logs if we have ID.
                else:
                    lead_name = log_response.data[0].get("lead_name")
            
            # 2. Try to find investor by name in investors table
            investor_found = False
            if lead_name:
                investor_response = self.supabase.table("investors")\
                    .select("investor_id, chat_history")\
                    .eq("name", lead_name)\
                    .execute()
                    
                if investor_response.data:
                    # Found in investors table, update there
                    investor = investor_response.data[0]
                    investor_id = investor.get("investor_id")
                    current_history = investor.get("chat_history", []) or []
                    
                    # Append new history
                    current_history.append(history_entry)
                    
                    # Update investors table
                    self.supabase.table("investors")\
                        .update({"chat_history": current_history})\
                        .eq("investor_id", investor_id)\
                        .execute()
                    logger.info(f"Updated chat history for investor {lead_name} in investors table.")
                    investor_found = True
                    return True
            
            if not investor_found:
                # Fallback: Update ai_dispatch_logs
                logger.warning(f"Investor not found for {lead_name}. Fallback to ai_dispatch_logs.")
                
                if not lead_id:
                     logger.error("Cannot fallback to ai_dispatch_logs without lead_id.")
                     return False

                # Fetch current history from logs to append
                log_hist_res = self.supabase.table("ai_dispatch_logs")\
                    .select("chat_history")\
                    .eq("id", lead_id)\
                    .execute()
                    
                current_history = []
                if log_hist_res.data:
                    current_history = log_hist_res.data[0].get("chat_history", []) or []
                
                current_history.append(history_entry)
                
                self.supabase.table("ai_dispatch_logs")\
                    .update({"chat_history": current_history})\
                    .eq("id", lead_id)\
                    .execute()
                logger.info(f"Updated chat history for lead {lead_id} in ai_dispatch_logs (Fallback).")
                return True
                
        except Exception as e:
            logger.error(f"Error updating chat history for lead {lead_id}: {e}")
            return False
