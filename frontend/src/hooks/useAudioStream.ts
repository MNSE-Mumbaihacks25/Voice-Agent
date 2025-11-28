import { useState, useRef, useCallback, useEffect } from 'react';

export const useAudioStream = () => {
    const [isConnected, setIsConnected] = useState(false);
    const [transcript, setTranscript] = useState<{ text: string, speaker: number, speaker_name?: string }[]>([]);
    const [sessionId, setSessionId] = useState<string>("");
    const socketRef = useRef<WebSocket | null>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);

    useEffect(() => {
        // Generate a random session ID on mount
        setSessionId(Math.random().toString(36).substring(7));
    }, []);

    const startRecording = useCallback(async (agentName: string, leadName: string, language: string = "en") => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    channelCount: 1, // Force Mono
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 48000
                }
            });

            // Connect to WebSocket with names and language
            const ws = new WebSocket(`ws://localhost:8000/ws/audio?session_id=${sessionId}&agent_name=${encodeURIComponent(agentName)}&lead_name=${encodeURIComponent(leadName)}&language=${language}`);

            ws.onopen = () => {
                setIsConnected(true);
                console.log("Connected to WebSocket");
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

            socketRef.current = ws;

            // Start MediaRecorder
            const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
            mediaRecorderRef.current = mediaRecorder;

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0 && socketRef.current?.readyState === WebSocket.OPEN) {
                    console.log(`Sending audio chunk: ${event.data.size} bytes`);
                    socketRef.current.send(event.data);
                } else {
                    console.log("Skipping chunk:", event.data.size, socketRef.current?.readyState);
                }
            };

            mediaRecorder.start(250); // Revert to 250ms for low latency
            console.log("MediaRecorder started");

        } catch (error) {
            console.error("Error starting recording:", error);
        }
    }, [sessionId]);

    const streamAudioFile = useCallback(async (file: File, agentName: string, leadName: string, language: string = "en") => {
        try {
            // Connect to WebSocket with names and language
            const ws = new WebSocket(`ws://localhost:8000/ws/audio?session_id=${sessionId}&agent_name=${encodeURIComponent(agentName)}&lead_name=${encodeURIComponent(leadName)}&language=${language}`);
            socketRef.current = ws;

            ws.onopen = async () => {
                setIsConnected(true);
                console.log("Connected to WebSocket for file streaming");

                // Read file and stream
                const arrayBuffer = await file.arrayBuffer();
                const chunkSize = 16384; // Larger chunks (approx 0.5-1s of audio depending on bitrate)
                let offset = 0;

                const streamInterval = setInterval(() => {
                    if (offset >= arrayBuffer.byteLength) {
                        clearInterval(streamInterval);
                        console.log("File streaming complete");
                        // Send zero-byte message to indicate end of stream to Deepgram
                        if (ws.readyState === WebSocket.OPEN) {
                            ws.send(new Uint8Array(0));
                        }
                        return;
                    }

                    if (ws.readyState === WebSocket.OPEN) {
                        const chunk = arrayBuffer.slice(offset, offset + chunkSize);
                        ws.send(chunk);
                        offset += chunkSize;
                    }
                }, 250); // Send every 250ms to simulate real-time more accurately
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
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
            mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
        }
        if (socketRef.current) {
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
