import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

export interface Agent {
    agent_id: string;
    name: string;
}

interface AgentSelectorProps {
    onSelectAgent: (agent: Agent) => void;
}

export function AgentSelector({ onSelectAgent }: AgentSelectorProps) {
    const [agents, setAgents] = useState<Agent[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAgents = async () => {
            try {
                const response = await fetch('http://localhost:8000/agents/');
                const data = await response.json();
                setAgents(data);
            } catch (error) {
                console.error('Error fetching agents:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchAgents();
    }, []);

    return (
        <Card className="w-full max-w-md mb-6">
            <CardHeader>
                <CardTitle>Select Agent</CardTitle>
            </CardHeader>
            <CardContent>
                {loading ? (
                    <p>Loading agents...</p>
                ) : (
                    <select
                        className="w-full p-2 border rounded-md bg-background text-foreground"
                        onChange={(e) => {
                            const agent = agents.find(a => a.agent_id === e.target.value);
                            if (agent) onSelectAgent(agent);
                        }}
                        defaultValue=""
                    >
                        <option value="" disabled>Select an agent</option>
                        {agents.map((agent) => (
                            <option key={agent.agent_id} value={agent.agent_id}>
                                {agent.name}
                            </option>
                        ))}
                    </select>
                )}
            </CardContent>
        </Card>
    );
}
