import React, { useState } from 'react';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import { getApiUrl } from '@/lib/api-config';

interface Applicant {
  applicationId: string;
  applicantName: string;
  emailAddress: string;
  mobileNumber: string;
  city: string;
  state: string;
  jobTitle: string;
  workAuthorization: string;
  visaStatus: string;
  createdBy: string;
  techSkills?: string;
}

export default function SearchComponent() {
  const { token } = useAuth();
  const [keywords, setKeywords] = useState('');
  const [results, setResults] = useState<Applicant[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!keywords.trim()) {
      alert('Please enter a search keyword');
      return;
    }

    setLoading(true);
    setSearched(true);

    try {
      const apiUrl = getApiUrl();
      const response = await axios.post(`${apiUrl}/search`, {
        keywords: keywords,
        jobTitle: '',
        city: '',
        state: 'United States',
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      setResults(response.data.data || []);
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setKeywords('');
    setResults([]);
    setSearched(false);
  };

  return (
    <div className="w-full">
      {/* Search Form */}
      <div className="bg-blue-600 text-white p-8 rounded-lg mb-8">
        <h1 className="text-3xl font-bold mb-6">Search Applicants</h1>
        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-2">
              Search by: Name, Email, Skills, Job Title
            </label>
            <input
              type="text"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              placeholder="e.g., Python, Engineer, Data Science, Bangalore"
              className="w-full px-4 py-3 rounded text-gray-900 text-lg"
            />
          </div>
          <div className="flex gap-4">
            <button
              type="submit"
              className="bg-green-500 hover:bg-green-600 text-white px-8 py-3 rounded font-bold transition"
            >
              🔍 SEARCH
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="bg-gray-500 hover:bg-gray-600 text-white px-8 py-3 rounded font-bold transition"
            >
              ↺ RESET
            </button>
          </div>
        </form>
      </div>

      {/* Results */}
      {searched && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4">
            {loading ? '⏳ Searching...' : `Results: ${results.length} applicant(s) found`}
          </h2>

          {loading ? (
            <div className="text-center py-8">
              <p className="text-gray-600">Searching database...</p>
            </div>
          ) : results.length > 0 ? (
            /* ── horizontal scroll wrapper ── */
            <div className="w-full overflow-x-auto rounded-lg shadow border border-gray-200">
              <table className="min-w-full bg-white">
                <thead className="bg-gray-100 border-b-2">
                  <tr>
                    <th className="p-4 text-left font-bold whitespace-nowrap">Name</th>
                    <th className="p-4 text-left font-bold whitespace-nowrap">Email</th>
                    <th className="p-4 text-left font-bold whitespace-nowrap">Phone</th>
                    <th className="p-4 text-left font-bold whitespace-nowrap">Location</th>
                    <th className="p-4 text-left font-bold whitespace-nowrap">Job Title</th>
                    <th className="p-4 text-left font-bold whitespace-nowrap">Skills</th>
                    <th className="p-4 text-left font-bold whitespace-nowrap">Work Auth</th>
                    <th className="p-4 text-left font-bold whitespace-nowrap">Visa Status</th>
                    <th className="p-4 text-left font-bold whitespace-nowrap">Uploaded By</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((applicant) => (
                    <tr
                      key={applicant.applicationId}
                      className="border-b hover:bg-blue-50 transition"
                    >
                      <td className="p-4 font-semibold text-blue-600 whitespace-nowrap">
                        {applicant.applicantName}
                      </td>
                      <td className="p-4 text-sm whitespace-nowrap">{applicant.emailAddress}</td>
                      <td className="p-4 text-sm whitespace-nowrap">{applicant.mobileNumber}</td>
                      <td className="p-4 text-sm whitespace-nowrap">
                        {[applicant.city, applicant.state].filter(Boolean).join(', ') || '—'}
                      </td>
                      <td className="p-4 text-sm whitespace-nowrap">{applicant.jobTitle || '—'}</td>
                      <td className="p-4 text-sm max-w-[180px]">{applicant.techSkills || '—'}</td>
                      <td className="p-4 text-sm text-green-600 font-semibold whitespace-nowrap">
                        {applicant.workAuthorization || '—'}
                      </td>
                      <td className="p-4 text-sm text-indigo-600 font-semibold whitespace-nowrap">
                        {applicant.visaStatus || '—'}
                      </td>
                      <td className="p-4 text-sm text-orange-600 font-semibold whitespace-nowrap">
                        {applicant.createdBy || '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <p className="text-gray-600 text-lg">❌ No results found for "{keywords}"</p>
              <p className="text-gray-500 mt-2">Try different keywords</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}