/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
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
                sans: ['Inter', 'sans-serif'],
                display: ['Poppins', 'sans-serif'],
            },
            dropShadow: {
                'sharp': '4px 4px 0px rgba(0, 26, 51, 0.2)',
                'sharp-lg': '8px 8px 0px rgba(0, 26, 51, 0.2)',
            },
            backgroundImage: {
                'geometric-pattern': "linear-gradient(30deg, #f0f4f8 12%, transparent 12.5%, transparent 87%, #f0f4f8 87.5%, #f0f4f8), linear-gradient(150deg, #f0f4f8 12%, transparent 12.5%, transparent 87%, #f0f4f8 87.5%, #f0f4f8), linear-gradient(30deg, #f0f4f8 12%, transparent 12.5%, transparent 87%, #f0f4f8 87.5%, #f0f4f8), linear-gradient(150deg, #f0f4f8 12%, transparent 12.5%, transparent 87%, #f0f4f8 87.5%, #f0f4f8), linear-gradient(60deg, #f8fafc 25%, transparent 25.5%, transparent 75%, #f8fafc 75%, #f8fafc), linear-gradient(60deg, #f8fafc 25%, transparent 25.5%, transparent 75%, #f8fafc 75%, #f8fafc)",
            }
        },
    },
    plugins: [],
}
