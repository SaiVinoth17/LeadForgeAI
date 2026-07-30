import React from 'react';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-[#0A0C10] text-gray-100 p-6 flex flex-col gap-6 max-w-[1600px] mx-auto">
      {children}
    </div>
  );
}
