import { useState, useEffect, useRef } from 'react'
import { useSearchParams, Navigate } from 'react-router-dom'
import { useAudioStream } from '../hooks/useAudioStream'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { ScrollArea } from '../components/ui/scroll-area'
import { Mic, MicOff, BrainCircuit, FileText, Loader2, TrendingUp, Shield, Info } from 'lucide-react'

interface RagResponse {
    status: string
    question: string
    answer: string
    context: any[]
}

export default function ChatPage() {
    const [searchParams] = useSearchParams();
    const agentId = searchParams.get('agent_id');
    const leadId = searchParams.get('lead_id');
    const leadName = searchParams.get('lead_name') || 'Lead';

    const agentName = searchParams.get('agent_name') || 'Agent';
    const [language, setLanguage] = useState<string>("en");

    // Redirect if missing params
    if (!agentId || !leadId) {
        return <Navigate to="/" replace />;
    }

    const { isConnected, transcript, startRecording, stopRecording, streamAudioFile, sessionId } = useAudioStream()
    const [ragResult, setRagResult] = useState<RagResponse | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const transcriptEndRef = useRef<HTMLDivElement>(null)
    const lastProcessedIndexRef = useRef<number>(-1)

    // Scroll to bottom of transcript
    useEffect(() => {
        transcriptEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [transcript])

    const handleAssist = async (triggerWord?: string) => {
        setIsLoading(true)
        try {
            const res = await fetch('http://localhost:8000/assist', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    trigger_word: triggerWord
                })
            })
            const data = await res.json()
            setRagResult(data)
        } catch (error) {
            console.error("Failed to fetch assistance:", error)
        } finally {
            setIsLoading(false)
        }
    }

    // Auto-trigger logic
    useEffect(() => {
        if (transcript.length > 0 && transcript.length - 1 > lastProcessedIndexRef.current) {
            const lastSegment = transcript[transcript.length - 1]

            // Only check if Agent is speaking (speaker 0)
            if (lastSegment.speaker === 0) {
                const triggerWord = "let me check"
                if (lastSegment.text.toLowerCase().includes(triggerWord)) {
                    console.log("Trigger word detected:", triggerWord)
                    handleAssist(triggerWord)
                }
            }
            lastProcessedIndexRef.current = transcript.length - 1
        }
    }, [transcript])

    return (
        <div className="min-h-screen bg-slate-50 p-6 flex gap-6 font-sans text-slate-900">
            {/* Left Panel: Live Transcript */}
            <Card className="flex-1 flex flex-col shadow-xl border-0 bg-white/80 backdrop-blur-sm h-[calc(100vh-3rem)]">
                <CardHeader className="border-b border-slate-100 bg-white/50 pb-4">
                    <div className="flex justify-between items-center">
                        <div>
                            <CardTitle className="text-xl font-bold text-indigo-900 flex items-center gap-2">
                                <Mic className="h-5 w-5 text-indigo-600" /> Live Transcript
                            </CardTitle>
                            <p className="text-sm text-slate-500 mt-1">
                                Agent: {agentName} | Lead: {leadName}
                            </p>
                        </div>
                        <div className="flex items-center gap-4">
                            <select
                                className="bg-white border border-slate-200 text-slate-700 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-2"
                                value={language}
                                onChange={(e) => setLanguage(e.target.value)}
                                disabled={isConnected}
                            >
                                <option value="en">English</option>
                                <option value="hi">Hindi</option>
                                <option value="mr">Marathi</option>
                                <option value="ta">Tamil</option>
                            </select>
                            <div className={`px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1.5 ${isConnected ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'}`}>
                                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-slate-400'}`} />
                                {isConnected ? 'Live' : 'Offline'}
                            </div>
                        </div>
                    </div>
                </CardHeader>
                <CardContent className="flex-1 overflow-hidden flex flex-col p-0">
                    <ScrollArea className="flex-1 p-6">
                        <div className="space-y-6">
                            {transcript.length === 0 && (
                                <div className="text-center text-slate-400 py-20">
                                    <p>Waiting for conversation to start...</p>
                                </div>
                            )}
                            {transcript.map((t, i) => (
                                <div key={i} className={`flex ${t.speaker === 0 ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`max-w-[80%] rounded-2xl px-5 py-3 shadow-sm ${t.speaker === 0
                                        ? 'bg-indigo-600 text-white rounded-br-none'
                                        : 'bg-white border border-slate-100 text-slate-800 rounded-bl-none'
                                        }`}>
                                        <p className={`text-xs mb-1 font-medium ${t.speaker === 0 ? 'text-indigo-200' : 'text-slate-400'}`}>
                                            {t.speaker === 0 ? 'Agent' : leadName}
                                        </p>
                                        <p className="leading-relaxed">{t.text}</p>
                                    </div>
                                </div>
                            ))}
                            <div ref={transcriptEndRef} />
                        </div>
                    </ScrollArea>

                    {/* Controls */}
                    <div className="p-6 bg-white border-t border-slate-100">
                        <div className="flex gap-4 mb-4">
                            <Button
                                size="lg"
                                className={`flex-1 transition-all ${isConnected ? 'bg-red-500 hover:bg-red-600 text-white' : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-200'}`}
                                onClick={isConnected ? stopRecording : () => startRecording(agentId, agentName, leadId, leadName, language)}
                            >
                                {isConnected ? <><MicOff className="mr-2 h-5 w-5" /> End Call</> : <><Mic className="mr-2 h-5 w-5" /> Start Call</>}
                            </Button>

                            <Button
                                size="lg"
                                className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-200 transition-all"
                                onClick={() => handleAssist()}
                                disabled={!isConnected && transcript.length === 0}
                            >
                                {isLoading ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : <BrainCircuit className="mr-2 h-5 w-5" />}
                                {isLoading ? 'Analyzing...' : 'Ask AI Assistant'}
                            </Button>
                        </div>

                        <div className="relative">
                            <input
                                type="file"
                                accept="audio/*"
                                className="hidden"
                                id="audio-upload"
                                onChange={(e) => {
                                    const file = e.target.files?.[0];
                                    if (file) streamAudioFile(file, agentId, agentName, leadId, leadName, language);
                                }}
                            />
                            <label
                                htmlFor="audio-upload"
                                className="block w-full text-center py-2 px-4 border-2 border-dashed border-slate-200 rounded-lg text-slate-500 hover:border-indigo-400 hover:text-indigo-600 cursor-pointer transition-colors text-sm font-medium"
                            >
                                Upload Audio File to Simulate Stream
                            </label>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Right Panel: AI Assistant */}
            <Card className="w-[400px] flex flex-col shadow-xl border-0 bg-white/80 backdrop-blur-sm h-[calc(100vh-3rem)]">
                <CardHeader className="border-b border-slate-100 bg-white/50 pb-4">
                    <CardTitle className="text-xl font-bold text-indigo-900 flex items-center gap-2">
                        <BrainCircuit className="h-5 w-5 text-indigo-600" /> AI Copilot
                    </CardTitle>
                </CardHeader>
                <CardContent className="flex-1 overflow-hidden p-0 relative">
                    <ScrollArea className="h-full">
                        <div className="p-6 space-y-6">
                            {!ragResult ? (
                                <div className="text-center py-20 space-y-4">
                                    <div className="w-16 h-16 bg-indigo-50 rounded-full flex items-center justify-center mx-auto">
                                        <BrainCircuit className="h-8 w-8 text-indigo-400" />
                                    </div>
                                    <div className="space-y-2">
                                        <h3 className="font-semibold text-slate-700">Ready to Assist</h3>
                                        <p className="text-sm text-slate-500 max-w-[200px] mx-auto">
                                            I'm listening to the conversation. Say "Let me check" to trigger a search.
                                        </p>
                                    </div>
                                </div>
                            ) : (
                                <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-6">
                                    {/* Intent Section */}
                                    <div className="bg-indigo-50/50 rounded-xl p-4 border border-indigo-100">
                                        <p className="text-xs font-semibold text-indigo-400 uppercase mb-2 flex items-center gap-1.5">
                                            <BrainCircuit className="h-3 w-3" /> Detected Intent
                                        </p>
                                        <p className="font-medium text-indigo-900">{ragResult.question}</p>
                                    </div>

                                    {/* Answer Section */}
                                    <div className="space-y-3">
                                        <p className="text-xs font-semibold text-slate-400 uppercase flex items-center gap-2">
                                            <FileText className="h-3 w-3" /> Suggested Response
                                        </p>
                                        <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-100 leading-relaxed text-slate-700">
                                            <p className="text-indigo-900 leading-relaxed">{ragResult.answer}</p>
                                        </div>
                                    </div>

                                    {/* Context Section */}
                                    {ragResult.context && (
                                        <div className="pt-4 border-t border-indigo-50">
                                            <p className="text-xs font-semibold text-slate-400 uppercase mb-3 flex items-center gap-2">
                                                <Info className="h-3 w-3" /> Relevant Data Points
                                            </p>
                                            <div className="flex gap-3 overflow-x-auto pb-4 snap-x">
                                                {ragResult.context.map((ctx: any, i: number) => {
                                                    const isFund = !!ctx.scheme_name;
                                                    return (
                                                        <div key={i} className="min-w-[240px] max-w-[240px] bg-white border border-slate-200 rounded-lg p-3 shadow-sm snap-center flex-shrink-0 hover:border-indigo-300 transition-colors">
                                                            {isFund ? (
                                                                <div className="space-y-2">
                                                                    <div className="flex items-start justify-between gap-2">
                                                                        <h4 className="font-semibold text-indigo-700 text-sm leading-tight line-clamp-2" title={ctx.scheme_name}>
                                                                            {ctx.scheme_name}
                                                                        </h4>
                                                                        <span className="text-[10px] px-1.5 py-0.5 bg-indigo-50 text-indigo-600 rounded font-medium whitespace-nowrap">
                                                                            {ctx.category}
                                                                        </span>
                                                                    </div>

                                                                    <div className="grid grid-cols-2 gap-2 text-xs">
                                                                        <div className="bg-green-50 p-1.5 rounded border border-green-100">
                                                                            <p className="text-green-600 font-medium flex items-center gap-1">
                                                                                <TrendingUp className="h-3 w-3" /> 1Y Return
                                                                            </p>
                                                                            <p className="text-green-800 font-bold mt-0.5">{ctx.returns_1yr}%</p>
                                                                        </div>
                                                                        <div className="bg-slate-50 p-1.5 rounded border border-slate-100">
                                                                            <p className="text-slate-500 font-medium flex items-center gap-1">
                                                                                <Shield className="h-3 w-3" /> Risk
                                                                            </p>
                                                                            <p className="text-slate-700 font-bold mt-0.5">{ctx.metadata?.risk_level || ctx.risk_level || 'N/A'}</p>
                                                                        </div>
                                                                    </div>

                                                                    <div className="text-[10px] text-slate-500 flex justify-between pt-1 border-t border-slate-100">
                                                                        <span>Exp: {ctx.metadata?.expense_ratio || ctx.expense_ratio}%</span>
                                                                        <span>SIP: ₹{ctx.metadata?.min_sip || ctx.min_sip}</span>
                                                                    </div>
                                                                </div>
                                                            ) : (
                                                                <div className="space-y-2">
                                                                    <h4 className="font-semibold text-slate-700 text-sm flex items-center gap-2">
                                                                        <FileText className="h-3 w-3" />
                                                                        {ctx.metadata?.name || 'Knowledge Base'}
                                                                    </h4>
                                                                    <p className="text-xs text-slate-600 line-clamp-4 leading-relaxed">
                                                                        {ctx.content}
                                                                    </p>
                                                                </div>
                                                            )}
                                                        </div>
                                                    )
                                                })}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </ScrollArea>
                </CardContent>
            </Card>
        </div>
    )
}
