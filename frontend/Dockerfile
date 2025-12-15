FROM node:20-alpine AS builder

WORKDIR /app

# Set NODE_ENV to production for build (ensures basePath is applied)
ENV NODE_ENV=production
# Set NEXT_PUBLIC_BASE_PATH for build (gets embedded in JavaScript)
ENV NEXT_PUBLIC_BASE_PATH=/remittance-assistant

# Copy package files
COPY package.json ./
COPY pnpm-lock.yaml* ./

# Install dependencies with specific pnpm version
RUN corepack enable && corepack prepare pnpm@10.12.4 --activate
RUN pnpm install

# Copy application code
COPY . .

# Build Next.js application with NODE_ENV=production explicitly set
RUN NODE_ENV=production pnpm build

FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/remittance-assistant/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Run application
CMD ["node", "server.js"]

