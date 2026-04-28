import React from 'react';
import Layout from '@/components/Layout';
import StoredResumes from '@/components/StoredResumes';
import { ProtectedRoute } from '@/components/ProtectedRoute';

export default function ResumesPage() {
  return (
    <ProtectedRoute>
      <Layout>
        <StoredResumes />
      </Layout>
    </ProtectedRoute>
  );
}
