import React from 'react';
import { ClipboardIcon } from '@heroicons/react/24/outline';

interface Props {
  id: string;
  timestamp: string;
}

export default function PredictionHeader({ id, timestamp }: Props) {
  const short = `Pred-${id.slice(0, 8)}`;
  return (
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-2">
        <span className="font-semibold">Prediction Result:</span>
        <span className="font-mono font-semibold text-slate-900">{short}</span>
        <button
          onClick={() => navigator.clipboard.writeText(id)}
          className="text-slate-400 hover:text-slate-600"
          title="Copy full ID"
        >
          <ClipboardIcon className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
} 