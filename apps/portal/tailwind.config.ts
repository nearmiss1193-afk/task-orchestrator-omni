import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                spartan: {
                    900: "#000000",
                    800: "#111111",
                    700: "#1a1a1a",
                    500: "#ff3333", // Accent Red
                }
            },
        },
    },
    plugins: [],
};
export default config;
