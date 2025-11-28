import { useState, useEffect, useRef } from 'react'
import { useAudioStream } from './hooks/useAudioStream'
import { Button } from './components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card'
import { Mic, MicOff, BrainCircuit, FileText, Loader2 } from 'lucide-react'

interface RagResponse {
    status: string
    question: string
    answer: string
    context: any[]
}

interface AnalyticsReport {
    sentiment: string
    objections: string[]
    adherence: string
    next_steps: string[]
}

function App() {
    const { isConnected, transcript, startRecording, stopRecording, streamAudioFile, sessionId } = useAudioStream()
    const [ragResult, setRagResult] = useState<RagResponse | null>(null)
    const [report, setReport] = useState<AnalyticsReport | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [isReportLoading, setIsReportLoading] = useState(false)

    const transcriptEndRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        transcriptEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [transcript])

    const handleAssist = async () => {
        setIsLoading(true)
        try {
            const res = await fetch('http://localhost:8000/assist', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            })
            const data = await res.json()
            setRagResult(data)
        } catch (e) {
            console.error(e)
        } finally {
            setIsLoading(false)
        }
    }

    const handleEndCall = async () => {
        stopRecording()
        setIsReportLoading(true)
        try {
            const res = await fetch('http://localhost:8000/end-call', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            })
            const data = await res.json()
            setReport(data)
        } catch (e) {
            console.error(e)
        } finally {
            setIsReportLoading(false)
        }
    }

    const [agentName, setAgentName] = useState("John Smith")
    const [leadName, setLeadName] = useState("Karen Smith")
    const [language, setLanguage] = useState("en")

    const handleStartCall = () => {
        startRecording(agentName, leadName, language)
    }

    const [triggerWord, setTriggerWord] = useState("let me check")
    const [audioFile, setAudioFile] = useState<File | null>(null)
    const audioPlayerRef = useRef<HTMLAudioElement | null>(null)

    const lastProcessedIndexRef = useRef(-1)

    // Auto-trigger RAG
    useEffect(() => {
        if (transcript.length > 0) {
            // Check only new segments
            for (let i = lastProcessedIndexRef.current + 1; i < transcript.length; i++) {
                const segment = transcript[i]
                // Strict check: Trigger only if spoken by the Agent
                if (
                    segment.speaker_name === agentName &&
                    segment.text.toLowerCase().includes(triggerWord.toLowerCase())
                ) {
                    console.log("Trigger word detected from Agent:", triggerWord, "in segment:", segment.text)
                    handleAssist()
                }
            }
            lastProcessedIndexRef.current = transcript.length - 1
        }
    }, [transcript, triggerWord, agentName])

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setAudioFile(e.target.files[0])
        }
    }

    const handlePlayAndStream = async () => {
        if (!audioFile) return

        // Start streaming to backend
        streamAudioFile(audioFile, agentName, leadName, language)

        // Play locally
        if (audioPlayerRef.current) {
            audioPlayerRef.current.src = URL.createObjectURL(audioFile)
            audioPlayerRef.current.play()
        }
    }

    return (
        <div className="min-h-screen bg-slate-50 p-8 font-sans text-slate-900">
            <div className="max-w-6xl mx-auto space-y-8">

                {/* Header */}
                <header className="flex flex-col md:flex-row justify-between items-center pb-6 border-b border-slate-200 gap-4">
                    <div>
                        <h1 className="text-3xl font-bold text-indigo-600 tracking-tight">Sales Copilot</h1>
                        <p className="text-slate-500 mt-1">Real-time AI assistance for financial agents</p>
                    </div>

                    <div className="flex flex-col items-end gap-4">
                        <div className="flex gap-2 items-center">
                            <input
                                type="text"
                                placeholder="Agent Name"
                                value={agentName}
                                onChange={(e) => setAgentName(e.target.value)}
                                className="px-3 py-2 border border-slate-300 rounded-md text-sm w-32 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                disabled={isConnected}
                            />
                            <input
                                type="text"
                                placeholder="Lead Name"
                                value={leadName}
                                onChange={(e) => setLeadName(e.target.value)}
                                className="px-3 py-2 border border-slate-300 rounded-md text-sm w-32 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                disabled={isConnected}
                            />
                            <select
                                value={language}
                                onChange={(e) => setLanguage(e.target.value)}
                                className="px-3 py-2 border border-slate-300 rounded-md text-sm w-32 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                                disabled={isConnected}
                            >
                                <option value="en">English</option>
                                <option value="hi">Hindi</option>
                                <option value="hi">Hinglish</option>
                            </select>
                            <input
                                type="text"
                                placeholder="Trigger Word"
                                value={triggerWord}
                                onChange={(e) => setTriggerWord(e.target.value)}
                                className="px-3 py-2 border border-indigo-300 rounded-md text-sm w-32 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-indigo-50"
                            />
                        </div>

                        <div className="flex items-center gap-4">
                            {/* File Upload Section */}
                            <div className="flex items-center gap-2">
                                <input
                                    type="file"
                                    accept="audio/*"
                                    onChange={handleFileUpload}
                                    className="text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                                    disabled={isConnected}
                                />
                                <Button
                                    variant="outline"
                                    onClick={handlePlayAndStream}
                                    disabled={!audioFile || isConnected}
                                    className="border-indigo-200 text-indigo-700 hover:bg-indigo-50"
                                >
                                    Simulate Call
                                </Button>
                                <audio ref={audioPlayerRef} className="hidden" />
                            </div>

                            <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${isConnected ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-600'}`}>
                                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-red-500 animate-pulse' : 'bg-slate-400'}`} />
                                {isConnected ? 'Live Recording' : 'Ready'}
                            </div>
                            <Button
                                variant={isConnected ? "destructive" : "default"}
                                onClick={isConnected ? stopRecording : handleStartCall}
                                className="w-40"
                            >
                                {isConnected ? <><MicOff className="mr-2 h-4 w-4" /> End Stream</> : <><Mic className="mr-2 h-4 w-4" /> Start Call</>}
                            </Button>
                        </div>
                    </div>
                </header>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                    {/* Left Column: Live Transcript */}
                    <div className="lg:col-span-2 space-y-6">
                        <Card className="h-[500px] flex flex-col shadow-md border-slate-200">
                            <CardHeader className="bg-white border-b border-slate-100 pb-4">
                                <CardTitle className="text-lg font-medium flex items-center gap-2">
                                    <FileText className="h-5 w-5 text-indigo-500" />
                                    Live Transcript
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50/50">
                                {transcript.length === 0 ? (
                                    <div className="h-full flex items-center justify-center text-slate-400 italic">
                                        Start the call to see real-time transcription...
                                    </div>
                                ) : (
                                    transcript.map((item, i) => (
                                        <div key={i} className={`p-3 rounded-lg shadow-sm border text-slate-700 leading-relaxed ${
                                            // Highlight Agent (Speaker 0 or matching Agent Name)
                                            (item.speaker === 0 || item.speaker_name === agentName) ? 'bg-indigo-50 border-indigo-100 ml-8' : 'bg-white border-slate-100 mr-8'
                                            }`}>
                                            <div className="text-xs font-semibold mb-1 text-slate-400 uppercase tracking-wider">
                                                {item.speaker_name || (item.speaker !== undefined ? `Speaker ${item.speaker}` : 'Unknown Speaker')}
                                            </div>
                                            {item.text}
                                        </div>
                                    ))
                                )}
                                <div ref={transcriptEndRef} />
                            </CardContent>
                        </Card>

                        {/* Action Bar */}
                        <div className="flex gap-4">
                            <Button
                                size="lg"
                                className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-200 transition-all"
                                onClick={handleAssist}
                                disabled={!isConnected && transcript.length === 0}
                            >
                                {isLoading ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : <BrainCircuit className="mr-2 h-5 w-5" />}
                                Analyze & Answer (RAG)
                            </Button>
                            <Button
                                size="lg"
                                variant="outline"
                                className="flex-1 border-slate-300 hover:bg-slate-50 text-slate-700"
                                onClick={handleEndCall}
                                disabled={transcript.length === 0}
                            >
                                Generate Post-Call Report
                            </Button>
                        </div>
                    </div>

                    {/* Right Column: AI Insights */}
                    <div className="space-y-6">

                        {/* RAG Result */}
                        {ragResult && (
                            <Card className="border-indigo-100 shadow-md bg-white overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
                                <div className="bg-indigo-50/50 p-4 border-b border-indigo-100">
                                    <h3 className="font-semibold text-indigo-900 text-sm uppercase tracking-wider">AI Suggestion</h3>
                                </div>
                                <CardContent className="p-5 space-y-4">
                                    <div>
                                        <p className="text-xs font-medium text-slate-400 uppercase mb-1">Detected Question</p>
                                        <p className="text-slate-800 font-medium italic">"{ragResult.question}"</p>
                                    </div>
                                    <div className="bg-indigo-50 p-4 rounded-md border border-indigo-100">
                                        <p className="text-indigo-900 leading-relaxed">{ragResult.answer}</p>
                                    </div>
                                    {ragResult.context && (
                                        <div className="pt-2">
                                            <p className="text-xs text-slate-400 mb-1">Source Context</p>
                                            <div className="flex gap-2 overflow-x-auto pb-2">
                                                {ragResult.context.map((ctx: any, i: number) => (
                                                    <span key={i} className="inline-block px-2 py-1 bg-slate-100 text-slate-600 text-xs rounded border border-slate-200 whitespace-nowrap">
                                                        {ctx.metadata?.name || 'Doc'}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        )}

                        {/* Post-Call Report */}
                        {isReportLoading && (
                            <Card className="border-slate-200 shadow-sm">
                                <CardContent className="p-8 flex flex-col items-center justify-center text-slate-500">
                                    <Loader2 className="h-8 w-8 animate-spin mb-2 text-indigo-500" />
                                    <p>Generating Analytics Report...</p>
                                </CardContent>
                            </Card>
                        )}

                        {report && (
                            <Card className="border-green-100 shadow-md bg-white overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
                                <div className="bg-green-50/50 p-4 border-b border-green-100">
                                    <h3 className="font-semibold text-green-900 text-sm uppercase tracking-wider">Call Analytics</h3>
                                </div>
                                <CardContent className="p-5 space-y-4">
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-slate-500">Sentiment</span>
                                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${report.sentiment.toLowerCase().includes('positive') ? 'bg-green-100 text-green-700' :
                                            report.sentiment.toLowerCase().includes('negative') ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'
                                            }`}>
                                            {report.sentiment}
                                        </span>
                                    </div>

                                    <div>
                                        <p className="text-xs font-medium text-slate-400 uppercase mb-2">Objections Raised</p>
                                        <ul className="space-y-1">
                                            {report.objections.map((obj, i) => (
                                                <li key={i} className="text-sm text-slate-700 flex items-start gap-2">
                                                    <span className="text-red-400 mt-1">•</span> {obj}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    <div>
                                        <p className="text-xs font-medium text-slate-400 uppercase mb-2">Next Steps</p>
                                        <ul className="space-y-1">
                                            {report.next_steps.map((step, i) => (
                                                <li key={i} className="text-sm text-slate-700 flex items-start gap-2">
                                                    <span className="text-indigo-400 mt-1">→</span> {step}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                </CardContent>
                            </Card>
                        )}

                    </div>
                </div>
            </div>
        </div>
    )
}

export default App
