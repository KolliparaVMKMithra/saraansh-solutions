import React, { useEffect, useState } from 'react';
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
  createdOn: string;
  techSkills?: string;
}

interface SelectedApplicant extends Applicant {
  applicantStatus: string;
  ownership: string;
  source: string;
  createdBy: string;
  resumeText?: string;
  blobUrl?: string;
}

export default function StoredResumes() {
  const { token } = useAuth();
  const [applicants, setApplicants] = useState<Applicant[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedApplicant, setSelectedApplicant] = useState<SelectedApplicant | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    const fetchApplicants = async () => {
      try {
        const apiUrl = getApiUrl();
        const response = await axios.get(`${apiUrl}/applicants?limit=100`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        setApplicants(response.data.data || []);
      } catch (error) {
        console.error('Failed to fetch applicants:', error);
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchApplicants();
    }
  }, [token]);

  const handleDownloadResume = (applicantId: string) => {
    const apiUrl = getApiUrl();
    const downloadUrl = `${apiUrl}/applicants/${applicantId}/download?token=${token}`;
    window.open(downloadUrl, '_blank');
  };

  const handleSelectApplicant = async (applicantId: string) => {
    try {
      const apiUrl = getApiUrl();
      const response = await axios.get(`${apiUrl}/applicants/${applicantId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setSelectedApplicant(response.data.data || null);
    } catch (error) {
      console.error('Failed to fetch applicant details:', error);
    }
  };

  const handleDeleteResume = async (applicantId: string, applicantName: string) => {
    if (!window.confirm(`Are you sure you want to delete ${applicantName}'s resume? This action cannot be undone.`)) {
      return;
    }
    
    try {
      const apiUrl = getApiUrl();
      const response = await axios.delete(`${apiUrl}/applicants/${applicantId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.data.success) {
        // Remove from list
        setApplicants(applicants.filter(a => a.applicationId !== applicantId));
        // Close detail view if open
        if (selectedApplicant?.applicationId === applicantId) {
          setSelectedApplicant(null);
        }
        alert('Resume deleted successfully');
      } else {
        alert('Failed to delete resume: ' + response.data.message);
      }
    } catch (error) {
      console.error('Failed to delete resume:', error);
      alert('Failed to delete resume');
    }
  };

  // Pagination
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentApplicants = applicants.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(applicants.length / itemsPerPage);

  if (selectedApplicant) {
    return (
      <div className="w-full">
        {/* Back Button */}
        <button
          onClick={() => setSelectedApplicant(null)}
          className="mb-6 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded font-semibold transition"
        >
          ← Back to List
        </button>

        {/* Main Container */}
        <div className="grid grid-cols-3 gap-6">
          
          {/* LEFT SIDEBAR - Extracted Data */}
          <div className="col-span-1 bg-white rounded-lg shadow-lg p-6">
            <h1 className="text-2xl font-bold text-blue-600 mb-6 break-words">
              {selectedApplicant.applicantName}
            </h1>

            {/* Key Information */}
            <div className="space-y-4 mb-6">
              <div className="bg-blue-50 rounded p-3">
                <label className="text-xs font-semibold text-gray-600 uppercase">Email</label>
                <p className="text-sm text-gray-900 break-all mt-1">{selectedApplicant.emailAddress}</p>
              </div>

              <div className="bg-blue-50 rounded p-3">
                <label className="text-xs font-semibold text-gray-600 uppercase">Phone</label>
                <p className="text-sm text-gray-900 mt-1">{selectedApplicant.mobileNumber}</p>
              </div>

              <div className="bg-blue-50 rounded p-3">
                <label className="text-xs font-semibold text-gray-600 uppercase">Location</label>
                <p className="text-sm text-gray-900 mt-1">
                  {selectedApplicant.city}, {selectedApplicant.state}
                </p>
              </div>

              <div className="bg-green-50 rounded p-3">
                <label className="text-xs font-semibold text-gray-600 uppercase">Job Title</label>
                <p className="text-sm font-semibold text-green-700 mt-1">{selectedApplicant.jobTitle}</p>
              </div>

              <div className="bg-purple-50 rounded p-3">
                <label className="text-xs font-semibold text-gray-600 uppercase">Work Auth</label>
                <p className="text-sm font-semibold text-purple-700 mt-1">{selectedApplicant.workAuthorization}</p>
              </div>
            </div>

            {/* Metadata */}
            <div className="border-t pt-4 text-xs space-y-2">
              <div>
                <span className="text-gray-500 font-semibold">Status:</span>
                <span className="ml-2 text-gray-700">{selectedApplicant.applicantStatus}</span>
              </div>
              <div>
                <span className="text-gray-500 font-semibold">Source:</span>
                <span className="ml-2 text-gray-700">{selectedApplicant.source}</span>
              </div>
              <div>
                <span className="text-gray-500 font-semibold">Added:</span>
                <span className="ml-2 text-gray-700">
                  {new Date(selectedApplicant.createdOn).toLocaleDateString()}
                </span>
              </div>
            </div>

            {/* Skills Box */}
            {selectedApplicant.techSkills && (
              <div className="mt-6 bg-yellow-50 rounded p-4">
                <label className="text-xs font-semibold text-gray-600 uppercase block mb-3">Extracted Skills</label>
                <div className="flex flex-wrap gap-2">
                  {selectedApplicant.techSkills.split(', ').map((skill, idx) => (
                    <span
                      key={idx}
                      className="bg-yellow-200 text-yellow-900 px-3 py-1 rounded-full text-xs font-semibold"
                    >
                      {skill.trim()}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <button className="w-full mt-6 bg-green-600 hover:bg-green-700 text-white px-4 py-3 rounded font-semibold transition text-sm">
              📧 Send Email
            </button>
            
            {selectedApplicant.blobUrl && (
              <button 
                onClick={() => handleDownloadResume(selectedApplicant.applicationId)}
                className="w-full mt-3 bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded font-semibold transition text-sm"
              >
                📄 View Full Resume
              </button>
            )}

            <button
              onClick={() => handleDeleteResume(selectedApplicant.applicationId, selectedApplicant.applicantName)}
              className="w-full mt-3 bg-red-600 hover:bg-red-700 text-white px-4 py-3 rounded font-semibold transition text-sm"
            >
              🗑️ Delete Resume
            </button>
          </div>

          {/* RIGHT CONTENT - Full Resume Text */}
          <div className="col-span-2">
            {selectedApplicant.resumeText ? (
              <div className="bg-white rounded-lg shadow-lg p-6 h-full flex flex-col">
                <div className="mb-4">
                  <h2 className="text-2xl font-bold mb-2">📄 Full Resume</h2>
                  <p className="text-sm text-gray-600">Complete extracted resume text</p>
                </div>

                <div className="flex-1 bg-gray-50 border-2 border-gray-200 rounded-lg p-5 overflow-y-auto">
                  <div className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap font-sans">
                    {selectedApplicant.resumeText}
                  </div>
                </div>

                <div className="mt-4 text-xs text-gray-500 text-center">
                  ↕️ Scroll to view full resume
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-lg p-6 h-full flex items-center justify-center">
                <p className="text-gray-500 text-lg">No resume text available</p>
              </div>
            )}
          </div>

        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      <h1 className="text-3xl font-bold mb-6">📋 Stored Resumes</h1>
      <p className="text-gray-600 mb-6">
        Total Applicants: <span className="font-bold text-blue-600">{applicants.length}</span>
      </p>

      {loading ? (
        <div className="text-center py-12">
          <p className="text-gray-600 text-lg">⏳ Loading applicants...</p>
        </div>
      ) : applicants.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-600 text-lg">No applicants found</p>
        </div>
      ) : (
        <>
          {/* Applicants Table */}
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="w-full">
              <thead className="bg-blue-600 text-white">
                <tr>
                  <th className="p-4 text-left font-semibold">Name</th>
                  <th className="p-4 text-left font-semibold">Email</th>
                  <th className="p-4 text-left font-semibold">Phone</th>
                  <th className="p-4 text-left font-semibold">Location</th>
                  <th className="p-4 text-left font-semibold">Job Title</th>
                  <th className="p-4 text-left font-semibold">Skills</th>
                  <th className="p-4 text-center font-semibold">Action</th>
                </tr>
              </thead>
              <tbody>
                {currentApplicants.map((applicant) => (
                  <tr key={applicant.applicationId} className="border-b hover:bg-blue-50 transition">
                    <td className="p-4 font-semibold text-blue-600">
                      {applicant.applicantName}
                    </td>
                    <td className="p-4 text-sm">{applicant.emailAddress}</td>
                    <td className="p-4 text-sm">{applicant.mobileNumber}</td>
                    <td className="p-4 text-sm">
                      {applicant.city}, {applicant.state}
                    </td>
                    <td className="p-4 text-sm">{applicant.jobTitle}</td>
                    <td className="p-4 text-sm text-gray-700">
                      {applicant.techSkills ? (applicant.techSkills.length > 40 ? `${applicant.techSkills.slice(0, 40)}...` : applicant.techSkills) : '—'}
                    </td>
                    <td className="p-4 text-center space-x-2">
                      <button
                        onClick={() => handleSelectApplicant(applicant.applicationId)}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm font-semibold transition"
                      >
                        View
                      </button>
                      <button
                        onClick={() => handleDownloadResume(applicant.applicationId)}
                        className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm font-semibold transition"
                      >
                        Resume
                      </button>
                      <button
                        onClick={() => handleDeleteResume(applicant.applicationId, applicant.applicantName)}
                        className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm font-semibold transition"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="mt-6 flex justify-between items-center">
            <div className="text-gray-600">
              Page <span className="font-bold">{currentPage}</span> of{' '}
              <span className="font-bold">{totalPages}</span>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="bg-gray-300 hover:bg-gray-400 disabled:opacity-50 text-gray-900 px-4 py-2 rounded font-semibold transition"
              >
                ← Previous
              </button>

              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="bg-gray-300 hover:bg-gray-400 disabled:opacity-50 text-gray-900 px-4 py-2 rounded font-semibold transition"
              >
                Next →
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
