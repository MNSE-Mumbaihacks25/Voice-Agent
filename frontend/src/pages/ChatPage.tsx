import { useState, useEffect, useRef } from 'react'
import { useSearchParams, Navigate } from 'react-router-dom'
import { useAudioStream } from '../hooks/useAudioStream'
import { Button } from '../components/ui/button'
import { Card } from '../components/ui/card' // Simplified imports
import {
    Mic, MicOff, BrainCircuit, FileText, Loader2,
    Sparkles, ChevronRight, ChevronLeft, TrendingUp,
    AlertTriangle, ShieldCheck, Clock, User
} from 'lucide-react'

// --- Types ---
interface RagResponse {
    status: string
    question: string
    answer: string
    context: any[]
    timestamp: number
}

export default function ChatPage() {
    // --- 1. State & Hooks ---
    const [searchParams] = useSearchParams();
    const agentId = searchParams.get('agent_id');
    const leadId = searchParams.get('lead_id');
    const leadName = searchParams.get('lead_name') || 'Lead';
    const agentName = searchParams.get('agent_name') || 'Agent';
    const [language, setLanguage] = useState<string>("en");

    // Redirect logic
    if (!agentId || !leadId) return <Navigate to="/" replace />;

    const { isConnected, transcript, startRecording, stopRecording, streamAudioFile, sessionId } = useAudioStream()
    const [ragHistory, setRagHistory] = useState<RagResponse[]>([])
    const [isLoading, setIsLoading] = useState(false)

    // --- 2. Refs for Scrolling ---
    const transcriptEndRef = useRef<HTMLDivElement>(null)
    const copilotEndRef = useRef<HTMLDivElement>(null)
    const transcriptContainerRef = useRef<HTMLDivElement>(null)
    const copilotContainerRef = useRef<HTMLDivElement>(null)
    const lastProcessedIndexRef = useRef<number>(-1)

    // --- 3. Auto-Scroll Logic ---
    const scrollToBottom = (ref: React.RefObject<HTMLDivElement>, containerRef: React.RefObject<HTMLDivElement>) => {
        if (ref.current && containerRef.current) {
            // Check if user is already near bottom to avoid yanking them away if they are reading up
            const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
            const isNearBottom = scrollHeight - scrollTop - clientHeight < 150;

            if (isNearBottom) {
                ref.current.scrollIntoView({ behavior: "smooth" })
            }
        }
    }

    // Effect: Scroll Transcript
    useEffect(() => {
        if (transcript.length > 0) {
            // Force scroll on new message
            transcriptEndRef.current?.scrollIntoView({ behavior: "smooth" })
        }
    }, [transcript.length])

    // Effect: Scroll Copilot
    useEffect(() => {
        if (ragHistory.length > 0) {
            copilotEndRef.current?.scrollIntoView({ behavior: "smooth" })
        }
    }, [ragHistory.length])

    // --- 4. API & Trigger Logic ---
    const handleAssist = async (triggerWord?: string) => {
        setIsLoading(true)
        try {
            const res = await fetch('http://localhost:8000/assist', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, trigger_word: triggerWord })
            })
            const data = await res.json()
            setRagHistory(prev => [...prev, { ...data, timestamp: Date.now() }])
        } catch (error) {
            console.error("Failed to fetch assistance:", error)
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        if (transcript.length > 0 && transcript.length - 1 > lastProcessedIndexRef.current) {
            const lastSegment = transcript[transcript.length - 1]
            if (lastSegment.speaker === 0) {
                const triggerWord = "let me check"
                if (lastSegment.text.toLowerCase().includes(triggerWord)) {
                    handleAssist(triggerWord)
                }
            }
            lastProcessedIndexRef.current = transcript.length - 1
        }
    }, [transcript])

    // --- 5. Horizontal Scroll Helper ---
    const scrollCarousel = (id: string, direction: 'left' | 'right') => {
        const container = document.getElementById(id);
        if (container) {
            const scrollAmount = 300;
            container.scrollBy({
                left: direction === 'left' ? -scrollAmount : scrollAmount,
                behavior: 'smooth'
            });
        }
    };

    // --- 6. Helper Components for Cleaner JSX ---

    // The "Status Badge" for SIP/MFs
    const RiskBadge = ({ level }: { level: string }) => {
        const color = level?.toLowerCase().includes('high') ? 'bg-red-100 text-red-700 border-red-200'
            : level?.toLowerCase().includes('moderate') ? 'bg-amber-100 text-amber-700 border-amber-200'
                : 'bg-emerald-100 text-emerald-700 border-emerald-200';

        return (
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border flex items-center gap-1 ${color}`}>
                <ShieldCheck className="h-3 w-3" /> {level || 'Moderate'}
            </span>
        )
    }

    return (
        <div className="h-screen bg-slate-50 flex flex-col overflow-hidden font-sans text-slate-900">

            {/* === HEADER === */}
            <header className="bg-white border-b border-slate-200 px-6 py-3 flex justify-between items-center shadow-sm z-20 flex-shrink-0 h-16">
                <div className="flex items-center gap-4">
                    <div className="h-10 w-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-indigo-200 shadow-lg">
                        <BrainCircuit className="h-6 w-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-lg font-bold text-slate-800 leading-tight">Sales Copilot</h1>
                        <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
                            <span className="flex items-center gap-1"><User className="h-3 w-3" /> {agentName}</span>
                            <span className="text-slate-300">•</span>
                            <span className="flex items-center gap-1 text-indigo-600"><User className="h-3 w-3" /> {leadName}</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <select
                        className="bg-slate-50 border border-slate-200 text-slate-600 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-2 outline-none"
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        disabled={isConnected}
                    >
                        <option value="en">English</option>
                        <option value="hi">Hindi</option>
                        <option value="mr">Marathi</option>
                        <option value="ta">Tamil</option>
                    </select>

                    <div className={`px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition-all duration-300 ${isConnected ? 'bg-red-50 text-red-600 border border-red-100 ring-2 ring-red-500/10' : 'bg-slate-100 text-slate-500'
                        }`}>
                        <div className={`w-2.5 h-2.5 rounded-full ${isConnected ? 'bg-red-500 animate-pulse' : 'bg-slate-400'}`} />
                        {isConnected ? 'LIVE RECORDING' : 'READY'}
                    </div>
                </div>
            </header>

            {/* === MAIN CONTENT GRID === */}
            <main className="flex-1 flex overflow-hidden max-w-[1920px] w-full mx-auto">

                {/* --- LEFT: TRANSCRIPT --- */}
                <section className="flex-1 flex flex-col border-r border-slate-200 bg-white/50 min-w-0">
                    <div className="px-6 py-3 border-b border-slate-100 bg-white sticky top-0 z-10 flex justify-between items-center">
                        <h2 className="text-sm font-bold text-slate-600 uppercase tracking-wider flex items-center gap-2">
                            <FileText className="h-4 w-4 text-slate-400" /> Live Transcript
                        </h2>
                        {transcript.length > 0 && (
                            <span className="text-xs text-slate-400 font-mono">{transcript.length} segments</span>
                        )}
                    </div>

                    <div
                        ref={transcriptContainerRef}
                        className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth scrollbar-thin scrollbar-thumb-slate-200 hover:scrollbar-thumb-slate-300"
                    >
                        {transcript.length === 0 ? (
                            <div className="h-full flex flex-col items-center justify-center text-slate-300 space-y-4">
                                <div className="p-6 rounded-full bg-slate-50 border border-slate-100">
                                    <Mic className="h-8 w-8 text-slate-300" />
                                </div>
                                <p className="font-medium text-sm">Start the call to see real-time transcription</p>
                            </div>
                        ) : (
                            transcript.map((t, i) => (
                                <div key={i} className={`flex ${t.speaker === 0 ? 'justify-end' : 'justify-start'} group animate-in fade-in slide-in-from-bottom-2 duration-300`}>
                                    <div className={`max-w-[80%] rounded-2xl px-5 py-3.5 shadow-sm relative ${t.speaker === 0
                                            ? 'bg-indigo-600 text-white rounded-br-sm'
                                            : 'bg-white border border-slate-200 text-slate-700 rounded-bl-sm'
                                        }`}>
                                        <div className={`text-[10px] font-bold mb-1 uppercase tracking-wide opacity-70 ${t.speaker === 0 ? 'text-indigo-100 text-right' : 'text-slate-400'
                                            }`}>
                                            {t.speaker === 0 ? 'Agent' : leadName}
                                        </div>
                                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{t.text}</p>
                                    </div>
                                </div>
                            ))
                        )}
                        <div ref={transcriptEndRef} className="h-4" />
                    </div>
                </section>

                {/* --- RIGHT: COPILOT --- */}
                <section className="w-[45%] xl:w-[40%] flex flex-col bg-slate-50/50 min-w-[450px]">
                    <div className="px-6 py-3 border-b border-slate-200 bg-white sticky top-0 z-10 shadow-sm flex justify-between items-center">
                        <h2 className="text-sm font-bold text-indigo-900 uppercase tracking-wider flex items-center gap-2">
                            <Sparkles className="h-4 w-4 text-indigo-600" /> AI Suggestions
                        </h2>
                        {isLoading && (
                            <span className="flex items-center gap-2 text-xs font-bold text-indigo-600 bg-indigo-50 px-2 py-1 rounded-full">
                                <Loader2 className="h-3 w-3 animate-spin" /> Analyzing...
                            </span>
                        )}
                    </div>

                    <div
                        ref={copilotContainerRef}
                        className="flex-1 overflow-y-auto p-6 space-y-8 scroll-smooth scrollbar-thin scrollbar-thumb-indigo-200 hover:scrollbar-thumb-indigo-300"
                    >
                        {ragHistory.length === 0 ? (
                            <div className="h-full flex flex-col items-center justify-center text-center p-8">
                                <div className="w-20 h-20 bg-white rounded-2xl shadow-sm border border-slate-200 flex items-center justify-center mb-6">
                                    <BrainCircuit className="h-10 w-10 text-indigo-200" />
                                </div>
                                <h3 className="text-slate-900 font-bold mb-2">AI Companion is Ready</h3>
                                <p className="text-slate-500 text-sm max-w-xs leading-relaxed">
                                    I will analyze the conversation in real-time. Use the trigger word <span className="font-mono text-indigo-600 bg-indigo-50 px-1 rounded">"Let me check"</span> to get instant data.
                                </p>
                            </div>
                        ) : (
                            ragHistory.map((item, index) => (
                                <div key={index} className="animate-in slide-in-from-bottom-4 duration-500 fill-mode-backwards">

                                    {/* 1. The Interaction Wrapper */}
                                    <div className="bg-white rounded-xl shadow-[0_2px_8px_-2px_rgba(0,0,0,0.05)] border border-slate-200 overflow-hidden group hover:border-indigo-300 transition-all">

                                        {/* Header: Intent */}
                                        <div className="bg-gradient-to-r from-slate-50 to-white border-b border-slate-100 p-4 flex gap-3">
                                            <div className="mt-1 h-6 w-6 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
                                                <TrendingUp className="h-3.5 w-3.5 text-indigo-600" />
                                            </div>
                                            <div>
                                                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-0.5">Query</p>
                                                <p className="text-sm font-semibold text-slate-800 leading-snug">{item.question}</p>
                                            </div>
                                        </div>

                                        {/* Body: Answer */}
                                        <div className="p-5">
                                            <div className="prose prose-sm prose-slate max-w-none">
                                                <p className="text-slate-600 leading-relaxed text-[15px]">{item.answer}</p>
                                            </div>
                                        </div>

                                        {/* Footer: Data Context Carousel */}
                                        {item.context && item.context.length > 0 && (
                                            <div className="bg-slate-50 border-t border-slate-100 p-4">
                                                <div className="flex items-center justify-between mb-3">
                                                    <div className="flex items-center gap-2">
                                                        <ShieldCheck className="h-4 w-4 text-emerald-500" />
                                                        <span className="text-xs font-bold text-slate-500 uppercase">Recommended Data</span>
                                                    </div>

                                                    {/* Navigation Arrows */}
                                                    {item.context.length > 1 && (
                                                        <div className="flex gap-1">
                                                            <button onClick={() => scrollCarousel(`c-${index}`, 'left')} className="p-1.5 hover:bg-white rounded-md text-slate-400 hover:text-indigo-600 transition shadow-sm border border-transparent hover:border-slate-200">
                                                                <ChevronLeft className="h-3 w-3" />
                                                            </button>
                                                            <button onClick={() => scrollCarousel(`c-${index}`, 'right')} className="p-1.5 hover:bg-white rounded-md text-slate-400 hover:text-indigo-600 transition shadow-sm border border-transparent hover:border-slate-200">
                                                                <ChevronRight className="h-3 w-3" />
                                                            </button>
                                                        </div>
                                                    )}
                                                </div>

                                                {/* THE CAROUSEL CONTAINER */}
                                                <div
                                                    id={`c-${index}`}
                                                    className="flex gap-4 overflow-x-auto pb-2 snap-x snap-mandatory scrollbar-hide"
                                                    style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
                                                >
                                                    {item.context.map((ctx: any, i: number) => {
                                                        const isFund = !!ctx.scheme_name;

                                                        // --- CARD: Mutual Fund / Financial Product ---
                                                        if (isFund) return (
                                                            <div key={i} className="min-w-[280px] w-[280px] bg-white rounded-lg border border-slate-200 shadow-sm snap-center flex-shrink-0 overflow-hidden hover:shadow-md transition-shadow relative">
                                                                {/* Card Top Border Accent */}
                                                                <div className="h-1 w-full bg-emerald-500"></div>

                                                                <div className="p-4 space-y-4">
                                                                    <div>
                                                                        <div className="flex justify-between items-start mb-2">
                                                                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{ctx.category || 'Equity'}</span>
                                                                            <RiskBadge level={ctx.metadata?.risk_level || ctx.risk_level} />
                                                                        </div>
                                                                        <h4 className="font-bold text-slate-800 text-sm leading-tight line-clamp-2 min-h-[2.5rem]" title={ctx.scheme_name}>
                                                                            {ctx.scheme_name}
                                                                        </h4>
                                                                    </div>

                                                                    <div className="grid grid-cols-2 gap-3 bg-slate-50 p-2 rounded-lg border border-slate-100">
                                                                        <div>
                                                                            <p className="text-[10px] text-slate-500 font-medium">1Y Returns</p>
                                                                            <p className="text-emerald-600 font-bold text-lg flex items-center">
                                                                                <TrendingUp className="h-3 w-3 mr-1" />
                                                                                {ctx.returns_1yr}%
                                                                            </p>
                                                                        </div>
                                                                        <div>
                                                                            <p className="text-[10px] text-slate-500 font-medium">Min. Inv</p>
                                                                            <p className="text-slate-700 font-bold text-lg">₹500</p>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        );

                                                        // --- CARD: Knowledge Base / Text ---
                                                        return (
                                                            <div key={i} className="min-w-[260px] w-[260px] bg-white rounded-lg border border-slate-200 shadow-sm snap-center flex-shrink-0 p-4 hover:border-indigo-200 transition-colors">
                                                                <div className="flex items-center gap-2 mb-2">
                                                                    <FileText className="h-4 w-4 text-indigo-400" />
                                                                    <span className="text-xs font-bold text-slate-700 truncate">{ctx.metadata?.source || 'Policy Doc'}</span>
                                                                </div>
                                                                <p className="text-xs text-slate-600 leading-relaxed line-clamp-5">
                                                                    {ctx.content}
                                                                </p>
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))
                        )}
                        <div ref={copilotEndRef} className="h-2" />
                    </div>
                </section>
            </main>

            {/* === FOOTER CONTROLS === */}
            <footer className="bg-white border-t border-slate-200 p-4 z-20 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
                <div className="max-w-4xl mx-auto flex items-center gap-4">
                    <Button
                        size="lg"
                        onClick={isConnected ? stopRecording : () => startRecording(agentId, agentName, leadId, leadName, language)}
                        className={`flex-1 h-12 text-base font-bold transition-all shadow-md hover:shadow-lg ${isConnected
                                ? 'bg-red-500 hover:bg-red-600 text-white'
                                : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                            }`}
                    >
                        {isConnected ? (
                            <><MicOff className="mr-2 h-5 w-5" /> End Session</>
                        ) : (
                            <><Mic className="mr-2 h-5 w-5" /> Start Live Call</>
                        )}
                    </Button>

                    <Button
                        size="lg"
                        variant="outline"
                        onClick={() => handleAssist()}
                        disabled={!isConnected && transcript.length === 0}
                        className="flex-1 h-12 border-2 border-slate-200 hover:border-indigo-500 hover:bg-indigo-50 text-slate-700 font-bold text-base transition-all"
                    >
                        {isLoading ? (
                            <Loader2 className="mr-2 h-5 w-5 animate-spin text-indigo-600" />
                        ) : (
                            <BrainCircuit className="mr-2 h-5 w-5 text-indigo-600" />
                        )}
                        {isLoading ? 'Processing...' : 'Ask Copilot'}
                    </Button>

                    {/* Audio Upload Hidden Input Wrapper */}
                    <div className="relative">
                        <input
                            type="file"
                            accept="audio/*"
                            id="audio-upload"
                            className="hidden"
                            onChange={(e) => {
                                const file = e.target.files?.[0];
                                if (file) streamAudioFile(file, agentId, agentName, leadId, leadName, language);
                            }}
                        />
                        <Button
                            asChild
                            variant="ghost"
                            size="icon"
                            className="h-12 w-12 border border-slate-200 rounded-lg hover:bg-slate-50 text-slate-400 hover:text-indigo-600"
                        >
                            <label htmlFor="audio-upload" className="cursor-pointer flex items-center justify-center w-full h-full">
                                <FileText className="h-5 w-5" />
                            </label>
                        </Button>
                    </div>
                </div>
            </footer>
        </div>
    )
}