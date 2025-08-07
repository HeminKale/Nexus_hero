'use client';

import { useEffect, useState } from 'react';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import { useRouter } from 'next/navigation';
import { useSupabase } from '../commonfiles/core/providers/SupabaseProvider';
import AppLauncher from '../commonfiles/core/components/AppLauncher';

export default function Dashboard() {
  const { user, userProfile, tenant, loading } = useSupabase();
  const [dashboardLoading, setDashboardLoading] = useState(true);
  const [selectedApp, setSelectedApp] = useState<{ id: string; name: string } | null>(null);
  const supabase = createClientComponentClient();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (!user) {
        router.push('/');
        return;
      }
      setDashboardLoading(false);
    }
  }, [user, loading, router]);

  // Load selected app from localStorage
  useEffect(() => {
    const savedApp = localStorage.getItem('selected_app');
    if (savedApp) {
      try {
        setSelectedApp(JSON.parse(savedApp));
      } catch (error) {
        console.error('Error parsing saved app:', error);
      }
    }
  }, []);

  const handleAppSelect = (app: { id: string; name: string }) => {
    setSelectedApp(app);
  };

  // Debug logging
  console.log('🔍 Dashboard - tenant:', tenant);
  console.log('🔍 Dashboard - tenant?.id:', tenant?.id);
  console.log('🔍 Dashboard - userProfile:', userProfile);

  if (loading || dashboardLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900">Nexus</h1>
              
              {/* App Launcher - Always show for testing */}
              <AppLauncher 
                onAppSelect={handleAppSelect}
                tenantId={tenant?.id || 'test-tenant-id'}
              />
              
              {/* Selected App Display */}
              {selectedApp && (
                <div className="flex items-center space-x-2">
                  <span className="text-gray-400">|</span>
                  <span className="text-sm font-medium text-gray-700">
                    {selectedApp.name}
                  </span>
                </div>
              )}
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Welcome, {userProfile?.first_name || user?.email}
              </span>
              <button
                onClick={async () => {
                  await supabase.auth.signOut();
                  router.push('/');
                }}
                className="bg-red-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-red-700"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Welcome to Nexus Dashboard
            </h2>
            <p className="text-lg text-gray-600 mb-8">
              Your multi-tenant SaaS platform
            </p>
            
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 max-w-2xl mx-auto">
              <div className="text-gray-400 mb-4">
                <svg className="mx-auto h-16 w-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {selectedApp ? `${selectedApp.name} Dashboard` : 'Dashboard is Ready!'}
              </h3>
              <p className="text-gray-500 mb-4">
                {selectedApp 
                  ? `You are currently in the ${selectedApp.name} application.`
                  : 'You have successfully logged in to your account.'
                }
              </p>
              
              {/* User Info */}
              <div className="bg-gray-50 rounded-lg p-4 mb-4">
                <h4 className="font-medium text-gray-900 mb-2">Account Information</h4>
                <div className="text-sm text-gray-600 space-y-1">
                  <p><strong>Email:</strong> {user?.email}</p>
                  <p><strong>Name:</strong> {userProfile?.first_name} {userProfile?.last_name}</p>
                  <p><strong>Role:</strong> {userProfile?.role}</p>
                  <p><strong>Organization:</strong> {tenant?.name}</p>
                  <p><strong>Tenant ID:</strong> {tenant?.id || 'Not loaded'}</p>
                  {selectedApp && (
                    <p><strong>Current App:</strong> {selectedApp.name}</p>
                  )}
                </div>
              </div>
              
              <p className="text-sm text-gray-400">
                {selectedApp 
                  ? 'Use the app launcher (9-dot icon) to switch between applications.'
                  : 'Click the app launcher (9-dot icon) in the header to select an application.'
                }
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 