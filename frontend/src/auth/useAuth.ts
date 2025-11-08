import { useEffect, useState } from "react";
import { supabase } from "../lib/supabase";
import type { Session } from "@supabase/supabase-js";

export function useAuth(){
    const [session, setSession] = useState<Session | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        supabase.auth.getSession().then(({ data }) => {
            setSession(data.session ?? null)
            setLoading(false)
        })
        const { data: {subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            setSession(session ?? null)
        })
        return () => subscription.unsubscribe()
    }, [])
    return { session, loading }
}