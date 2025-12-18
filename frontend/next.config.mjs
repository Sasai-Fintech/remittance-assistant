/** @type {import('next').NextConfig} */
const nextConfig = {
  // Base path for serving the app under /remittance-assistant
  // This is required for ingress routing in Kubernetes
  basePath: process.env.NODE_ENV === 'production' ? '/remittance-assistant' : '',

  // Disable source maps in production to prevent 404 errors for .map files
  productionBrowserSourceMaps: false,
  
  // Optimize for faster compilation
  swcMinify: true,
  
  // Configure external image domains
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'res.cloudinary.com',
        pathname: '/**',
      },
    ],
  },
  
  // Optimize module resolution and compilation
  experimental: {
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons'],
    turbo: {
      resolveAlias: {
        // Optimize common imports
        '@copilotkit/react-core': '@copilotkit/react-core',
        '@copilotkit/react-ui': '@copilotkit/react-ui',
      },
    },
  },
  
  // Disable source maps for CSS and JavaScript (only in production)
  webpack: (config, { dev, isServer }) => {
    // Only disable source maps in production builds
    // Next.js requires eval-source-map in dev mode for proper debugging
    if (!dev) {
      config.devtool = false;
      
      // Disable CSS source maps in production
      if (config.module && config.module.rules) {
        config.module.rules.forEach((rule) => {
          if (rule.test && rule.test.toString().includes('css')) {
            if (rule.use) {
              rule.use.forEach((use) => {
                if (use.loader && typeof use.loader === 'string' && use.loader.includes('css-loader')) {
                  use.options = {
                    ...(use.options || {}),
                    sourceMap: false,
                  };
                }
                if (use.loader && typeof use.loader === 'string' && use.loader.includes('postcss-loader')) {
                  use.options = {
                    ...(use.options || {}),
                    sourceMap: false,
                  };
                }
              });
            }
          }
        });
      }
    }
    
    // Optimize leaflet (if used) - exclude from server-side
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }
    
    // Split chunks for better caching
    if (!dev && !isServer) {
      config.optimization = {
        ...config.optimization,
        moduleIds: 'deterministic',
        runtimeChunk: 'single',
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            default: false,
            vendors: false,
            // Vendor chunk for node_modules
            vendor: {
              name: 'vendor',
              chunks: 'all',
              test: /node_modules/,
              priority: 20,
            },
            // CopilotKit chunk
            copilotkit: {
              name: 'copilotkit',
              test: /[\\/]node_modules[\\/]@copilotkit/,
              chunks: 'all',
              priority: 30,
            },
            // UI libraries chunk
            ui: {
              name: 'ui',
              test: /[\\/]node_modules[\\/](@radix-ui|lucide-react)/,
              chunks: 'all',
              priority: 25,
            },
            // Common chunks
            common: {
              name: 'common',
              minChunks: 2,
              chunks: 'all',
              priority: 10,
              reuseExistingChunk: true,
              enforce: true,
            },
          },
        },
      };
    }
    
    return config;
  },
  
  // Output standalone for Docker
  output: 'standalone',
};

export default nextConfig;

