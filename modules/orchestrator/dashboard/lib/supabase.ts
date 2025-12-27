
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

if (!supabaseUrl || !supabaseKey) {
    console.error("⚠️ SUPABASE CONFIG MISSING");
    console.error("URL:", supabaseUrl);
    console.error("Refusing to create client without key.");
}

export const supabase = createClient(supabaseUrl || "", supabaseKey || "");
