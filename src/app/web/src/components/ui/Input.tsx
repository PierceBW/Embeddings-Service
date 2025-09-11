import React, { InputHTMLAttributes } from 'react';
import clsx from 'clsx';

export const Input = React.forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={clsx(
        'border rounded-md p-2 focus:outline-none focus:ring-2 ring-indigo-500 ring-offset-1',
        className
      )}
      {...props}
    />
  )
);
Input.displayName = 'Input'; 