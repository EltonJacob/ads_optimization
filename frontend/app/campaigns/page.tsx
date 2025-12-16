'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';
import type { KeywordListResponse } from '@/lib/api-client';
import { formatCurrency, formatPercentage, formatNumber, getDateRangePresets } from '@/lib/utils';

export default function CampaignsPage() {
  const [keywords, setKeywords] = useState<KeywordListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<{ start: string; end: string }>(
    getDateRangePresets()['Last 30 Days']
  );
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState('spend');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [selectedCampaign, setSelectedCampaign] = useState<string | null>(null);

  const profileId = process.env.NEXT_PUBLIC_DEFAULT_PROFILE_ID || 'profile_123';

  useEffect(() => {
    loadCampaignData();
  }, [dateRange, page, sortBy, sortOrder]);

  async function loadCampaignData() {
    try {
      setLoading(true);
      setError(null);

      const data = await apiClient.getKeywords(
        profileId,
        dateRange.start,
        dateRange.end,
        page,
        20,
        sortBy,
        sortOrder
      );

      setKeywords(data);
    } catch (err) {
      console.error('Failed to load campaign data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }

  // Group keywords by campaign
  const campaignGroups = keywords?.keywords.reduce((acc, keyword) => {
    const campaign = keyword.campaign_name || 'Unknown Campaign';
    if (!acc[campaign]) {
      acc[campaign] = [];
    }
    acc[campaign].push(keyword);
    return acc;
  }, {} as Record<string, Array<typeof keywords.keywords[number]>>) || {};

  // Calculate campaign totals
  const getCampaignTotals = (campaignKeywords: Array<{ impressions: number; clicks: number; spend: string; sales: string; orders: number }>) => {
    return campaignKeywords.reduce(
      (totals, kw) => ({
        impressions: totals.impressions + kw.impressions,
        clicks: totals.clicks + kw.clicks,
        spend: totals.spend + parseFloat(kw.spend),
        sales: totals.sales + parseFloat(kw.sales),
        orders: totals.orders + kw.orders,
      }),
      { impressions: 0, clicks: 0, spend: 0, sales: 0, orders: 0 }
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400"></div>
          <p className="mt-4 text-gray-600">Loading campaigns...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h2 className="text-red-800 font-semibold text-lg mb-2">Error Loading Campaigns</h2>
          <p className="text-red-600">{error}</p>
          <button
            onClick={loadCampaignData}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-black">Campaigns</h1>
          <p className="text-gray-600 mt-1">
            {Object.keys(campaignGroups).length} campaigns with performance data
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

      {/* Campaigns List */}
      <div className="space-y-4">
        {Object.entries(campaignGroups).map(([campaignName, campaignKeywords]) => {
          const totals = getCampaignTotals(campaignKeywords);
          const acos = totals.sales > 0 ? (totals.spend / totals.sales) * 100 : 0;
          const roas = totals.spend > 0 ? totals.sales / totals.spend : 0;
          const ctr = totals.impressions > 0 ? (totals.clicks / totals.impressions) * 100 : 0;
          const isExpanded = selectedCampaign === campaignName;

          return (
            <div key={campaignName} className="bg-white rounded-lg shadow-sm border border-gray-200">
              {/* Campaign Header */}
              <div
                onClick={() => setSelectedCampaign(isExpanded ? null : campaignName)}
                className="p-6 cursor-pointer hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-semibold text-black">{campaignName}</h3>
                      <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">
                        Active
                      </span>
                      <span className="text-sm text-gray-500">
                        {campaignKeywords.length} keywords
                      </span>
                    </div>
                  </div>

                  <svg
                    className={`w-5 h-5 text-gray-600 transition-transform ${
                      isExpanded ? 'transform rotate-180' : ''
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </div>

                {/* Campaign Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-4">
                  <div>
                    <p className="text-xs text-gray-600">Spend</p>
                    <p className="text-lg font-semibold text-black">{formatCurrency(totals.spend)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Sales</p>
                    <p className="text-lg font-semibold text-green-600">
                      {formatCurrency(totals.sales)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">ACOS</p>
                    <p className="text-lg font-semibold text-black">{formatPercentage(acos)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">ROAS</p>
                    <p className="text-lg font-semibold text-black">{roas.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Clicks</p>
                    <p className="text-lg font-semibold text-black">
                      {formatNumber(totals.clicks)}
                    </p>
                    <p className="text-xs text-gray-500">{formatPercentage(ctr)} CTR</p>
                  </div>
                </div>
              </div>

              {/* Expanded Keywords Table */}
              {isExpanded && (
                <div className="border-t border-gray-200">
                  <div className="overflow-x-auto">
                    <table className="min-w-full">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                            Keyword
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                            Match Type
                          </th>
                          <th className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase">
                            Impressions
                          </th>
                          <th className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase">
                            Clicks
                          </th>
                          <th className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase">
                            Spend
                          </th>
                          <th className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase">
                            Sales
                          </th>
                          <th className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase">
                            ACOS
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {campaignKeywords.map((keyword) => (
                          <tr key={keyword.keyword_id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 text-sm font-medium text-black">
                              {keyword.keyword_text}
                            </td>
                            <td className="px-6 py-4">
                              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded">
                                {keyword.match_type}
                              </span>
                            </td>
                            <td className="px-6 py-4 text-right text-sm text-gray-900">
                              {formatNumber(keyword.impressions)}
                            </td>
                            <td className="px-6 py-4 text-right text-sm text-gray-900">
                              {formatNumber(keyword.clicks)}
                            </td>
                            <td className="px-6 py-4 text-right text-sm font-medium text-gray-900">
                              {formatCurrency(keyword.spend)}
                            </td>
                            <td className="px-6 py-4 text-right text-sm font-medium text-green-600">
                              {formatCurrency(keyword.sales)}
                            </td>
                            <td className="px-6 py-4 text-right text-sm text-gray-900">
                              {formatPercentage(keyword.acos)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {Object.keys(campaignGroups).length === 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <svg
            className="w-16 h-16 text-gray-400 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="text-lg font-semibold text-black mb-2">No Campaigns Found</h3>
          <p className="text-gray-600 mb-6">
            Import data or connect to Amazon Ads API to see your campaigns
          </p>
          <button
            onClick={() => (window.location.href = '/data-import')}
            className="px-6 py-3 bg-yellow-400 text-black font-medium rounded-md hover:bg-yellow-500 transition-colors"
          >
            Import Data
          </button>
        </div>
      )}
    </div>
  );
}
