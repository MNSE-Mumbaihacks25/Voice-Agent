import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { User, Users, ArrowRight } from 'lucide-react';

interface Agent {
    agent_id: string;
    name: string;
}

interface Lead {
    id: number;
    lead_name: string;
    lead_persona: string;
    top_candidate: string;
    assigned_agent: string;
}

export default function SelectionPage() {
    const [agents, setAgents] = useState<Agent[]>([]);
    const [leads, setLeads] = useState<Lead[]>([]);
    const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
    const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
    const navigate = useNavigate();

    useEffect(() => {
        // Fetch Agents
        fetch('http://localhost:8000/agents/')
            .then(res => res.json())
            .then(data => {
                if (Array.isArray(data)) {
                    setAgents(data);
                } else {
                    console.error("Agents data is not an array:", data);
                    setAgents([]);
                }
            })
            .catch(err => console.error("Failed to fetch agents:", err));
    }, []);

    useEffect(() => {
        if (selectedAgent) {
            // Fetch Leads for Agent
            fetch(`http://localhost:8000/agents/${selectedAgent}/leads`)
                .then(res => res.json())
                .then(data => setLeads(data))
                .catch(err => console.error("Failed to fetch leads:", err));
        } else {
            setLeads([]);
        }
    }, [selectedAgent]);

    const handleStartChat = () => {
        if (selectedAgent && selectedLead) {
            const agent = agents.find(a => a.agent_id === selectedAgent);
            const agentName = agent ? agent.name : 'Agent';
            navigate(`/chat?agent_id=${selectedAgent}&agent_name=${encodeURIComponent(agentName)}&lead_id=${selectedLead.id}&lead_name=${encodeURIComponent(selectedLead.lead_name)}`);
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 p-8 flex items-center justify-center">
            <Card className="w-full max-w-4xl shadow-xl">
                <CardHeader className="bg-indigo-600 text-white rounded-t-lg">
                    <CardTitle className="text-2xl flex items-center gap-2">
                        <Users className="h-6 w-6" /> Select Agent & Lead
                    </CardTitle>
                </CardHeader>
                <CardContent className="p-6 space-y-8">

                    {/* Agent Selection */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-slate-700 flex items-center gap-2">
                            <User className="h-5 w-5 text-indigo-600" /> 1. Choose an Agent
                        </h3>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                            {agents.map(agent => (
                                <button
                                    key={agent.agent_id}
                                    onClick={() => { setSelectedAgent(agent.agent_id); setSelectedLead(null); }}
                                    className={`p-4 rounded-lg border text-left transition-all ${selectedAgent === agent.agent_id
                                        ? 'bg-indigo-50 border-indigo-500 ring-2 ring-indigo-200'
                                        : 'bg-white border-slate-200 hover:border-indigo-300'
                                        }`}
                                >
                                    <div className="font-medium text-slate-900">{agent.name}</div>
                                    <div className="text-xs text-slate-500">ID: {agent.agent_id}</div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Lead Selection */}
                    {selectedAgent && (
                        <div className="space-y-4 animate-in fade-in slide-in-from-top-4 duration-500">
                            <h3 className="text-lg font-semibold text-slate-700 flex items-center gap-2">
                                <Users className="h-5 w-5 text-indigo-600" /> 2. Select a Lead
                            </h3>
                            {leads.length === 0 ? (
                                <p className="text-slate-500 italic">No leads assigned to this agent.</p>
                            ) : (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {leads.map(lead => (
                                        <button
                                            key={lead.id}
                                            onClick={() => setSelectedLead(lead)}
                                            className={`p-4 rounded-lg border text-left transition-all ${selectedLead?.id === lead.id
                                                ? 'bg-indigo-50 border-indigo-500 ring-2 ring-indigo-200'
                                                : 'bg-white border-slate-200 hover:border-indigo-300'
                                                }`}
                                        >
                                            <div className="flex justify-between items-start">
                                                <div className="font-medium text-slate-900">{lead.lead_name}</div>
                                                <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full">
                                                    {lead.top_candidate}
                                                </span>
                                            </div>
                                            <div className="text-sm text-slate-600 mt-1">{lead.lead_persona}</div>
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {/* Start Button */}
                    <div className="pt-4 flex justify-end">
                        <Button
                            size="lg"
                            onClick={handleStartChat}
                            disabled={!selectedAgent || !selectedLead}
                            className="bg-indigo-600 hover:bg-indigo-700 text-white px-8"
                        >
                            Start Conversation <ArrowRight className="ml-2 h-5 w-5" />
                        </Button>
                    </div>

                </CardContent>
            </Card>
        </div>
    );
}
