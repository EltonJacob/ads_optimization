'use client';

import { useState } from 'react';

interface HeaderProps {
  onMenuToggle?: () => void;
}

export default function Header({ onMenuToggle }: HeaderProps) {
  const appName = process.env.NEXT_PUBLIC_APP_NAME || 'Amazon PPC Optimizer';
  const appVersion = process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0';

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="flex items-center justify-between px-6 py-4">
        {/* Left: Menu Toggle & App Name */}
        <div className="flex items-center gap-4">
          <button
            onClick={onMenuToggle}
            className="lg:hidden p-2 rounded-md hover:bg-gray-100 transition-colors"
            aria-label="Toggle menu"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>

          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-black rounded-md flex items-center justify-center">
              <span className="text-yellow-400 font-bold text-lg">A</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-black">{appName}</h1>
              <span className="text-xs text-gray-500">v{appVersion}</span>
            </div>
          </div>
        </div>

        {/* Right: Profile Selector & Actions */}
        <div className="flex items-center gap-4">
          {/* Profile Selector */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-md border border-gray-200">
            <svg
              className="w-5 h-5 text-gray-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
            <select
              className="bg-transparent border-none text-sm font-medium text-gray-700 focus:outline-none cursor-pointer"
              defaultValue="profile_123"
            >
              <option value="profile_123">Profile 123</option>
              <option value="profile_456">Profile 456</option>
              <option value="profile_789">Profile 789</option>
            </select>
          </div>

          {/* Notifications */}
          <button
            className="p-2 rounded-md hover:bg-gray-100 transition-colors relative"
            aria-label="Notifications"
          >
            <svg
              className="w-6 h-6 text-gray-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
              />
            </svg>
            {/* Notification badge */}
            <span className="absolute top-1 right-1 w-2 h-2 bg-yellow-400 rounded-full"></span>
          </button>

          {/* Settings */}
          <button
            className="p-2 rounded-md hover:bg-gray-100 transition-colors"
            aria-label="Settings"
          >
            <svg
              className="w-6 h-6 text-gray-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
}
