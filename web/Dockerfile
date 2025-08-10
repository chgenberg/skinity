# syntax=docker/dockerfile:1

# Build stage (needs devDependencies like @tailwindcss/postcss)
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Runtime stage (production deps only)
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=8080

# Install only production deps
COPY package*.json ./
RUN npm ci --omit=dev

# Copy built assets
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.ts ./next.config.ts
COPY --from=builder /app/next-intl.config.js ./next-intl.config.js

EXPOSE 8080
CMD ["npm", "run", "start", "--", "-p", "8080"] 