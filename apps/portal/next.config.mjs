/** @type {import('next').NextConfig} */
const nextConfig = {
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
