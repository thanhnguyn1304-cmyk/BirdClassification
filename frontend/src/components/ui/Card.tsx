import { HTMLAttributes, forwardRef } from 'react';
import { cn } from '../../lib/utils';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
    variant?: 'default' | 'brutal' | 'glass';
}

const Card = forwardRef<HTMLDivElement, CardProps>(
    ({ className, variant = 'default', children, ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={cn(
                    "group relative",
                    // Brutal style - default for new theme
                    variant === 'default' && "bg-sand-light p-6 border-3 border-ink-black rounded-xl shadow-brutal-lg transition-all duration-200 hover:translate-x-[-4px] hover:translate-y-[-4px] hover:shadow-brutal-xl",
                    variant === 'brutal' && "bg-sand-light p-6 border-3 border-ink-black rounded-xl shadow-brutal-lg transition-all duration-200 hover:translate-x-[-4px] hover:translate-y-[-4px] hover:shadow-brutal-xl",
                    variant === 'glass' && "bg-white/90 backdrop-blur-md p-6 border-2 border-ink-black/20 rounded-xl shadow-lg",
                    className
                )}
                {...props}
            >
                {children}
            </div>
        );
    }
);

Card.displayName = "Card";

export { Card };
