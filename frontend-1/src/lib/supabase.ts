import { createClient } from '@supabase/supabase-js';

// Default to the actual values if .env fails to load
const supabaseUrl = (import.meta.env.VITE_SUPABASE_URL || 'https://edwxfhoaxqhngvrcnieb.supabase.co').trim();
const supabaseAnonKey = (import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVkd3hmaG9heHFobmd2cmNuaWViIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU0ODk1MjYsImV4cCI6MjEwMTA2NTUyNn0.Vhsfh1bapHAPQEPSR4ImrbouW4Hss5FbbhckmX-VnPo').trim();

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
