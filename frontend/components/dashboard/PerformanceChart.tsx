'use client';

import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { formatCurrency, formatDate } from '@/lib/utils';

interface TrendDataPoint {
  date: string;
  impressions: number;
  clicks: number;
  spend: string;
  sales: string;
  orders: number;
  acos: string | null;
  roas: string | null;
  ctr: string | null;
}

interface PerformanceChartProps {
  data: TrendDataPoint[];
  metric: 'spend' | 'sales' | 'clicks' | 'impressions' | 'orders';
  chartType?: 'line' | 'area';
  height?: number;
}

export default function PerformanceChart({
  data,
  metric,
  chartType = 'area',
  height = 300,
}: PerformanceChartProps) {
  // Transform data for the chart
  const chartData = data.map((point) => ({
    date: formatDate(point.date),
    value:
      metric === 'spend' || metric === 'sales'
        ? parseFloat(point[metric])
        : point[metric],
  }));

  const getMetricConfig = () => {
    switch (metric) {
      case 'spend':
        return {
          name: 'Spend',
          color: '#fbbf24',
          format: (value: number) => formatCurrency(value),
        };
      case 'sales':
        return {
          name: 'Sales',
          color: '#10b981',
          format: (value: number) => formatCurrency(value),
        };
      case 'clicks':
        return {
          name: 'Clicks',
          color: '#3b82f6',
          format: (value: number) => value.toLocaleString(),
        };
      case 'impressions':
        return {
          name: 'Impressions',
          color: '#8b5cf6',
          format: (value: number) => value.toLocaleString(),
        };
      case 'orders':
        return {
          name: 'Orders',
          color: '#f59e0b',
          format: (value: number) => value.toLocaleString(),
        };
      default:
        return {
          name: metric,
          color: '#6b7280',
          format: (value: number) => value.toLocaleString(),
        };
    }
  };

  const config = getMetricConfig();

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
          <p className="text-sm font-medium text-gray-900">{payload[0].payload.date}</p>
          <p className="text-sm text-gray-600 mt-1">
            <span className="font-medium" style={{ color: config.color }}>
              {config.name}:
            </span>{' '}
            {config.format(payload[0].value)}
          </p>
        </div>
      );
    }
    return null;
  };

  const ChartComponent = chartType === 'area' ? AreaChart : LineChart;
  const DataComponent = chartType === 'area' ? Area : Line;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-black">{config.name} Trend</h3>
        <p className="text-sm text-gray-600">Daily performance over time</p>
      </div>

      <ResponsiveContainer width="100%" height={height}>
        <ChartComponent data={chartData}>
          <defs>
            <linearGradient id={`gradient-${metric}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={config.color} stopOpacity={0.3} />
              <stop offset="95%" stopColor={config.color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="date"
            tick={{ fill: '#6b7280', fontSize: 12 }}
            tickLine={{ stroke: '#e5e7eb' }}
          />
          <YAxis
            tick={{ fill: '#6b7280', fontSize: 12 }}
            tickLine={{ stroke: '#e5e7eb' }}
            tickFormatter={config.format}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="circle"
            formatter={() => config.name}
          />
          {chartType === 'area' ? (
            <Area
              type="monotone"
              dataKey="value"
              stroke={config.color}
              strokeWidth={2}
              fill={`url(#gradient-${metric})`}
              name={config.name}
            />
          ) : (
            <Line
              type="monotone"
              dataKey="value"
              stroke={config.color}
              strokeWidth={2}
              dot={{ fill: config.color, r: 4 }}
              activeDot={{ r: 6 }}
              name={config.name}
            />
          )}
        </ChartComponent>
      </ResponsiveContainer>
    </div>
  );
}
