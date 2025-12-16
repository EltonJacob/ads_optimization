'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';
import type {
  PerformanceSummary,
  TrendResponse,
  KeywordListResponse,
} from '@/lib/api-client';
import { formatCurrency, formatPercentage, getDateRangePresets } from '@/lib/utils';
import MetricsCard from '@/components/dashboard/MetricsCard';
import PerformanceChart from '@/components/dashboard/PerformanceChart';
import KeywordTable from '@/components/dashboard/KeywordTable';

export default function DashboardPage() {
  const [summary, setSummary] = useState<PerformanceSummary | null>(null);
  const [trends, setTrends] = useState<TrendResponse | null>(null);
  const [keywords, setKeywords] = useState<KeywordListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<{ start: string; end: string }>(
    getDateRangePresets()['Last 30 Days']
  );
  const [selectedMetric, setSelectedMetric] = useState<
    'spend' | 'sales' | 'clicks' | 'impressions' | 'orders'
  >('spend');
  const [keywordPage, setKeywordPage] = useState(1);
  const [keywordSort, setKeywordSort] = useState<{
    sortBy: string;
    sortOrder: 'asc' | 'desc';
  }>({ sortBy: 'spend', sortOrder: 'desc' });

  const profileId = process.env.NEXT_PUBLIC_DEFAULT_PROFILE_ID || 'profile_123';

  useEffect(() => {
    loadDashboardData();
  }, [dateRange, keywordPage, keywordSort]);

  async function loadDashboardData() {
    try {
      setLoading(true);
      setError(null);

      // Load all data in parallel
      const [summaryData, trendsData, keywordsData] = await Promise.all([
        apiClient.getPerformanceSummary(profileId, dateRange.start, dateRange.end),
        apiClient.getTrends(profileId, dateRange.start, dateRange.end, 'day'),
        apiClient.getKeywords(
          profileId,
          dateRange.start,
          dateRange.end,
          keywordPage,
          10,
          keywordSort.sortBy,
          keywordSort.sortOrder
        ),
      ]);

      setSummary(summaryData);
      setTrends(trendsData);
      setKeywords(keywordsData);
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
        <MetricsCard
          title="Total Spend"
          value={formatCurrency(summary.total_spend)}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          }
          iconBgColor="bg-yellow-100"
          iconColor="text-yellow-600"
        />

        <MetricsCard
          title="Total Sales"
          value={formatCurrency(summary.total_sales)}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
              />
            </svg>
          }
          iconBgColor="bg-green-100"
          iconColor="text-green-600"
        />

        <MetricsCard
          title="ACOS"
          value={formatPercentage(summary.avg_acos)}
          subtitle="Advertising Cost of Sales"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          }
          iconBgColor="bg-blue-100"
          iconColor="text-blue-600"
        />

        <MetricsCard
          title="ROAS"
          value={summary.avg_roas || '0.00'}
          subtitle="Return on Ad Spend"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
          }
          iconBgColor="bg-purple-100"
          iconColor="text-purple-600"
        />
      </div>

      {/* Additional Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricsCard
          title="Total Orders"
          value={summary.total_orders}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
              />
            </svg>
          }
          iconBgColor="bg-orange-100"
          iconColor="text-orange-600"
        />

        <MetricsCard
          title="Total Clicks"
          value={summary.total_clicks}
          subtitle={`CTR: ${formatPercentage(summary.avg_ctr)}`}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122"
              />
            </svg>
          }
          iconBgColor="bg-indigo-100"
          iconColor="text-indigo-600"
        />

        <MetricsCard
          title="Active Keywords"
          value={summary.keyword_count}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
              />
            </svg>
          }
          iconBgColor="bg-pink-100"
          iconColor="text-pink-600"
        />
      </div>

      {/* Performance Chart */}
      {trends && trends.data_points.length > 0 && (
        <div>
          <div className="mb-4 flex gap-2">
            {(['spend', 'sales', 'clicks', 'impressions', 'orders'] as const).map((metric) => (
              <button
                key={metric}
                onClick={() => setSelectedMetric(metric)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  selectedMetric === metric
                    ? 'bg-yellow-400 text-black'
                    : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                {metric.charAt(0).toUpperCase() + metric.slice(1)}
              </button>
            ))}
          </div>
          <PerformanceChart
            data={trends.data_points}
            metric={selectedMetric}
            chartType="area"
            height={350}
          />
        </div>
      )}

      {/* Keywords Table */}
      {keywords && keywords.keywords.length > 0 && (
        <KeywordTable
          keywords={keywords.keywords}
          totalCount={keywords.total_count}
          currentPage={keywordPage}
          pageSize={10}
          onPageChange={setKeywordPage}
          onSort={(sortBy, sortOrder) => setKeywordSort({ sortBy, sortOrder })}
          currentSort={keywordSort}
        />
      )}

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-black mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => (window.location.href = '/campaigns')}
            className="px-4 py-3 bg-yellow-400 text-black font-medium rounded-md hover:bg-yellow-500 transition-colors"
          >
            View Campaigns
          </button>
          <button
            onClick={() => (window.location.href = '/data-import')}
            className="px-4 py-3 bg-black text-yellow-400 font-medium rounded-md hover:bg-gray-900 transition-colors"
          >
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
