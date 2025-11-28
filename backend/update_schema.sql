-- Add chat_history column to ai_dispatch_logs table
ALTER TABLE public.ai_dispatch_logs 
ADD COLUMN IF NOT EXISTS chat_history jsonb DEFAULT '[]'::jsonb;
