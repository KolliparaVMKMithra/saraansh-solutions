import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '@/context/AuthContext';
import type { ReactNode } from 'react';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();
  const { user, logout, isAuthenticated } = useAuth();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  // Don't show layout on login/signup pages
  if (router.pathname === '/login' || router.pathname === '/signup') {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-blue-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="text-2xl font-bold">💼 Applicant Database</div>
            <div className="flex gap-8 items-center">
              {isAuthenticated ? (
                <>
                  <Link href="/" className="hover:bg-blue-700 px-4 py-2 rounded transition font-semibold">
                    🏠 Home
                  </Link>
                  <Link href="/upload" className="hover:bg-blue-700 px-4 py-2 rounded transition font-semibold">
                    📤 Upload
                  </Link>
                  <Link href="/search" className="hover:bg-blue-700 px-4 py-2 rounded transition font-semibold">
                    🔍 Search
                  </Link>
                  <Link href="/resumes" className="hover:bg-blue-700 px-4 py-2 rounded transition font-semibold">
                    📋 Resumes
                  </Link>
                  <div className="border-l border-blue-400 pl-8 flex items-center gap-4">
                    <span className="text-sm">👤 {user?.fullName}</span>
                    <button
                      onClick={handleLogout}
                      className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded transition font-semibold text-sm"
                    >
                      🚪 Logout
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <Link href="/login" className="hover:bg-blue-700 px-4 py-2 rounded transition font-semibold">
                    🔐 Login
                  </Link>
                  <Link href="/signup" className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded transition font-semibold">
                    ✍️ Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white mt-12 py-8">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2026 Applicant Database System. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

