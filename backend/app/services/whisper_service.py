import logging
import json
import asyncio
import tempfile
import wave
import struct
import numpy as np
from pathlib import Path
from pywhispercpp.model import Model
from scipy.spatial.distance import euclidean
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize Sentiment Analyzer (optional)
try:
    import nltk
    # Download VADER lexicon if not already present
    try:
        nltk.data.find('sentiment/vader_lexicon')
    except LookupError:
        print("Downloading VADER lexicon...")
        nltk.download('vader_lexicon', quiet=True)
    
    from nltk.sentiment import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()
    print("✓ VADER sentiment analyzer initialized")
except Exception as e:
    sia = None
    logger.warning(f"VADER sentiment analyzer not available: {e}")

# Profanity detection (optional)
profanity = None
try:
    from better_profanity import profanity as profanity_module
    profanity = profanity_module
    profanity.load_censor_words()
except ImportError:
    logger.warning("Profanity detector not available")


def check_profanity(text):
    """Detect profanity. Returns (original text, flag)."""
    if not profanity:
        return text, False
    return text, profanity.contains_profanity(text)


def analyze_sentiment(text):
    """Analyze sentiment and detect emotional tone."""
    if not sia:
        return "Neutral"
    
    scores = sia.polarity_scores(text)
    compound = scores["compound"]
    
    if scores["pos"] > 0.3 and compound < 0:
        return "Sarcasm"
    elif compound >= 0.05:
        return "Positive"
    elif compound <= -0.6:
        return "Anger"
    elif compound <= -0.05:
        return "Negative"
    return "Neutral"


def calculate_fingerprint(audio_chunk):
    """
    Calculate energy and frequency fingerprint from audio chunk.
    
    Args:
        audio_chunk: bytes or bytearray of 16-bit PCM audio
        
    Returns:
        dict with 'energy' and 'frequency' keys
    """
    try:
        # Convert bytes to int16 array
        audio_array = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32)
        
        if len(audio_array) == 0:
            return {"energy": 0.0, "frequency": 0.0}
        
        # Calculate energy (RMS)
        energy = np.sqrt(np.mean(audio_array ** 2))
        
        # Calculate frequency (simple approach: zero crossing rate)
        zero_crossings = np.sum(np.abs(np.diff(np.sign(audio_array)))) / 2
        frequency = zero_crossings / len(audio_array)
        
        return {"energy": float(energy), "frequency": float(frequency)}
    except Exception as e:
        logger.error(f"Error calculating fingerprint: {e}")
        return {"energy": 0.0, "frequency": 0.0}


class DiarizationManager:
    """Lightweight speaker identification based on audio fingerprints."""
    
    def __init__(self, history_size=20, similarity_threshold=0.3):
        self.speaker_profiles = []  # List of (fingerprint, speaker_id)
        self.speaker_history = defaultdict(list)
        self.next_speaker_id = 0
        self.history_size = history_size
        self.similarity_threshold = similarity_threshold
    
    def get_speaker_for_fingerprint(self, fingerprint):
        """Match fingerprint to existing speaker or create new one."""
        if not fingerprint or not all(isinstance(x, (int, float)) for x in fingerprint.values()):
            return {"id": 0, "name": "Speaker"}
        
        # Convert to vector for distance calculation
        vector = [fingerprint["energy"], fingerprint["frequency"]]
        
        best_match = None
        min_distance = float("inf")
        
        # Check against existing speakers
        for speaker_profile in self.speaker_profiles:
            profile_vector = [speaker_profile[0]["energy"], speaker_profile[0]["frequency"]]
            distance = euclidean(vector, profile_vector)
            
            if distance < min_distance:
                min_distance = distance
                best_match = speaker_profile[1]
        
        # If close match found, use that speaker
        if best_match is not None and min_distance < self.similarity_threshold:
            speaker_id = best_match
            
            # Update profile with history
            for profile in self.speaker_profiles:
                if profile[1] == speaker_id:
                    self.speaker_history[speaker_id].append(fingerprint)
                    if len(self.speaker_history[speaker_id]) > self.history_size:
                        self.speaker_history[speaker_id].pop(0)
                    
                    # Update with average
                    if self.speaker_history[speaker_id]:
                        avg_energy = np.mean([fp["energy"] for fp in self.speaker_history[speaker_id]])
                        avg_freq = np.mean([fp["frequency"] for fp in self.speaker_history[speaker_id]])
                        profile[0]["energy"] = float(avg_energy)
                        profile[0]["frequency"] = float(avg_freq)
                    break
        else:
            # Create new speaker
            speaker_id = self.next_speaker_id
            self.next_speaker_id += 1
            self.speaker_profiles.append((fingerprint.copy(), speaker_id))
            self.speaker_history[speaker_id].append(fingerprint)
        
        return {"id": speaker_id, "name": f"Speaker {speaker_id + 1}"}


class WhisperService:
    """
    Local Whisper transcription service using pywhispercpp.
    Includes audio fingerprinting, speaker identification, sentiment analysis.
    """
    def __init__(self, model_name: str = "base.en", n_threads: int = 4, chunk_size: int = 8000):
        """
        Initialize Whisper model.
        
        Args:
            model_name: Model size ('tiny.en', 'base.en', 'small.en', 'medium.en', 'large-v3')
            n_threads: Number of CPU threads to use
            chunk_size: Audio chunk size in bytes (8000 = 4000 samples at 16-bit = 250ms at 16kHz)
        """
        self.model_name = model_name
        self.n_threads = n_threads
        self.chunk_size = chunk_size
        self.model = None
        self.diarization_manager = DiarizationManager()
        self._load_model()

    def _load_model(self):
        """Load the Whisper model."""
        try:
            print(f"Loading Whisper model: {self.model_name}")
            self.model = Model(self.model_name, n_threads=self.n_threads)
            print(f"✓ Whisper model loaded successfully: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise

    async def start_transcription(self, websocket_client, language: str = "en"):
        """
        Manages transcription of audio from WebSocket client using local Whisper.
        
        Args:
            websocket_client: WebSocket client wrapper
            language: Language code (e.g., 'en', 'hi', 'mr')
        """
        print(f"Starting Whisper transcription (model: {self.model_name}, language: {language})")
        
        audio_buffer = bytearray()
        transcription_interval = 16000  # 1 second at 16kHz (32KB at 16-bit) - much more responsive
        silence_threshold = 500  # Energy threshold for silence detection
        last_transcribed_pos = 0
        consecutive_silence_chunks = 0
        silence_chunk_limit = 5  # Transcribe after 5 consecutive silent chunks (~1.25 seconds)

        try:
            async def receiver():
                """Receive audio chunks from client and transcribe periodically"""
                nonlocal last_transcribed_pos, consecutive_silence_chunks
                
                print("Starting receiver task for Whisper")
                
                try:
                    while True:
                        # Receive audio data from client
                        data = await websocket_client.receive_bytes()
                        
                        if len(data) == 0:
                            break
                        
                        audio_buffer.extend(data)
                        print(f"Received audio chunk: {len(data)} bytes (total buffer: {len(audio_buffer)} bytes)")
                        
                        # Check for silence in recent chunk
                        fingerprint = calculate_fingerprint(data)
                        is_silent = fingerprint["energy"] < silence_threshold
                        
                        if is_silent:
                            consecutive_silence_chunks += 1
                        else:
                            consecutive_silence_chunks = 0
                        
                        # Transcribe on silence (end of speech) or after time interval
                        should_transcribe = (
                            (consecutive_silence_chunks >= silence_chunk_limit and len(audio_buffer) - last_transcribed_pos >= 2000) or
                            (len(audio_buffer) - last_transcribed_pos >= transcription_interval)
                        )
                        
                        if should_transcribe:
                            await _transcribe_buffer(audio_buffer, last_transcribed_pos, websocket_client)
                            last_transcribed_pos = len(audio_buffer)
                            consecutive_silence_chunks = 0
                            
                except Exception as e:
                    logger.info(f"Receiver closed: {e}")
                    print(f"Receiver closed: {e}")
                    
                    # Final transcription of remaining audio
                    if len(audio_buffer) > last_transcribed_pos:
                        print("Performing final transcription of remaining audio")
                        await _transcribe_buffer(audio_buffer, last_transcribed_pos, websocket_client, is_final=True)

            async def _transcribe_buffer(buffer, start_pos, ws_client, is_final=False):
                """Transcribe audio buffer segment"""
                if len(buffer) <= start_pos:
                    return
                
                segment = buffer[start_pos:]
                print(f"Transcribing segment ({len(segment)} bytes, final={is_final})")
                
                try:
                    # Calculate fingerprint from segment
                    fingerprint = calculate_fingerprint(segment)
                    speaker = self.diarization_manager.get_speaker_for_fingerprint(fingerprint)
                    
                    # Save segment to temporary WAV file
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                        tmp_path = tmp_file.name
                        
                        # Write as WAV format (16-bit mono, 16kHz)
                        with wave.open(tmp_path, "wb") as wav_file:
                            wav_file.setnchannels(1)      # Mono
                            wav_file.setsampwidth(2)       # 16-bit
                            wav_file.setframerate(16000)   # 16kHz
                            wav_file.writeframes(bytes(segment))
                    
                    # Transcribe using the temporary file path
                    print(f"Transcribing from file: {tmp_path}")
                    segments = self.model.transcribe(tmp_path)
                    
                    for seg in segments:
                        text = seg.text.strip()
                        if text:
                            print(f"Transcribed: {text}")
                            
                            # Analyze sentiment and profanity
                            _, has_profanity = check_profanity(text)
                            sentiment = analyze_sentiment(text)
                            
                            try:
                                await ws_client.send_text(json.dumps({
                                    "type": "transcript",
                                    "data": text,
                                    "speaker": speaker["id"],
                                    "speaker_name": speaker["name"],
                                    "is_final": is_final,
                                    "sentiment": sentiment,
                                    "profanity_detected": has_profanity,
                                    "timestamp": datetime.utcnow().isoformat() + "Z"
                                }))
                            except Exception as send_err:
                                logger.warning(f"Failed to send transcription: {send_err}")
                                print(f"Failed to send transcription: {send_err}")
                    
                    # Clean up temporary file
                    Path(tmp_path).unlink(missing_ok=True)
                    
                except Exception as e:
                    logger.error(f"Transcription error: {e}")
                    print(f"Transcription error: {e}")

            # Run receiver
            await receiver()

        except Exception as e:
            logger.error(f"Whisper Service Error: {e}")
            print(f"Whisper Service Error: {e}")
