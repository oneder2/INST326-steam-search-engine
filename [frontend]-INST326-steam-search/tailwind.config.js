/**
 * Tailwind CSS Configuration
 * 
 * This file configures Tailwind CSS for the Steam Game Search Engine project.
 * It includes custom colors, fonts, and other design tokens that match the Steam aesthetic.
 */

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // Custom colors inspired by Steam's design
      colors: {
        steam: {
          blue: '#1b2838',
          'blue-light': '#2a475e',
          'blue-dark': '#171a21',
          green: '#90ba3c',
          'green-light': '#a4d007',
          'green-dark': '#7ba428',
          orange: '#ff6600',
          'orange-light': '#ff8533',
          'orange-dark': '#cc5200',
          gray: {
            100: '#f5f5f5',
            200: '#eeeeee',
            300: '#e0e0e0',
            400: '#bdbdbd',
            500: '#9e9e9e',
            600: '#757575',
            700: '#616161',
            800: '#424242',
            900: '#212121',
          }
        },
        // Game rating colors
        rating: {
          'very-positive': '#66c0f4',
          'positive': '#90ba3c',
          'mixed': '#ffcc00',
          'negative': '#ff6600',
          'very-negative': '#ff3333',
        }
      },
      
      // Custom fonts
      fontFamily: {
        'steam': ['Arial', 'Helvetica', 'sans-serif'],
        'mono': ['Consolas', 'Monaco', 'monospace'],
      },
      
      // Custom spacing
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      
      // Custom border radius
      borderRadius: {
        'steam': '3px',
      },
      
      // Custom box shadows
      boxShadow: {
        'steam': '0 0 5px rgba(0, 0, 0, 0.5)',
        'steam-hover': '0 0 10px rgba(102, 192, 244, 0.5)',
      },
      
      // Custom animations
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      
      // Custom keyframes
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    // Add any Tailwind plugins here
    // require('@tailwindcss/forms'),
    // require('@tailwindcss/typography'),
  ],
}
