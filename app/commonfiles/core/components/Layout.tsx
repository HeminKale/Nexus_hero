'use client';

import React, { useState, useEffect } from 'react';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import { useRouter } from 'next/navigation';
import AppLauncher from './AppLauncher';
import { useCurrentApp } from '../hooks/useCurrentApp';

interface LayoutProps {
  children: React.ReactNode;
}

interface TabEntry {
  id: string;
  label: string;
}

export default function Layout({ children }: LayoutProps) {
  const [showUserDropdown, setShowUserDropdown] = useState(false);
  const [visibleTabs, setVisibleTabs] = useState<TabEntry[]>([]);
  const [activeTab, setActiveTab] = useState<string>('');
  const [user, setUser] = useState<any>(null);
  const [tenantId, setTenantId] = useState<string>('');
  const supabase = createClientComponentClient();
  const router = useRouter();
  const { selectedApp, updateSelectedApp } = useCurrentApp();

  console.log('🔍 Layout component rendered');
  console.log('🔍 selectedApp:', selectedApp);
  console.log('🔍 tenantId:', tenantId);

  // Get current user and tenant
  useEffect(() => {
    const getUser = async () => {
      console.log('🔍 Getting user and tenant...');
      const { data: { user } } = await supabase.auth.getUser();
      console.log('🔍 Auth user:', user);
      setUser(user);
      
      if (user) {
        const { data: profile, error } = await supabase
          .from('system.users')  // Fixed: was tenant.users
          .select('tenant_id')
          .eq('id', user.id)
          .single();
        
        console.log('🔍 User profile:', profile);
        console.log('🔍 Profile error:', error);
        
        if (profile) {
          setTenantId(profile.tenant_id);
          console.log('🔍 Set tenantId:', profile.tenant_id);
        }
      }
    };
    
    getUser();
  }, [supabase]);

  // Fetch tabs for selected app
  useEffect(() => {
    const fetchTabs = async () => {
      if (!selectedApp || !tenantId) {
        console.log('🔍 Skipping tab fetch - selectedApp:', selectedApp, 'tenantId:', tenantId);
        return;
      }

      console.log('🔍 Fetching tabs for app:', selectedApp.id, 'tenant:', tenantId);
      try {
        const { data: tabs, error } = await supabase
          .from('tenant.tabs')
          .select('id, label')
          .eq('app_id', selectedApp.id)
          .eq('tenant_id', tenantId)
          .eq('is_active', true)
          .order('order_index');

        console.log('🔍 Tabs result:', tabs);
        console.log('🔍 Tabs error:', error);

        if (!error && tabs) {
          setVisibleTabs(tabs);
          if (tabs.length > 0 && !activeTab) {
            setActiveTab(tabs[0].id);
          }
        }
      } catch (err) {
        console.error('Error fetching tabs:', err);
      }
    };

    fetchTabs();
  }, [selectedApp, tenantId, supabase]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    // Here you can add navigation logic to different tab content
  };

  const handleSettingsClick = async () => {
    // Navigate to settings page
    router.push('/settings');
    setShowUserDropdown(false);
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    router.push('/commonfiles/features/auth');
    setShowUserDropdown(false);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showUserDropdown) {
        setShowUserDropdown(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [showUserDropdown]);

  // Render blank page when app is selected but has no tabs
  const renderMainContent = () => {
    console.log('🔍 Rendering main content');
    console.log('🔍 selectedApp:', selectedApp);
    console.log('🔍 visibleTabs:', visibleTabs);
    
    if (selectedApp && visibleTabs.length === 0) {
      console.log('🔍 Rendering no tabs message');
      return (
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <div className="text-gray-400 mb-4">
              <svg className="mx-auto h-16 w-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              {selectedApp.name}
            </h2>
            <p className="text-gray-500 mb-4">
              No tabs are configured for this application.
            </p>
            <p className="text-sm text-gray-400">
              Go to Settings → App Manager to configure tabs for this app.
            </p>
          </div>
        </div>
      );
    }
    
    console.log('🔍 Rendering children');
    return children;
  };

  console.log('🔍 Layout render - user:', user, 'tenantId:', tenantId);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Horizontal Navigation */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between px-6 py-4 space-y-4 lg:space-y-0">
          {/* App Launcher, App Name, and Navigation Tabs */}
          <div className="flex items-center space-x-4 flex-wrap gap-2 lg:gap-4">
            <AppLauncher onAppSelect={updateSelectedApp} tenantId={tenantId} />
            {selectedApp && (
              <div className="flex items-center space-x-2">
                <span className="text-gray-400">|</span>
                <span className="text-lg font-semibold text-gray-900 truncate">
                  {selectedApp.name}
                </span>
              </div>
            )}
            
            {/* Navigation Tabs - moved to left side */}
            {visibleTabs.length > 0 ? (
              visibleTabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => handleTabChange(tab.id)}
                  className={`px-3 py-2 text-sm font-medium border-b-2 whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))
            ) : selectedApp ? (
              <div className="flex items-center space-x-2 text-gray-500">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm">No tabs available for {selectedApp.name}</span>
              </div>
            ) : null}
          </div>

          {/* User Profile Dropdown */}
          <div className="relative">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowUserDropdown(!showUserDropdown);
              }}
              className="flex items-center space-x-2 p-2 rounded-md hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
            </button>

            {/* Dropdown Menu */}
            {showUserDropdown && (
              <div className="absolute right-0 mt-2 w-64 bg-white rounded-md shadow-lg border border-gray-200 z-50">
                <div className="py-2">
                  {/* User Info */}
                  <div className="px-4 py-3 border-b border-gray-100">
                    <div className="text-sm font-medium text-gray-900">
                      {(user?.user_metadata?.name || user?.email || 'User')}
                    </div>
                    <div className="text-sm text-gray-500 mt-1">
                      {user?.email}
                    </div>
                  </div>

                  {/* Menu Items */}
                  <div className="py-1">
                    <button
                      onClick={handleSettingsClick}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                    >
                      Settings
                    </button>
                    <button
                      onClick={handleSignOut}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                    >
                      Sign Out
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {renderMainContent()}
      </main>
    </div>
  );
} 