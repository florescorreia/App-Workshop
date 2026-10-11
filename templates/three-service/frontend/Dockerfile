FROM node:22.19.0-bookworm-slim AS build
WORKDIR /app
ENV RAYON_NUM_THREADS=1 UV_THREADPOOL_SIZE=2 GOMAXPROCS=2
COPY . .
# Build native tooling on tmpfs to avoid executable locking in the Windows
# Rancher Desktop overlay filesystem. Only the built static files are saved.
RUN --mount=type=tmpfs,target=/work cp -r /app/. /work/ && cd /work && npm ci && npm run build && cp -r dist /app/dist
FROM nginx:1.28.0-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
