'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import { User } from '@supabase/supabase-js';

interface UserProfile {
  id: string;
  email: string;
  tenant_id: string;
  role: string;
}

interface Tenant {
  id: string;
  name: string;
  slug: string;
  domain: string;
  settings: any;
  is_active: boolean;
}

interface SupabaseContextType {
  user: User | null;
  userProfile: UserProfile | null;
  tenant: Tenant | null;
  loading: boolean;
  signOut: () => Promise<void>;
}

const SupabaseContext = createContext<SupabaseContextType | undefined>(undefined);

export function SupabaseProvider({ children }: { children: React.ReactNode }) {
  console.log('🔍 SupabaseProvider: Component rendered')
  
  const [user, setUser] = useState<User | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [tenant, setTenant] = useState<Tenant | null>(null);
  const [loading, setLoading] = useState(true);
  const supabase = createClientComponentClient();

  console.log('🔍 SupabaseProvider: Initial state:', { user, userProfile, tenant, loading })

  useEffect(() => {
    console.log('🔍 SupabaseProvider: useEffect - initial session')
    // Get initial session
    const getInitialSession = async () => {
      console.log('🔍 SupabaseProvider: Getting initial session...')
      const { data: { session } } = await supabase.auth.getSession();
      console.log('🔍 SupabaseProvider: Initial session:', session)
      setUser(session?.user ?? null);
      
      if (session?.user) {
        console.log('🔍 SupabaseProvider: User found in session, loading profile...')
        await loadUserProfile(session.user);
      }
      
      setLoading(false);
      console.log('🔍 SupabaseProvider: Initial loading complete')
    };

    getInitialSession();

    // Listen for auth changes
    console.log('🔍 SupabaseProvider: Setting up auth state listener')
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('🔍 SupabaseProvider: Auth state change:', event, session?.user?.email)
        setUser(session?.user ?? null);
        
        if (session?.user) {
          console.log('🔍 SupabaseProvider: User authenticated, loading profile...')
          await loadUserProfile(session.user);
        } else {
          console.log('🔍 SupabaseProvider: User signed out, clearing profile')
          setUserProfile(null);
          setTenant(null);
        }
        
        setLoading(false);
      }
    );

    return () => subscription.unsubscribe();
  }, [supabase]);

  const loadUserProfile = async (user: User) => {
    console.log('🔍 SupabaseProvider: loadUserProfile called for user:', user.email)
    try {
      // Get user profile from system.users
      const { data: profile, error: profileError } = await supabase
        .from('system.users')
        .select('*')
        .eq('id', user.id)
        .single();

      if (profileError) {
        console.error('❌ Error loading user profile:', profileError);
        return;
      }

      console.log('🔍 SupabaseProvider: User profile loaded:', profile)
      if (profile) {
        setUserProfile(profile);

        // Get tenant information
        const { data: tenantData, error: tenantError } = await supabase
          .from('system.tenants')
          .select('*')
          .eq('id', profile.tenant_id)
          .single();

        if (tenantError) {
          console.error('❌ Error loading tenant:', tenantError);
          return;
        }

        console.log('🔍 SupabaseProvider: Tenant loaded:', tenantData)
        setTenant(tenantData);
      }
    } catch (error) {
      console.error('❌ Error in loadUserProfile:', error);
    }
  };

  const signOut = async () => {
    console.log('🔍 SupabaseProvider: signOut called')
    try {
      await supabase.auth.signOut();
      console.log('✅ Sign out successful')
    } catch (error) {
      console.error('❌ Error signing out:', error);
    }
  };

  const value = { user, userProfile, tenant, loading, signOut };
  
  console.log('🔍 SupabaseProvider: Providing context value:', { 
    user: user?.email, 
    userProfile: userProfile?.email, 
    tenant: tenant?.name, 
    loading 
  })

  return (
    <SupabaseContext.Provider value={value}>
      {children}
    </SupabaseContext.Provider>
  );
}

export function useSupabase() {
  console.log('🔍 useSupabase: Hook called')
  const context = useContext(SupabaseContext);
  if (context === undefined) {
    console.error('❌ useSupabase must be used within a SupabaseProvider');
    throw new Error('useSupabase must be used within a SupabaseProvider');
  }
  console.log('🔍 useSupabase: Returning context:', { 
    user: context.user?.email, 
    loading: context.loading 
  })
  return context;
} 