'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface BreadcrumbItem {
  name: string;
  href: string;
}

interface NavigationProps {
  breadcrumbs?: BreadcrumbItem[];
}

export default function Navigation({ breadcrumbs }: NavigationProps) {
  const pathname = usePathname();

  // Auto-generate breadcrumbs from pathname if not provided
  const getBreadcrumbs = (): BreadcrumbItem[] => {
    if (breadcrumbs) return breadcrumbs;

    const paths = pathname.split('/').filter(Boolean);
    const items: BreadcrumbItem[] = [{ name: 'Home', href: '/' }];

    let currentPath = '';
    paths.forEach((path) => {
      currentPath += `/${path}`;
      items.push({
        name: path.charAt(0).toUpperCase() + path.slice(1).replace(/-/g, ' '),
        href: currentPath,
      });
    });

    return items;
  };

  const items = getBreadcrumbs();

  if (items.length <= 1) {
    return null;
  }

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-3">
      <ol className="flex items-center space-x-2 text-sm">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;

          return (
            <li key={item.href} className="flex items-center">
              {index > 0 && (
                <svg
                  className="w-4 h-4 text-gray-400 mx-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              )}

              {isLast ? (
                <span className="font-medium text-black">{item.name}</span>
              ) : (
                <Link
                  href={item.href}
                  className="text-gray-600 hover:text-yellow-500 transition-colors"
                >
                  {item.name}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
