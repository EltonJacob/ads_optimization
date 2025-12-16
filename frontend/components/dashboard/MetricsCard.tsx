'use client';

import { ReactNode } from 'react';

interface MetricsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
  iconBgColor?: string;
  iconColor?: string;
  trend?: {
    value: string;
    direction: 'up' | 'down' | 'flat';
  };
}

export default function MetricsCard({
  title,
  value,
  subtitle,
  icon,
  iconBgColor = 'bg-yellow-100',
  iconColor = 'text-yellow-600',
  trend,
}: MetricsCardProps) {
  const getTrendIcon = () => {
    if (!trend) return null;

    const isPositive = trend.direction === 'up';
    const isNegative = trend.direction === 'down';

    return (
      <div
        className={`flex items-center gap-1 text-sm font-medium ${
          isPositive ? 'text-green-600' : isNegative ? 'text-red-600' : 'text-gray-600'
        }`}
      >
        {trend.direction === 'up' && (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
          </svg>
        )}
        {trend.direction === 'down' && (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        )}
        {trend.direction === 'flat' && (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
          </svg>
        )}
        <span>{trend.value}</span>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-black mt-2">{value}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
          {trend && <div className="mt-2">{getTrendIcon()}</div>}
        </div>

        {icon && (
          <div className={`w-12 h-12 ${iconBgColor} rounded-full flex items-center justify-center flex-shrink-0`}>
            <div className={iconColor}>{icon}</div>
          </div>
        )}
      </div>
    </div>
  );
}
