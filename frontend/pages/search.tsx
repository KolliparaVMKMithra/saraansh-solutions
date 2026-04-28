import React from 'react';
import Layout from '@/components/Layout';
import SearchComponent from '@/components/Search';
import { ProtectedRoute } from '@/components/ProtectedRoute';

export default function SearchPage() {
  return (
    <ProtectedRoute>
      <Layout>
        <SearchComponent />
      </Layout>
    </ProtectedRoute>
  );
}
