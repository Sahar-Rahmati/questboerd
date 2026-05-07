FROM node:24-alpine AS builder

WORKDIR /app/frontend

COPY frontend/package.json /app/frontend/package.json
RUN npm install

COPY frontend /app/frontend

ARG VITE_API_BASE_URL=/api/v1
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

FROM nginx:1.27-alpine

COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/frontend/dist /usr/share/nginx/html

EXPOSE 80
