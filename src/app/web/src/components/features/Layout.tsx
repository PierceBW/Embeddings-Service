import React from 'react';
import MainWorkspace from './MainWorkspace';
import SidePanel from './SidePanel';

export default function Layout() {
  return (
    <div className="md:flex min-h-screen gap-0 px-1 py-1">
      <div className="md:w-1/2 w-full">
        <SidePanel />
      </div>
      <div className="md:w-1/2 w-full">
        <MainWorkspace />
      </div>
    </div>
  );
} 