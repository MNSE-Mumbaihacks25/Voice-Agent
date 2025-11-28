-- Add chat_history to investors table
ALTER TABLE public.investors 
ADD COLUMN IF NOT EXISTS chat_history JSONB DEFAULT '[]'::jsonb;

-- Remove chat_history from ai_dispatch_logs table
ALTER TABLE public.ai_dispatch_logs 
DROP COLUMN IF EXISTS chat_history;
