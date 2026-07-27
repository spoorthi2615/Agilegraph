# Stage 1: Build the React application
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies optimally
COPY package.json package-lock.json* ./
RUN npm ci

# Copy application source code
COPY . .

# Build the application
# We use standard vite build flags. Environment variables like VITE_API_BASE_URL 
# should be provided during build time or injected via a runtime script if required.
RUN npm run build

# Stage 2: Serve the application using Nginx
FROM nginx:alpine

# Copy custom nginx configuration if needed, otherwise use default
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create non-root user execution environment for Nginx (best practice for security)
RUN chown -R nginx:nginx /var/cache/nginx /var/run /var/log/nginx /usr/share/nginx/html

# Switch to non-root user
USER nginx

# Expose port
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
