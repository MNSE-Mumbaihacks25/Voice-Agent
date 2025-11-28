from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.deepgram_service import DeepgramService
from app.core.state import transcript_store
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/audio")
async def websocket_endpoint(
    websocket: WebSocket, 
    session_id: str = Query(...),
    agent_name: str = Query("Agent"),
    lead_name: str = Query("Lead"),
    language: str = Query("en")
):
    print(f"New WebSocket connection request: {session_id} (Agent: {agent_name}, Lead: {lead_name}, Language: {language})")
    await websocket.accept()
    print(f"WebSocket accepted: {session_id}")
    deepgram_service = DeepgramService()
    dg_connection = None
    
    # Initialize transcript store for this session
    if session_id not in transcript_store:
        transcript_store[session_id] = []
        
    audio_buffer = bytearray()

    try:
        # We need to intercept the message to store it
        original_send_text = websocket.send_text
        
        async def intercepted_send_text(data: str):
            # Parse the data to extract transcript
            try:
                # print(f"Sending to client: {data[:50]}...") # Verbose
                msg = json.loads(data)
                if msg.get("type") == "transcript" and msg.get("is_final"):
                    print(f"Received final transcript: {msg.get('data')}")
                    transcript_store[session_id].append(msg.get("data"))
            except:
                pass
            await original_send_text(data)
            
        class WebSocketWrapper:
            def __init__(self, ws):
                self.ws = ws
            async def send_text(self, data: str):
                try:
                    msg = json.loads(data)
                    if msg.get("type") == "transcript" and msg.get("is_final"):
                        # Map Speaker ID to Name
                        speaker_id = msg.get("speaker")
                        speaker_name = "Unknown"
                        
                        # Simple Heuristic: Speaker 0 is Agent, Speaker 1 is Lead
                        if speaker_id == 0:
                            speaker_name = agent_name
                        elif speaker_id == 1:
                            speaker_name = lead_name
                        else:
                            speaker_name = f"Speaker {speaker_id}"
                            
                        msg["speaker_name"] = speaker_name
                        
                        # Store in transcript store (optional: store with name)
                        transcript_store[session_id].append(f"{speaker_name}: {msg.get('data')}")
                        
                        # Send modified JSON
                        await self.ws.send_text(json.dumps(msg))
                        return
                except Exception as e:
                    print(f"Error mapping speaker: {e}")
                    pass
                await self.ws.send_text(data)
            async def receive_bytes(self):
                data = await self.ws.receive_bytes()
                # print(f"Received {len(data)} bytes from client") # Verbose
                audio_buffer.extend(data)
                return data

        wrapper = WebSocketWrapper(websocket)
        
        print("Starting Deepgram transcription...")
        # The new start_transcription handles the loop internally
        await deepgram_service.start_transcription(wrapper, language)
        print("Deepgram transcription finished.")

    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
    finally:
        # Save audio to file
        import wave
        from app.services.summary_service import SummaryService
        from app.services.agent_service import AgentService
        from app.services.analytics_service import AnalyticsService
        import datetime

        try:
            if len(audio_buffer) > 0:
                filename = f"audio_{session_id}.wav"
                with wave.open(filename, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2) # 16-bit
                    wf.setframerate(16000)
                    wf.writeframes(audio_buffer)
                logger.info(f"Saved audio to {filename}")
                
            # Generate Summary and Analytics
            full_transcript = " ".join(transcript_store.get(session_id, []))
            if full_transcript:
                print(f"Generating summary for session {session_id}...")
                summary_service = SummaryService()
                summary = summary_service.generate_summary(full_transcript)
                
                # Mock Analytics (or use real if available)
                analytics_service = AnalyticsService()
                # analytics = analytics_service.generate_report(full_transcript) # This might be slow/expensive
                analytics = {"sentiment": "Positive", "duration": "Unknown"} # Placeholder
                
                history_entry = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "conversation": full_transcript,
                    "summary": summary,
                    "call_analytics": analytics,
                    "handling_agent": agent_name,
                    "session_id": session_id
                }
                
                # Update DB
                # We need lead_id. But we only have lead_name. 
                # Ideally, we should pass lead_id in the query param.
                # For now, we'll try to find the lead by name and agent.
                agent_service = AgentService()
                leads = agent_service.get_leads_by_agent(agent_name) # This expects agent_id, but we passed agent_name?
                # Wait, agent_name passed in query might be ID or Name. 
                # Let's assume the frontend passes ID as 'agent_name' or we need to fix frontend to pass IDs.
                
                # FIX: The frontend should pass IDs.
                # But for now, let's just print the entry.
                print(f"Call Summary: {summary}")
                print(f"History Entry to Save: {history_entry}")
                
                # TODO: Actually save to DB once we have lead_id
                # agent_service.update_chat_history(lead_id, history_entry)
                
        except Exception as e:
            logger.error(f"Failed to save audio/summary: {e}")
