'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';
import type { PerformanceSummary } from '@/lib/api-client';
import { formatCurrency, formatPercentage, getDateRangePresets } from '@/lib/utils';

export default function DashboardPage() {
  const [summary, setSummary] = useState<PerformanceSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<{ start: string; end: string }>(
    getDateRangePresets()['Last 30 Days']
  );

  const profileId = process.env.NEXT_PUBLIC_DEFAULT_PROFILE_ID || 'profile_123';

  useEffect(() => {
    loadDashboardData();
  }, [dateRange]);

  async function loadDashboardData() {
    try {
      setLoading(true);
      setError(null);

      const data = await apiClient.getPerformanceSummary(
        profileId,
        dateRange.start,
        dateRange.end
      );

      setSummary(data);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h2 className="text-red-800 font-semibold text-lg mb-2">Error Loading Dashboard</h2>
          <p className="text-red-600">{error}</p>
          <button
            onClick={loadDashboardData}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-gray-600">No data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-black">Performance Dashboard</h1>
          <p className="text-gray-600 mt-1">
            {dateRange.start} to {dateRange.end}
          </p>
        </div>

        {/* Date Range Selector */}
        <select
          value={JSON.stringify(dateRange)}
          onChange={(e) => setDateRange(JSON.parse(e.target.value))}
          className="px-4 py-2 border border-gray-300 rounded-md bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-yellow-400"
        >
          {Object.entries(getDateRangePresets()).map(([label, range]) => (
            <option key={label} value={JSON.stringify(range)}>
              {label}
            </option>
          ))}
        </select>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Spend */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Spend</p>
              <p className="text-2xl font-bold text-black mt-2">
                {formatCurrency(summary.total_spend)}
              </p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
              <svg
                className="w-6 h-6 text-yellow-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
          </div>
        </div>

        {/* Total Sales */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Sales</p>
              <p className="text-2xl font-bold text-black mt-2">
                {formatCurrency(summary.total_sales)}
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <svg
                className="w-6 h-6 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                />
              </svg>
            </div>
          </div>
        </div>

        {/* ACOS */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">ACOS</p>
              <p className="text-2xl font-bold text-black mt-2">
                {formatPercentage(summary.avg_acos)}
              </p>
              <p className="text-xs text-gray-500 mt-1">Advertising Cost of Sales</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <svg
                className="w-6 h-6 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
          </div>
        </div>

        {/* ROAS */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">ROAS</p>
              <p className="text-2xl font-bold text-black mt-2">
                {summary.avg_roas || '0.00'}
              </p>
              <p className="text-xs text-gray-500 mt-1">Return on Ad Spend</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
              <svg
                className="w-6 h-6 text-purple-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"
                />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Orders */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <p className="text-sm font-medium text-gray-600">Total Orders</p>
          <p className="text-3xl font-bold text-black mt-2">{summary.total_orders}</p>
        </div>

        {/* Clicks */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <p className="text-sm font-medium text-gray-600">Total Clicks</p>
          <p className="text-3xl font-bold text-black mt-2">{summary.total_clicks}</p>
          <p className="text-xs text-gray-500 mt-1">
            CTR: {formatPercentage(summary.avg_ctr)}
          </p>
        </div>

        {/* Keywords */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <p className="text-sm font-medium text-gray-600">Active Keywords</p>
          <p className="text-3xl font-bold text-black mt-2">{summary.keyword_count}</p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-black mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="px-4 py-3 bg-yellow-400 text-black font-medium rounded-md hover:bg-yellow-500 transition-colors">
            View Campaigns
          </button>
          <button className="px-4 py-3 bg-black text-yellow-400 font-medium rounded-md hover:bg-gray-900 transition-colors">
            Import Data
          </button>
          <button className="px-4 py-3 border border-gray-300 text-black font-medium rounded-md hover:bg-gray-50 transition-colors">
            Get Recommendations
          </button>
        </div>
      </div>
    </div>
  );
}
