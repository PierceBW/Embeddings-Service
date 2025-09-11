import React, { ButtonHTMLAttributes } from 'react';
import clsx from 'clsx';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  leftIcon?: React.ReactNode;
}

/**
 * Generic button used across the dashboard.
 * Tailwind styles are applied based on `variant`.
 */
export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', className, leftIcon, ...props }, ref) => {
    const base = 'inline-flex items-center gap-2 px-4 py-2 rounded-md font-medium focus:outline-none transition-colors';
    const variants = {
      primary: 'bg-indigo-600 text-white hover:bg-indigo-700 disabled:bg-indigo-300',
      secondary: 'bg-slate-200 text-slate-800 hover:bg-slate-300 disabled:opacity-50',
      ghost: 'text-indigo-600 hover:bg-indigo-50',
    } as const;

    return (
      <button
        ref={ref}
        className={clsx(base, variants[variant], className)}
        {...props}
      >
        {leftIcon && <span className="h-4 w-4">{leftIcon}</span>}
        {props.children}
      </button>
    );
  }
);
Button.displayName = 'Button'; 