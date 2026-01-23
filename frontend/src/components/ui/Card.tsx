import { HTMLAttributes, forwardRef } from 'react';
import { cn } from '../../lib/utils';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
    variant?: 'default' | 'inverse' | 'glass';
}

const Card = forwardRef<HTMLDivElement, CardProps>(
    ({ className, variant = 'default', children, ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={cn(
                    "group",
                    variant === 'default' && "card-geometric",
                    variant === 'inverse' && "card-geometric-inverse",
                    variant === 'glass' && "bg-white/80 backdrop-blur-md border border-white/20 shadow-lg rounded-none", // Fallback or simpler shape
                    className
                )}
                {...props}
            >
                {children}
                {/* Decorative corner triangle */}
                <div className="absolute top-0 right-0 w-8 h-8 bg-gradient-to-bl from-kingfisher-sky/20 to-transparent pointer-events-none" />
            </div>
        );
    }
);

Card.displayName = "Card";

export { Card };
