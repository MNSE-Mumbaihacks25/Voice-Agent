import logging
import json
from websockets.asyncio.client import connect
from app.core.config import settings
import asyncio

logger = logging.getLogger(__name__)

class DeepgramService:
    def __init__(self):
        self.api_key = settings.DEEPGRAM_API_KEY

    async def start_transcription(self, websocket_client, language="en"):
        """
        Manages the connection between the client WebSocket and Deepgram using raw websockets.
        """
        extra_headers = {
            "Authorization": f"Token {self.api_key}"
        }
        
        # Dynamic Model Selection
        # Using Nova-3 as requested.
        model = "nova-3"
        if language == "mr":
            model = "whisper-medium"
        
        # Using channels=1 (Downmix) for robust diarization
        url = f"wss://api.deepgram.com/v1/listen?model={model}&language={language}&smart_format=true&channels=1&interim_results=true&utterance_end_ms=1500&vad_events=true&diarize=true"

        print(f"Connecting to Deepgram: {url}")
        try:
            # Increase timeout and disable ping_interval to avoid handshake timeouts
            async with connect(url, additional_headers=extra_headers, ping_interval=None, open_timeout=20) as dg_socket:
                print("Connected to Deepgram WebSocket")
                
                async def sender():
                    """Forwards audio from client to Deepgram"""
                    print("Starting sender task")
                    try:
                        while True:
                            data = await websocket_client.receive_bytes()
                            print(f"Forwarding {len(data)} bytes to Deepgram")
                            await dg_socket.send(data)
                    except Exception as e:
                        logger.info(f"Sender closed: {e}")
                        print(f"Sender closed: {e}")

                async def receiver():
                    """Forwards transcripts from Deepgram to client"""
                    print("Starting receiver task")
                    try:
                        async for msg in dg_socket:
                            # print(f"Received message from Deepgram: {msg[:100]}")
                            try:
                                res = json.loads(msg)
                            except json.JSONDecodeError:
                                print(f"Failed to decode JSON: {msg}")
                                continue

                            if not isinstance(res, dict):
                                # print(f"Unexpected response type: {type(res)} - {res}")
                                continue
                            
                            # Handle Transcript
                            if "channel" in res:
                                channel_data = res["channel"]
                                channels = []
                                
                                if isinstance(channel_data, list):
                                    channels = channel_data
                                else:
                                    channels = [channel_data]
                                
                                for channel in channels:
                                    if isinstance(channel, dict) and "alternatives" in channel:
                                        alternatives = channel["alternatives"]
                                        if alternatives and isinstance(alternatives, list):
                                            alt = alternatives[0]
                                            transcript = alt.get("transcript")
                                            
                                            # Extract speaker if available
                                            speaker = None
                                            words = alt.get("words", [])
                                            if words and len(words) > 0:
                                                # Take the speaker of the first word as the speaker for this segment
                                                speaker = words[0].get("speaker")
                                                # Debug logging for diarization
                                                print(f"Diarization Debug: Extracted Speaker={speaker}, Words List Length={len(words)}")
                                            else:
                                                print(f"Diarization Debug: No words found. Transcript: '{transcript}'")
                                                
                                            if transcript:
                                                print(f"Transcript: {transcript} (Speaker: {speaker})")
                                                await websocket_client.send_text(json.dumps({
                                                    "type": "transcript",
                                                    "data": transcript,
                                                    "speaker": speaker,
                                                    "is_final": res.get("is_final", False)
                                                }))
                    except Exception as e:
                        logger.info(f"Receiver closed: {e}")
                        print(f"Receiver closed: {e}")

                # Run both tasks
                await asyncio.gather(sender(), receiver())

        except Exception as e:
            logger.error(f"Deepgram Connection Error: {e}")
            print(f"Deepgram Connection Error: {e}")
            # Don't raise, just log/return to allow cleanup
