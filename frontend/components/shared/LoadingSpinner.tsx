'use client';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: 'yellow' | 'black' | 'white';
  message?: string;
}

export default function LoadingSpinner({
  size = 'md',
  color = 'yellow',
  message,
}: LoadingSpinnerProps) {
  const sizeStyles = {
    sm: 'h-6 w-6',
    md: 'h-12 w-12',
    lg: 'h-16 w-16',
  };

  const colorStyles = {
    yellow: 'border-yellow-400',
    black: 'border-black',
    white: 'border-white',
  };

  return (
    <div className="flex flex-col items-center justify-center">
      <div
        className={`inline-block animate-spin rounded-full border-b-2 ${sizeStyles[size]} ${colorStyles[color]}`}
      ></div>
      {message && <p className="mt-4 text-gray-600">{message}</p>}
    </div>
  );
}
