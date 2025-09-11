import React from 'react';

interface GaugeProps {
  value: number; // 0 - 1
  color: string;
}

export default function Gauge({ value, color }: GaugeProps) {
  const size = 120;
  const stroke = 12;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const dash = circumference * value;

  return (
    <svg width={size} height={size} className="transform -rotate-90">
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        strokeWidth={stroke}
        stroke="#e2e8f0"
        fill="none"
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        strokeWidth={stroke}
        stroke={color}
        fill="none"
        strokeDasharray={`${dash} ${circumference - dash}`}
        strokeLinecap="round"
      />
      <text
        x="50%"
        y="50%"
        dominantBaseline="middle"
        textAnchor="middle"
        className="text-xl font-bold text-slate-900 rotate-90 origin-center"
      >
        {(value * 100).toFixed(0)}%
      </text>
    </svg>
  );
} 