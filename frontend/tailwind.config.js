/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    // Safelist ensures these dynamically-used gradient classes are never purged
    safelist: [
        'bg-gradient-to-br',
        'from-coastal-blue', 'to-coastal-deepblue',
        'from-emerald-500', 'to-emerald-600',
        'from-sun-orange', 'to-sun-coral',
        'from-purple-500', 'to-purple-600',
        'from-green-500', 'to-green-600',
        'from-amber-500', 'to-amber-600',
    ],
    theme: {
        extend: {
            colors: {
                // San Sebastian Retro Coastal Palette
                coastal: {
                    blue: "#007AFF",       // Vibrant electric blue
                    deepblue: "#0056B3",   // Darker blue for hover states
                    navy: "#003366",       // Deep navy for text/accents
                },
                sand: {
                    light: "#FFF8E7",      // Warm cream background
                    DEFAULT: "#F5E6C8",    // Sand color
                    dark: "#E8D5A3",       // Darker sand
                },
                sun: {
                    yellow: "#FFD700",     // Vibrant yellow
                    orange: "#FF9500",     // Orange accent
                    coral: "#FF453A",      // Coral/red accent
                },
                ink: {
                    black: "#1a1a1a",      // Rich black for borders/text
                    gray: "#4a4a4a",       // Dark gray
                },
                // Keep some kingfisher colors for backwards compatibility
                kingfisher: {
                    royal: "#0055D4",
                    sky: "#4BA3F5",
                    turquoise: "#00C2CB",
                    coral: "#FF6B35",
                    peach: "#FF9E75",
                    midnight: "#001A33",
                }
            },
            fontFamily: {
                sans: ['DM Sans', 'Inter', 'sans-serif'],
                display: ['Passion One', 'Poppins', 'sans-serif'],
                body: ['Space Grotesk', 'DM Sans', 'sans-serif'],
            },
            boxShadow: {
                'brutal': '4px 4px 0px 0px #1a1a1a',
                'brutal-lg': '6px 6px 0px 0px #1a1a1a',
                'brutal-xl': '8px 8px 0px 0px #1a1a1a',
                'brutal-hover': '6px 6px 0px 0px #1a1a1a',
            },
            dropShadow: {
                'sharp': '4px 4px 0px rgba(0, 26, 51, 0.2)',
                'sharp-lg': '8px 8px 0px rgba(0, 26, 51, 0.2)',
            },
            backgroundImage: {
                'geometric-pattern': "linear-gradient(30deg, #f0f4f8 12%, transparent 12.5%, transparent 87%, #f0f4f8 87.5%, #f0f4f8), linear-gradient(150deg, #f0f4f8 12%, transparent 12.5%, transparent 87%, #f0f4f8 87.5%, #f0f4f8), linear-gradient(30deg, #f0f4f8 12%, transparent 12.5%, transparent 87%, #f0f4f8 87.5%, #f0f4f8), linear-gradient(150deg, #f0f4f8 12%, transparent 12.5%, transparent 87%, #f0f4f8 87.5%, #f0f4f8), linear-gradient(60deg, #f8fafc 25%, transparent 25.5%, transparent 75%, #f8fafc 75%, #f8fafc), linear-gradient(60deg, #f8fafc 25%, transparent 25.5%, transparent 75%, #f8fafc 75%, #f8fafc)",
                'wave-pattern': "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320'%3E%3Cpath fill='%23FFF8E7' d='M0,96L48,112C96,128,192,160,288,165.3C384,171,480,149,576,149.3C672,149,768,171,864,165.3C960,160,1056,128,1152,122.7C1248,117,1344,139,1392,149.3L1440,160L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z'%3E%3C/path%3E%3C/svg%3E\")",
            },
            borderWidth: {
                '3': '3px',
            }
        },
    },
    plugins: [],
}
