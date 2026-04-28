import React from 'react';
import Layout from '@/components/Layout';
import UploadComponent from '@/components/Upload';
import { ProtectedRoute } from '@/components/ProtectedRoute';

export default function UploadPage() {
  return (
    <ProtectedRoute>
      <Layout>
        <UploadComponent />
      </Layout>
    </ProtectedRoute>
  );
}
