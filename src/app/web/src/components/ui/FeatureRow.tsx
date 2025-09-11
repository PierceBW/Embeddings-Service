import React from 'react';

interface FeatureRowProps {
  label: string;
  value: React.ReactNode;
}

// Renders label/value. If label contains a parenthetical description, it is rendered on a second line.
export default function FeatureRow({ label, value }: FeatureRowProps) {
  const match = label.match(/\(([^)]+)\)/);
  const hasDesc = Boolean(match);
  const mainLabel = hasDesc ? label.replace(/\s*\([^)]*\)\s*$/, '') : label;
  const desc = match ? match[1] : '';

  if (!hasDesc) {
    return (
      <div className="flex justify-between py-1.5 mb-2 border-b border-slate-100">
        <span className="text-sm text-slate-600">{mainLabel}</span>
        <span className="text-sm text-slate-800 font-medium break-words text-right ml-3">{value}</span>
      </div>
    );
  }

  return (
    <div className="py-1.5 mb-2 border-b border-slate-100">
      <div className="flex justify-between">
        <span className="text-sm text-slate-700">{mainLabel}</span>
        <span className="text-sm text-slate-900 font-medium break-words text-right ml-3">{value}</span>
      </div>
      <div className="text-xs text-slate-500 mt-1">{desc}</div>
    </div>
  );
}


