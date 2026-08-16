# Frontend container image, used by docker-compose.yml's "frontend" service.
FROM node:20-alpine AS base

WORKDIR /app

# Copy just the lockfiles first so `npm ci` is cached unless dependencies change.
COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
