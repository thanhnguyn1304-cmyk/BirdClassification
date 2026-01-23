import { HTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
    variant?: 'success' | 'warning' | 'neutral';
}

export function Badge({ className, variant = 'neutral', ...props }: BadgeProps) {
    return (
        <span
            className={cn(
                "inline-flex items-center px-3 py-1 font-bold text-xs uppercase tracking-widest",
                "bg-kingfisher-midnight text-white", // Default base

                variant === 'success' && "bg-kingfisher-turquoise",
                variant === 'warning' && "bg-kingfisher-coral",

                className
            )}
            style={{ clipPath: 'polygon(10% 0, 100% 0, 90% 100%, 0% 100%)' }}
            {...props}
        />
    );
}
