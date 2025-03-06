// next.config.mjs
import { createRequire } from 'module';
const require = createRequire(import.meta.url);

export default {
  reactStrictMode: true,
  swcMinify: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*', // Proxy to FastAPI backend (rest)
      },
      {
        source: '/ws',
        destination: 'http://localhost:8000/ws', // Proxy to FastAPI backend (ws)
      }
    ];
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // Fixes npm packages that depend on `fs` module
      config.resolve.fallback.fs = false;
    }
    return config;
  }
};
