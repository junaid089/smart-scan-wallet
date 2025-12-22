import type { NextConfig } from 'next';
import path from 'path';

const nextConfig: NextConfig = {
    webpack: (config) => {
        config.resolve.alias = {
            ...config.resolve.alias,
            '@': path.resolve(__dirname, 'src'),
        };
        return config;
    },
    // Disable Turbopack for now due to path alias issues
    experimental: {
        turbo: undefined,
    },
};

export default nextConfig;
