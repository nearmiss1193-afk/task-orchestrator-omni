/** @type {import('next').NextConfig} */
const nextConfig = {
    eslint: { ignoreDuringBuilds: true },
    typescript: { ignoreBuildErrors: true },
    async rewrites() {
        return [
            {
                source: '/landing/:path*',
                destination: '/landing/:path*',
            },
        ]
    }
};

export default nextConfig;
