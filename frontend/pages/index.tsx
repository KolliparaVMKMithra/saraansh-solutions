import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '@/context/AuthContext';
import { getApiUrl } from '@/lib/api-config';
import Layout from '@/components/Layout';
import Link from 'next/link';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, isLoading, token } = useAuth();
  const [candidateCount, setCandidateCount] = useState(0);
  const [loadingCount, setLoadingCount] = useState(true);

  // Redirect to signup if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/signup');
    }
  }, [isAuthenticated, isLoading, router]);

  // Fetch candidate count
  useEffect(() => {
    const fetchCandidateCount = async () => {
      if (isAuthenticated && token) {
        try {
          const apiUrl = getApiUrl();
          const response = await fetch(`${apiUrl}/applicants?skip=0&limit=100000`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (response.ok) {
            const data = await response.json();
            setCandidateCount(data.count || 0);
          }
        } catch (error) {
          console.error('Error fetching candidate count:', error);
          setCandidateCount(0);
        } finally {
          setLoadingCount(false);
        }
      }
    };

    fetchCandidateCount();
  }, [isAuthenticated, token]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-12">
          <p className="text-lg text-gray-600">Loading...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="text-center py-12">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Welcome to Applicant Database System
        </h1>
        <p className="text-xl text-gray-600 mb-12">
          Find and manage the perfect candidate quickly and easily
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Upload Card */}
          <Link href="/upload">
            <div className="bg-blue-500 hover:bg-blue-600 text-white p-8 rounded-lg cursor-pointer transition transform hover:scale-105 shadow-lg">
              <div className="text-5xl mb-4">📤</div>
              <h2 className="text-xl font-bold mb-2">Upload Resume</h2>
              <p className="text-blue-100">Add new applicants</p>
            </div>
          </Link>

          {/* Search Card */}
          <Link href="/search">
            <div className="bg-green-500 hover:bg-green-600 text-white p-8 rounded-lg cursor-pointer transition transform hover:scale-105 shadow-lg">
              <div className="text-5xl mb-4">🔍</div>
              <h2 className="text-xl font-bold mb-2">Search</h2>
              <p className="text-green-100">Find candidates by skills</p>
            </div>
          </Link>

          {/* View All Card */}
          <Link href="/resumes">
            <div className="bg-purple-500 hover:bg-purple-600 text-white p-8 rounded-lg cursor-pointer transition transform hover:scale-105 shadow-lg">
              <div className="text-5xl mb-4">📋</div>
              <h2 className="text-xl font-bold mb-2">View All</h2>
              <p className="text-purple-100">Browse all resumes</p>
            </div>
          </Link>

          {/* Stats Card */}
          <div className="bg-gray-700 text-white p-8 rounded-lg shadow-lg">
            <div className="text-5xl mb-4">📊</div>
            <h2 className="text-xl font-bold mb-2">Database</h2>
            <p className="text-gray-300">
              {loadingCount ? 'Loading...' : `${candidateCount} candidate${candidateCount !== 1 ? 's' : ''} loaded`}
            </p>
          </div>
        </div>

        {/* Quick Tips */}
        <div className="mt-16 bg-blue-50 rounded-lg p-8 max-w-2xl mx-auto">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">Quick Tips</h3>
          <div className="text-left space-y-3">
            <p className="flex items-center gap-3">
              <span className="text-2xl">✨</span>
              <span>Search by keywords like "Python", "Engineer", "Bangalore"</span>
            </p>
            <p className="flex items-center gap-3">
              <span className="text-2xl">📂</span>
              <span>View complete candidate profile by clicking "View" button</span>
            </p>
            <p className="flex items-center gap-3">
              <span className="text-2xl">⚡</span>
              <span>Upload new resumes instantly (PDF or DOCX)</span>
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
}

