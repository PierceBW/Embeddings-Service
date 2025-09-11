import clsx from 'clsx';

interface BadgeProps {
  level: number;
}

export function RiskBadge({ level }: BadgeProps) {
  const map = {
    0: 'bg-green-100 text-green-800',
    1: 'bg-yellow-100 text-yellow-800',
    2: 'bg-red-100 text-red-800',
  } as const;

  return (
    <span
      className={clsx(
        'inline-block px-3 py-1 text-sm font-semibold rounded-full',
        map[level as 0 | 1 | 2] || 'bg-slate-100 text-slate-800'
      )}
    >
      {level === 0 ? 'Low Risk' : level === 1 ? 'Medium Risk' : 'High Risk'}
    </span>
  );
} 