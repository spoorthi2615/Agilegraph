import { createClient } from '@supabase/supabase-js';

// Default to dummy values if not provided so the app doesn't crash during UI development
const supabaseUrl = (import.meta.env.VITE_SUPABASE_URL || 'https://placeholder-project.supabase.co').trim();
const supabaseAnonKey = (import.meta.env.VITE_SUPABASE_ANON_KEY || 'placeholder-anon-key').trim();

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
