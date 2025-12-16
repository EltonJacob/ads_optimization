'use client';

import { useState } from 'react';
import { formatCurrency, formatPercentage, formatNumber } from '@/lib/utils';

interface KeywordListItem {
  keyword_id: string;
  keyword_text: string;
  match_type: string;
  campaign_name: string | null;
  ad_group_name: string | null;
  state: string;
  bid: string | null;
  impressions: number;
  clicks: number;
  spend: string;
  sales: string;
  orders: number;
  cpc: string | null;
  ctr: string | null;
  acos: string | null;
  roas: string | null;
  conversion_rate: string | null;
}

interface KeywordTableProps {
  keywords: KeywordListItem[];
  totalCount: number;
  currentPage: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onSort: (sortBy: string, sortOrder: 'asc' | 'desc') => void;
  currentSort: {
    sortBy: string;
    sortOrder: 'asc' | 'desc';
  };
}

export default function KeywordTable({
  keywords,
  totalCount,
  currentPage,
  pageSize,
  onPageChange,
  onSort,
  currentSort,
}: KeywordTableProps) {
  const totalPages = Math.ceil(totalCount / pageSize);

  const handleSort = (field: string) => {
    const newOrder =
      currentSort.sortBy === field && currentSort.sortOrder === 'desc' ? 'asc' : 'desc';
    onSort(field, newOrder);
  };

  const SortIcon = ({ field }: { field: string }) => {
    if (currentSort.sortBy !== field) {
      return (
        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
      );
    }

    return currentSort.sortOrder === 'desc' ? (
      <svg className="w-4 h-4 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    ) : (
      <svg className="w-4 h-4 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
      </svg>
    );
  };

  const getMatchTypeBadge = (matchType: string) => {
    const colors: Record<string, string> = {
      EXACT: 'bg-green-100 text-green-800',
      PHRASE: 'bg-blue-100 text-blue-800',
      BROAD: 'bg-purple-100 text-purple-800',
    };

    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${colors[matchType] || 'bg-gray-100 text-gray-800'}`}>
        {matchType}
      </span>
    );
  };

  const getStateBadge = (state: string) => {
    const isEnabled = state === 'ENABLED' || state === 'enabled';
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${isEnabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
        {state}
      </span>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-black">Keywords Performance</h3>
        <p className="text-sm text-gray-600 mt-1">
          Showing {keywords.length} of {totalCount} keywords
        </p>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th
                onClick={() => handleSort('keyword_text')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              >
                <div className="flex items-center gap-2">
                  Keyword
                  <SortIcon field="keyword_text" />
                </div>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Match Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                State
              </th>
              <th
                onClick={() => handleSort('impressions')}
                className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              >
                <div className="flex items-center justify-end gap-2">
                  Impressions
                  <SortIcon field="impressions" />
                </div>
              </th>
              <th
                onClick={() => handleSort('clicks')}
                className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              >
                <div className="flex items-center justify-end gap-2">
                  Clicks
                  <SortIcon field="clicks" />
                </div>
              </th>
              <th
                onClick={() => handleSort('spend')}
                className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              >
                <div className="flex items-center justify-end gap-2">
                  Spend
                  <SortIcon field="spend" />
                </div>
              </th>
              <th
                onClick={() => handleSort('sales')}
                className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              >
                <div className="flex items-center justify-end gap-2">
                  Sales
                  <SortIcon field="sales" />
                </div>
              </th>
              <th
                onClick={() => handleSort('acos')}
                className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              >
                <div className="flex items-center justify-end gap-2">
                  ACOS
                  <SortIcon field="acos" />
                </div>
              </th>
              <th
                onClick={() => handleSort('roas')}
                className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              >
                <div className="flex items-center justify-end gap-2">
                  ROAS
                  <SortIcon field="roas" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {keywords.map((keyword) => (
              <tr key={keyword.keyword_id} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4">
                  <div>
                    <div className="text-sm font-medium text-black">{keyword.keyword_text}</div>
                    {keyword.campaign_name && (
                      <div className="text-xs text-gray-500 mt-1">{keyword.campaign_name}</div>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getMatchTypeBadge(keyword.match_type)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStateBadge(keyword.state)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                  {formatNumber(keyword.impressions)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                  {formatNumber(keyword.clicks)}
                  {keyword.ctr && (
                    <div className="text-xs text-gray-500">{formatPercentage(keyword.ctr)} CTR</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                  {formatCurrency(keyword.spend)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-green-600">
                  {formatCurrency(keyword.sales)}
                  <div className="text-xs text-gray-500">{keyword.orders} orders</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                  {formatPercentage(keyword.acos)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                  {keyword.roas || '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
        <div className="text-sm text-gray-600">
          Page {currentPage} of {totalPages}
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className={`px-4 py-2 border rounded-md text-sm font-medium transition-colors ${
              currentPage === 1
                ? 'border-gray-200 text-gray-400 cursor-not-allowed'
                : 'border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            Previous
          </button>

          <button
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className={`px-4 py-2 border rounded-md text-sm font-medium transition-colors ${
              currentPage === totalPages
                ? 'border-gray-200 text-gray-400 cursor-not-allowed'
                : 'border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
