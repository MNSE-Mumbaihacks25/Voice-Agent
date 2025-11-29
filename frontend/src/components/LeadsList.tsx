import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

export interface Lead {
    id: string;
    lead_name: string;
    lead_persona: string;
    top_candidate: string;
    math_score: number;
    reasoning: string;
    created_at: string;
}

interface LeadsListProps {
    leads: Lead[];
    loading: boolean;
    onSelectLead: (lead: Lead) => void;
    selectedLeadId?: string;
}

export function LeadsList({ leads, loading, onSelectLead, selectedLeadId }: LeadsListProps) {
    if (loading) {
        return <div className="text-center p-4">Loading leads...</div>;
    }

    if (leads.length === 0) {
        return <div className="text-center p-4 text-muted-foreground">No leads found for this agent.</div>;
    }

    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {leads.map((lead) => (
                <Card
                    key={lead.id}
                    className={`flex flex-col cursor-pointer transition-all hover:shadow-md ${selectedLeadId === lead.id ? 'ring-2 ring-indigo-500 bg-indigo-50' : ''}`}
                    onClick={() => onSelectLead(lead)}
                >
                    <CardHeader>
                        <CardTitle className="text-lg">{lead.lead_name}</CardTitle>
                        <p className="text-sm text-muted-foreground">{lead.lead_persona}</p>
                    </CardHeader>
                    <CardContent className="flex-1">
                        <div className="space-y-2">
                            <div className="flex justify-between">
                                <span className="font-semibold">Match Score:</span>
                                <span>{lead.math_score}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="font-semibold">Top Candidate:</span>
                                <span>{lead.top_candidate}</span>
                            </div>
                            <div className="mt-4">
                                <p className="font-semibold mb-1">Reasoning:</p>
                                <p className="text-sm text-muted-foreground line-clamp-3" title={lead.reasoning}>
                                    {lead.reasoning}
                                </p>
                            </div>
                            <div className="text-xs text-muted-foreground mt-4 pt-2 border-t">
                                {new Date(lead.created_at).toLocaleDateString()}
                            </div>
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}
