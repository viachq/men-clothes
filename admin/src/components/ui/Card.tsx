import type { HTMLAttributes } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export default function Card({ 
  children, 
  variant = 'default', 
  padding = 'md', 
  className = '', 
  ...props 
}: CardProps) {
  const baseStyles = 'rounded-xl transition-all';
  
  const variants = {
    default: 'bg-white dark:bg-neutral-900 shadow-sm border border-neutral-200 dark:border-neutral-700 hover:shadow-md',
    elevated: 'bg-white dark:bg-neutral-900 shadow-lg',
    outlined: 'bg-white dark:bg-neutral-900 border-2 border-neutral-200 dark:border-neutral-700',
  };
  
  const paddings = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };
  
  return (
    <div className={`${baseStyles} ${variants[variant]} ${paddings[padding]} ${className}`} {...props}>
      {children}
    </div>
  );
}

export function CardHeader({ children, className = '', ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`pb-4 border-b border-neutral-200 dark:border-neutral-700 mb-4 ${className}`} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({ children, className = '', ...props }: HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className={`text-xl font-bold text-neutral-900 dark:text-white ${className}`} {...props}>
      {children}
    </h3>
  );
}

export function CardContent({ children, className = '', ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={className} {...props}>
      {children}
    </div>
  );
}

