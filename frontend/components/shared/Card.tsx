'use client';

import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
}

export default function Card({
  children,
  title,
  subtitle,
  className = '',
  padding = 'md',
  hover = false,
}: CardProps) {
  const paddingStyles = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div
      className={`bg-white rounded-lg shadow-sm border border-gray-200 ${
        hover ? 'hover:shadow-md transition-shadow' : ''
      } ${className}`}
    >
      {(title || subtitle) && (
        <div className={`border-b border-gray-200 ${paddingStyles[padding]}`}>
          {title && <h3 className="text-lg font-semibold text-black">{title}</h3>}
          {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
        </div>
      )}
      <div className={title || subtitle ? '' : paddingStyles[padding]}>{children}</div>
    </div>
  );
}
