# Stage 1: Build the TanStack Start application
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies optimally
COPY package.json package-lock.json* ./
RUN npm ci

# Copy application source code
COPY . .

# Build the application
# TanStack Start / Nitro outputs to the .output directory
RUN npm run build

# Stage 2: Serve the application using Node.js
FROM node:20-alpine

WORKDIR /app

# Copy built assets from builder stage
COPY --from=builder /app/.output ./.output

# Create non-root user execution environment for Node (best practice for security)
RUN addgroup -S nodegroup && adduser -S nodeuser -G nodegroup
RUN chown -R nodeuser:nodegroup /app

# Switch to non-root user
USER nodeuser

# Set runtime environment variables
ENV NODE_ENV=production
ENV PORT=3000

# Expose port
EXPOSE 3000

# Start the Nitro SSR Node server
CMD ["node", ".output/server/index.mjs"]
