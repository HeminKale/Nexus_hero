'use client';

import { useEffect, useState } from 'react';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import { useRouter } from 'next/navigation';
import Layout from '../commonfiles/core/components/Layout';

interface App {
  id: string;
  name: string;
  description: string;
  is_active: boolean;
}

interface Tab {
  id: string;
  label: string;
  app_id: string;
  is_active: boolean;
  order_index: number;
}

export default function Settings() {
  const [apps, setApps] = useState<App[]>([]);
  const [tabs, setTabs] = useState<Tab[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedApp, setSelectedApp] = useState<string>('');
  const supabase = createClientComponentClient();
  const router = useRouter();

  useEffect(() => {
    const checkUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        router.push('/commonfiles/features/auth');
        return;
      }
      loadApps();
    };

    checkUser();
  }, [supabase, router]);

  const loadApps = async () => {
    try {
      const { data, error } = await supabase
        .from('tenant.apps')
        .select('*')
        .order('name');
      
      if (error) throw error;
      setApps(data || []);
      setLoading(false);
    } catch (err) {
      console.error('Error loading apps:', err);
      setLoading(false);
    }
  };

  const loadTabs = async (appId: string) => {
    try {
      const { data, error } = await supabase
        .from('tenant.tabs')
        .select('*')
        .eq('app_id', appId)
        .order('order_index');
      
      if (error) throw error;
      setTabs(data || []);
    } catch (err) {
      console.error('Error loading tabs:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <Layout>
      <div className="p-6">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
            <p className="text-gray-600">Manage your applications and tabs</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* App Manager */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">App Manager</h2>
              
              {apps.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-gray-400 mb-3">
                    <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <h3 className="text-sm font-medium text-gray-900 mb-1">No applications</h3>
                  <p className="text-xs text-gray-500">Create your first application to get started.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {apps.map((app) => (
                    <div key={app.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                          <span className="text-blue-600 font-medium text-sm">
                            {app.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <h3 className="font-medium text-gray-900">{app.name}</h3>
                          <p className="text-sm text-gray-500">{app.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          app.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {app.is_active ? 'Active' : 'Inactive'}
                        </span>
                        <button
                          onClick={() => setSelectedApp(app.id)}
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                        >
                          Manage
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Tab Manager */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Tab Manager</h2>
              
              {!selectedApp ? (
                <div className="text-center py-8">
                  <div className="text-gray-400 mb-3">
                    <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                    </svg>
                  </div>
                  <h3 className="text-sm font-medium text-gray-900 mb-1">Select an app</h3>
                  <p className="text-xs text-gray-500">Choose an app from the left to manage its tabs.</p>
                </div>
              ) : (
                <div>
                  <div className="mb-4">
                    <h3 className="font-medium text-gray-900">
                      Tabs for {apps.find(a => a.id === selectedApp)?.name}
                    </h3>
                  </div>
                  
                  {tabs.length === 0 ? (
                    <div className="text-center py-6">
                      <p className="text-sm text-gray-500">No tabs configured for this app.</p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {tabs.map((tab) => (
                        <div key={tab.id} className="flex items-center justify-between p-2 border border-gray-200 rounded">
                          <span className="text-sm text-gray-900">{tab.label}</span>
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            tab.is_active 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {tab.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
} 