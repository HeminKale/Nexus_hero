import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './commonfiles/core/globals.css'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { SupabaseProvider } from './commonfiles/core/providers/SupabaseProvider'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: process.env.NEXT_PUBLIC_APP_NAME || 'Craft App',
  description: process.env.NEXT_PUBLIC_APP_DESCRIPTION || 'Multi-tenant SaaS platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <SupabaseProvider>
          {children}
          <Toaster position="top-right" />
        </SupabaseProvider>
      </body>
    </html>
  )
} 