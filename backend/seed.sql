-- Seed data for Knowledge Base (Indian Financial Context)

INSERT INTO public.knowledge_base (content, metadata, embedding) VALUES
('HDFC Top 100 Fund is a large-cap equity fund that aims to provide long-term capital appreciation by investing predominantly in the top 100 companies by market capitalization. It has an expense ratio of 1.15% and a 3-year CAGR of 15.4%.', '{"type": "mutual_fund", "name": "HDFC Top 100 Fund", "risk": "High", "category": "Large Cap"}', '[0.01, 0.02, ...]'::vector), -- Placeholder embedding
('Reliance Industries Limited (RIL) is an Indian multinational conglomerate headquartered in Mumbai. It is engaged in energy, petrochemicals, natural gas, retail, telecommunications, mass media, and textiles. Current stock price is approx ₹2,400.', '{"type": "stock", "name": "Reliance Industries", "sector": "Conglomerate", "risk": "Medium"}', '[0.03, 0.04, ...]'::vector),
('Nifty 50 is a benchmark Indian stock market index that represents the weighted average of 50 of the largest Indian companies listed on the National Stock Exchange.', '{"type": "index", "name": "Nifty 50", "risk": "High"}', '[0.05, 0.06, ...]'::vector),
('Systematic Investment Plan (SIP) allows you to invest small amounts periodically (weekly, monthly, quarterly) into a mutual fund. It helps in rupee cost averaging and compounding.', '{"type": "concept", "name": "SIP", "risk": "Low"}', '[0.07, 0.08, ...]'::vector),
('The Sharpe Ratio measures the performance of an investment compared to a risk-free asset, after adjusting for its risk. A higher Sharpe ratio indicates better risk-adjusted performance.', '{"type": "metric", "name": "Sharpe Ratio"}', '[0.09, 0.10, ...]'::vector),
('Alpha is a measure of the active return on an investment, the performance of that investment compared with a suitable market index. An alpha of 1.0 means the fund has outperformed its benchmark index by 1%.', '{"type": "metric", "name": "Alpha"}', '[0.11, 0.12, ...]'::vector);

-- Seed data for Agents
INSERT INTO public.agents (agent_id, name, specialization, email) VALUES
('agent_001', 'Rahul Sharma', 'Mutual Funds', 'rahul@example.com'),
('agent_002', 'Priya Patel', 'Stocks & Derivatives', 'priya@example.com');

-- Seed data for Investors
INSERT INTO public.investors (investor_id, name, age, city, risk_appetite, sip_capacity) VALUES
('inv_001', 'Amit Kumar', 35, 'Mumbai', 'High', 10000),
('inv_002', 'Sneha Gupta', 28, 'Bangalore', 'Medium', 5000);
