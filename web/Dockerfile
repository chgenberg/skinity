# syntax=docker/dockerfile:1
FROM node:20-alpine AS base
WORKDIR /app
ENV NODE_ENV=production

# Install deps
COPY package*.json ./
RUN npm ci --omit=dev

# Copy source and build
COPY . .
RUN npm run build

# Runtime
ENV PORT=8080
EXPOSE 8080
CMD ["npm", "run", "start", "--", "-p", "8080"] 