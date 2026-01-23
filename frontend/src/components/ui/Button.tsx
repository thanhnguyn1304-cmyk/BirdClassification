import { ButtonHTMLAttributes, forwardRef } from 'react';
import { cn } from '../../lib/utils';
// import { motion } from 'framer-motion';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'outline';
    size?: 'sm' | 'md' | 'lg';
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
        return (
            <button
                ref={ref}
                className={cn(
                    "relative font-bold uppercase tracking-wider transition-all duration-200 focus:outline-none disabled:opacity-50 disabled:pointer-events-none hover:scale-105 active:scale-95",

                    // Variants
                    variant === 'primary' && "btn-primary", // Defined in index.css
                    variant === 'secondary' && "bg-kingfisher-sky text-white hover:bg-kingfisher-royal py-3 px-6",
                    variant === 'outline' && "border-2 border-kingfisher-royal text-kingfisher-royal hover:bg-kingfisher-royal hover:text-white py-2 px-6",

                    // Sizes
                    size === 'sm' && "text-xs py-2 px-4",
                    size === 'lg' && "text-lg py-4 px-8",

                    className
                )}
                style={variant === 'secondary' ? { clipPath: 'polygon(20% 0%, 80% 0%, 100% 20%, 100% 80%, 80% 100%, 20% 100%, 0% 80%, 0% 20%)' } : {}}
                {...props}
            >
                {children}
            </button>
        );
    }
);

Button.displayName = "Button";

export { Button };
