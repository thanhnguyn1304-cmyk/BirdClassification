import { ButtonHTMLAttributes, forwardRef } from 'react';
import { cn } from '../../lib/utils';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'outline' | 'coral';
    size?: 'sm' | 'md' | 'lg';
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
        return (
            <button
                ref={ref}
                className={cn(
                    "relative inline-flex items-center justify-center gap-2 font-bold uppercase tracking-wider",
                    "border-3 border-ink-black rounded-lg",
                    "shadow-brutal transition-all duration-200",
                    "hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-brutal-hover",
                    "active:translate-x-0 active:translate-y-0 active:shadow-none",
                    "focus:outline-none disabled:opacity-50 disabled:pointer-events-none",

                    // Variants
                    variant === 'primary' && "bg-sun-yellow text-ink-black",
                    variant === 'secondary' && "bg-coastal-blue text-white",
                    variant === 'coral' && "bg-sun-coral text-white",
                    variant === 'outline' && "bg-transparent border-ink-black text-ink-black hover:bg-ink-black hover:text-white",

                    // Sizes
                    size === 'sm' && "text-xs py-2 px-4",
                    size === 'md' && "text-sm py-3 px-6",
                    size === 'lg' && "text-lg py-4 px-8",

                    className
                )}
                {...props}
            >
                {children}
            </button>
        );
    }
);

Button.displayName = "Button";

export { Button };
