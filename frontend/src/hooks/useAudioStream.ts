import { useState, useRef, useCallback, useEffect } from 'react';


export const useAudioStream = () => {
    const [isConnected, setIsConnected] = useState(false);
    const [transcript, setTranscript] = useState<{ text: string, speaker: number, speaker_name?: string, sentiment?: string, profanity?: boolean }[]>([]);
    const [sessionId, setSessionId] = useState<string>("");
    const socketRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        // Generate a random session ID on mount
        setSessionId(Math.random().toString(36).substring(7));
    }, []);

    const startRecording = useCallback(async (agentName: string, leadName: string, language: string = "en") => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 16000 // Try to request 16kHz
                }
            });

            const audioContext = new AudioContext();
            // Fallback: if browser ignores sampleRate, we need to handle it
            console.log(`AudioContext sample rate: ${audioContext.sampleRate}`);

            const source = audioContext.createMediaStreamSource(stream);

            await audioContext.audioWorklet.addModule('/audio-processor.js');
            const workletNode = new AudioWorkletNode(audioContext, 'audio-processor', {
                processorOptions: {
                    sampleRate: audioContext.sampleRate
                }
            });

            source.connect(workletNode);
            workletNode.connect(audioContext.destination); // Necessary to keep the processor alive? Usually yes for some browsers, or just don't connect to destination to avoid feedback.
            // Actually, connecting to destination will play the audio back to the user, which causes echo.
            // We should NOT connect to destination. But we need to keep the graph alive.
            // In many browsers, just connecting source -> worklet is enough if the worklet returns true.

            // Connect to WebSocket
            const ws = new WebSocket(`ws://localhost:8000/ws/audio?session_id=${sessionId}&agent_name=${encodeURIComponent(agentName)}&lead_name=${encodeURIComponent(leadName)}&language=${language}&engine=whisper`);

            ws.onopen = () => {
                setIsConnected(true);
                console.log("Connected to WebSocket");
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'transcript') {
                    setTranscript(prev => [...prev, {
                        text: data.data,
                        speaker: data.speaker,
                        speaker_name: data.speaker_name,
                        sentiment: data.sentiment,
                        profanity: data.profanity_detected
                    }]);
                }
            };

            ws.onclose = () => {
                setIsConnected(false);
            };

            socketRef.current = ws;

            workletNode.port.onmessage = (event) => {
                if (socketRef.current?.readyState === WebSocket.OPEN) {
                    socketRef.current.send(event.data);
                }
            };

            // Store references for cleanup
            // We need to store audioContext and workletNode to close them later
            // But the current ref is for MediaRecorder. We can repurpose or add new refs.
            // For minimal changes, let's attach them to the socketRef or a new ref?
            // Let's add a new ref for the context.
            (socketRef as any).audioContext = audioContext;
            (socketRef as any).stream = stream;
            (socketRef as any).workletNode = workletNode;

            console.log("AudioContext started");

        } catch (error) {
            console.error("Error starting recording:", error);
        }
    }, [sessionId]);

    const streamAudioFile = useCallback(async (file: File, agentName: string, leadName: string, language: string = "en") => {
        try {
            // Connect to WebSocket with names and language
            const ws = new WebSocket(`ws://localhost:8000/ws/audio?session_id=${sessionId}&agent_name=${encodeURIComponent(agentName)}&lead_name=${encodeURIComponent(leadName)}&language=${language}&engine=whisper`);
            socketRef.current = ws;

            ws.onopen = async () => {
                setIsConnected(true);
                console.log("Connected to WebSocket for file streaming");

                try {
                    const arrayBuffer = await file.arrayBuffer();

                    // Decode audio using OfflineAudioContext to ensure 16kHz sample rate
                    // We use a temporary context to decode the original file first to get its duration/properties
                    const tempCtx = new AudioContext();
                    const audioBuffer = await tempCtx.decodeAudioData(arrayBuffer);

                    // Now resample to 16kHz using OfflineAudioContext
                    const targetSampleRate = 16000;
                    const offlineCtx = new OfflineAudioContext(1, audioBuffer.duration * targetSampleRate, targetSampleRate);
                    const source = offlineCtx.createBufferSource();
                    source.buffer = audioBuffer;
                    source.connect(offlineCtx.destination);
                    source.start();

                    const renderedBuffer = await offlineCtx.startRendering();
                    const channelData = renderedBuffer.getChannelData(0); // Mono

                    // Convert to Int16 PCM
                    const int16Data = new Int16Array(channelData.length);
                    for (let i = 0; i < channelData.length; i++) {
                        let s = Math.max(-1, Math.min(1, channelData[i]));
                        int16Data[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
                    }

                    // Send in chunks
                    const chunkSize = 4096; // 4KB chunks
                    let offset = 0;
                    const byteBuffer = int16Data.buffer;

                    const streamInterval = setInterval(() => {
                        if (offset >= byteBuffer.byteLength) {
                            clearInterval(streamInterval);
                            console.log("File streaming complete");
                            if (ws.readyState === WebSocket.OPEN) {
                                ws.send(new Uint8Array(0));
                            }
                            return;
                        }

                        if (ws.readyState === WebSocket.OPEN) {
                            const end = Math.min(offset + chunkSize, byteBuffer.byteLength);
                            const chunk = byteBuffer.slice(offset, end);
                            ws.send(chunk);
                            offset += chunkSize;
                        } else {
                            clearInterval(streamInterval);
                        }
                    }, 50); // Send faster than real-time if desired, or match playback speed. 50ms for 4KB (approx 125ms audio) is ~2.5x speed.

                    // Clean up temp context
                    tempCtx.close();

                } catch (decodeError) {
                    console.error("Error decoding audio file:", decodeError);
                }
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'transcript' && data.is_final) {
                    setTranscript(prev => [...prev, {
                        text: data.data,
                        speaker: data.speaker,
                        speaker_name: data.speaker_name
                    }]);
                }
            };

            ws.onclose = () => {
                setIsConnected(false);
            };

        } catch (error) {
            console.error("Error streaming file:", error);
        }
    }, [sessionId]);

    const stopRecording = useCallback(() => {
        if (socketRef.current) {
            const ctx = (socketRef.current as any).audioContext;
            const stream = (socketRef.current as any).stream;
            const worklet = (socketRef.current as any).workletNode;

            if (stream) {
                stream.getTracks().forEach((track: any) => track.stop());
            }
            if (worklet) {
                worklet.disconnect();
            }
            if (ctx) {
                ctx.close();
            }
            socketRef.current.close();
        }
        setIsConnected(false);
    }, []);

    return {
        isConnected,
        transcript,
        startRecording,
        stopRecording,
        streamAudioFile,
        sessionId
    };
};
