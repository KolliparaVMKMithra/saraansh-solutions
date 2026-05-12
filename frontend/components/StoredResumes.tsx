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
  visaStatus: string;
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

// Tooltip wrapper
function Tooltip({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="relative group inline-block">
      {children}
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
        {label}
      </div>
    </div>
  );
}

export default function StoredResumes() {
  const { token } = useAuth();
  const [applicants, setApplicants] = useState<Applicant[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedApplicant, setSelectedApplicant] = useState<SelectedApplicant | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<{ id: string; name: string } | null>(null);
  const itemsPerPage = 10;

  useEffect(() => {
    const fetchApplicants = async () => {
      try {
        const apiUrl = getApiUrl();
        const response = await axios.get(`${apiUrl}/applicants?limit=100`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setApplicants(response.data.data || []);
      } catch (error) {
        console.error('Failed to fetch applicants:', error);
      } finally {
        setLoading(false);
      }
    };
    if (token) fetchApplicants();
  }, [token]);

  const handleDownloadResume = (applicantId: string) => {
    const apiUrl = getApiUrl();
    window.open(`${apiUrl}/applicants/${applicantId}/download?token=${token}`, '_blank');
  };

  const handleSelectApplicant = async (applicantId: string) => {
    try {
      const apiUrl = getApiUrl();
      const response = await axios.get(`${apiUrl}/applicants/${applicantId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setSelectedApplicant(response.data.data || null);
    } catch (error) {
      console.error('Failed to fetch applicant details:', error);
    }
  };

  const handleDeleteResume = async (applicantId: string) => {
    setDeletingId(applicantId);
    try {
      const apiUrl = getApiUrl();
      const response = await axios.delete(`${apiUrl}/applicants/${applicantId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.data.success) {
        setApplicants(prev => prev.filter(a => a.applicationId !== applicantId));
        if (selectedApplicant?.applicationId === applicantId) setSelectedApplicant(null);
      }
    } catch (error) {
      console.error('Failed to delete resume:', error);
    } finally {
      setDeletingId(null);
      setConfirmDelete(null);
    }
  };

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentApplicants = applicants.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(applicants.length / itemsPerPage);

  // ── Detail View ──────────────────────────────────────────────
  if (selectedApplicant) {
    return (
      <div className="w-full">
        <button
          onClick={() => setSelectedApplicant(null)}
          className="mb-6 flex items-center gap-2 text-blue-600 hover:text-blue-800 font-semibold transition"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to List
        </button>

        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-1 bg-white rounded-xl shadow-lg p-6">
            <h1 className="text-2xl font-bold text-blue-600 mb-6 break-words">
              {selectedApplicant.applicantName}
            </h1>
            <div className="space-y-4 mb-6">
              {[
                { label: 'Email', value: selectedApplicant.emailAddress, color: 'blue' },
                { label: 'Phone', value: selectedApplicant.mobileNumber, color: 'blue' },
                { label: 'Location', value: `${selectedApplicant.city}, ${selectedApplicant.state}`, color: 'blue' },
                { label: 'Job Title', value: selectedApplicant.jobTitle, color: 'green' },
                { label: 'Work Auth', value: selectedApplicant.workAuthorization, color: 'purple' },
                { label: 'Visa Status', value: selectedApplicant.visaStatus, color: 'indigo' },
              ].map(({ label, value, color }) => (
                <div key={label} className={`bg-${color}-50 rounded-lg p-3`}>
                  <label className="text-xs font-semibold text-gray-500 uppercase">{label}</label>
                  <p className={`text-sm font-medium text-${color}-800 mt-1 break-all`}>{value || '—'}</p>
                </div>
              ))}
            </div>

            <div className="border-t pt-4 text-xs space-y-2 text-gray-500 mb-6">
              <p><span className="font-semibold">Status:</span> {selectedApplicant.applicantStatus}</p>
              <p><span className="font-semibold">Source:</span> {selectedApplicant.source}</p>
              <p><span className="font-semibold">Added:</span> {new Date(selectedApplicant.createdOn).toLocaleDateString()}</p>
            </div>

            {selectedApplicant.techSkills && (
              <div className="bg-yellow-50 rounded-lg p-4 mb-6">
                <label className="text-xs font-semibold text-gray-500 uppercase block mb-3">Skills</label>
                <div className="flex flex-wrap gap-2">
                  {selectedApplicant.techSkills.split(', ').map((skill, idx) => (
                    <span key={idx} className="bg-yellow-200 text-yellow-900 px-2 py-1 rounded-full text-xs font-semibold">
                      {skill.trim()}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Action buttons in detail view */}
            <div className="flex flex-col gap-2">
              {selectedApplicant.blobUrl && (
                <button
                  onClick={() => handleDownloadResume(selectedApplicant.applicationId)}
                  className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-lg font-semibold transition text-sm"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  View Resume
                </button>
              )}
              <button
                onClick={() => setConfirmDelete({ id: selectedApplicant.applicationId, name: selectedApplicant.applicantName })}
                className="w-full flex items-center justify-center gap-2 bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 px-4 py-2.5 rounded-lg font-semibold transition text-sm"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete Resume
              </button>
            </div>
          </div>

          <div className="col-span-2">
            {selectedApplicant.resumeText ? (
              <div className="bg-white rounded-xl shadow-lg p-6 h-full flex flex-col">
                <div className="mb-4">
                  <h2 className="text-xl font-bold">📄 Full Resume</h2>
                  <p className="text-sm text-gray-500">Complete extracted resume text</p>
                </div>
                <div className="flex-1 bg-gray-50 border border-gray-200 rounded-lg p-5 overflow-y-auto">
                  <pre className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap font-sans">
                    {selectedApplicant.resumeText}
                  </pre>
                </div>
                <p className="mt-3 text-xs text-gray-400 text-center">↕ Scroll to view full resume</p>
              </div>
            ) : (
              <div className="bg-white rounded-xl shadow-lg p-6 h-full flex items-center justify-center">
                <p className="text-gray-400 text-lg">No resume text available</p>
              </div>
            )}
          </div>
        </div>

        {/* Delete confirm modal */}
        {confirmDelete && (
          <DeleteModal
            name={confirmDelete.name}
            onConfirm={() => handleDeleteResume(confirmDelete.id)}
            onCancel={() => setConfirmDelete(null)}
            loading={deletingId === confirmDelete.id}
          />
        )}
      </div>
    );
  }

  // ── List View ────────────────────────────────────────────────
  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">📋 Stored Resumes</h1>
          <p className="text-gray-500 mt-1">
            <span className="font-bold text-blue-600">{applicants.length}</span> applicants total
          </p>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-16">
          <div className="text-4xl mb-3">⏳</div>
          <p className="text-gray-500">Loading applicants...</p>
        </div>
      ) : applicants.length === 0 ? (
        <div className="text-center py-16 bg-gray-50 rounded-xl border border-gray-200">
          <div className="text-4xl mb-3">📭</div>
          <p className="text-gray-500">No applicants found</p>
        </div>
      ) : (
        <>
          <div className="bg-white rounded-xl shadow overflow-hidden border border-gray-100">
            <table className="w-full">
              <thead className="bg-blue-600 text-white">
                <tr>
                  <th className="p-4 text-left font-semibold text-sm">Name</th>
                  <th className="p-4 text-left font-semibold text-sm">Email</th>
                  <th className="p-4 text-left font-semibold text-sm">Phone</th>
                  <th className="p-4 text-left font-semibold text-sm">Location</th>
                  <th className="p-4 text-left font-semibold text-sm">Job Title</th>
                  <th className="p-4 text-left font-semibold text-sm">Skills</th>
                  <th className="p-4 text-left font-semibold text-sm">Visa Status</th>
                  <th className="p-4 text-center font-semibold text-sm">Actions</th>
                </tr>
              </thead>
              <tbody>
                {currentApplicants.map((applicant, idx) => (
                  <tr
                    key={applicant.applicationId}
                    className={`border-b hover:bg-blue-50 transition ${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'}`}
                  >
                    <td className="p-4">
                      <span
                        className="font-semibold text-blue-600 hover:text-blue-800 cursor-pointer hover:underline"
                        onClick={() => handleSelectApplicant(applicant.applicationId)}
                      >
                        {applicant.applicantName}
                      </span>
                    </td>
                    <td className="p-4 text-sm text-gray-600">{applicant.emailAddress}</td>
                    <td className="p-4 text-sm text-gray-600">{applicant.mobileNumber}</td>
                    <td className="p-4 text-sm text-gray-600">
                      {[applicant.city, applicant.state].filter(Boolean).join(', ') || '—'}
                    </td>
                    <td className="p-4 text-sm text-gray-700">{applicant.jobTitle || '—'}</td>
                    <td className="p-4 text-sm text-gray-600">
                      {applicant.techSkills
                        ? applicant.techSkills.length > 40
                          ? `${applicant.techSkills.slice(0, 40)}…`
                          : applicant.techSkills
                        : '—'}
                    </td>
                    <td className="p-4 text-sm font-medium text-indigo-600">
                      {applicant.visaStatus || '—'}
                    </td>

                    {/* ── Cleaner Action Icons ── */}
                    <td className="p-4">
                      <div className="flex items-center justify-center gap-1">

                        {/* View Profile */}
                        <Tooltip label="View Profile">
                          <button
                            onClick={() => handleSelectApplicant(applicant.applicationId)}
                            className="w-9 h-9 flex items-center justify-center rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-600 transition"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                            </svg>
                          </button>
                        </Tooltip>

                        {/* Download Resume */}
                        <Tooltip label="View Resume">
                          <button
                            onClick={() => handleDownloadResume(applicant.applicationId)}
                            className="w-9 h-9 flex items-center justify-center rounded-lg bg-green-50 hover:bg-green-100 text-green-600 transition"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                          </button>
                        </Tooltip>

                        {/* Delete */}
                        <Tooltip label="Delete">
                          <button
                            onClick={() => setConfirmDelete({ id: applicant.applicationId, name: applicant.applicantName })}
                            className="w-9 h-9 flex items-center justify-center rounded-lg bg-red-50 hover:bg-red-100 text-red-500 transition"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </Tooltip>

                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="mt-6 flex justify-between items-center">
            <p className="text-sm text-gray-500">
              Showing {indexOfFirstItem + 1}–{Math.min(indexOfLastItem, applicants.length)} of {applicants.length}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 disabled:opacity-40 text-gray-700 font-semibold text-sm transition"
              >
                ← Prev
              </button>
              <span className="px-4 py-2 text-sm font-semibold text-gray-700">
                {currentPage} / {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 disabled:opacity-40 text-gray-700 font-semibold text-sm transition"
              >
                Next →
              </button>
            </div>
          </div>
        </>
      )}

      {/* Delete confirmation modal */}
      {confirmDelete && (
        <DeleteModal
          name={confirmDelete.name}
          onConfirm={() => handleDeleteResume(confirmDelete.id)}
          onCancel={() => setConfirmDelete(null)}
          loading={deletingId === confirmDelete.id}
        />
      )}
    </div>
  );
}

// ── Delete Confirmation Modal ────────────────────────────────
function DeleteModal({
  name,
  onConfirm,
  onCancel,
  loading,
}: {
  name: string;
  onConfirm: () => void;
  onCancel: () => void;
  loading: boolean;
}) {
  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-sm w-full mx-4 animate-fade-in">
        <div className="w-14 h-14 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-7 h-7 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </div>
        <h3 className="text-lg font-bold text-gray-900 text-center mb-2">Delete Resume?</h3>
        <p className="text-sm text-gray-500 text-center mb-6">
          This will permanently delete <span className="font-semibold text-gray-800">{name}</span>'s resume. This cannot be undone.
        </p>
        <div className="flex gap-3">
          <button
            onClick={onCancel}
            disabled={loading}
            className="flex-1 px-4 py-2.5 rounded-xl border border-gray-200 text-gray-700 font-semibold hover:bg-gray-50 transition text-sm"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            className="flex-1 px-4 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-semibold transition text-sm disabled:opacity-60"
          >
            {loading ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  );
}