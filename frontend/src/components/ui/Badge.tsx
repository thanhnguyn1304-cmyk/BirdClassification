import { HTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
    variant?: 'success' | 'warning' | 'neutral' | 'info';
}

export function Badge({ className, variant = 'neutral', ...props }: BadgeProps) {
    return (
        <span
            className={cn(
                "inline-flex items-center px-3 py-1 font-bold text-xs uppercase tracking-wider",
                "border-2 border-ink-black rounded-full shadow-[2px_2px_0px_0px_#1a1a1a]",

                // Variants
                variant === 'neutral' && "bg-sand-light text-ink-black",
                variant === 'success' && "bg-green-400 text-ink-black",
                variant === 'warning' && "bg-sun-yellow text-ink-black",
                variant === 'info' && "bg-coastal-blue text-white",

                className
            )}
            {...props}
        />
    );
}
