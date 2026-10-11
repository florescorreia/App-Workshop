FROM node:22.19.0-bookworm-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN mkdir -p public/vendor && cp node_modules/plotly.js-dist-min/plotly.min.js public/vendor/plotly.min.js && cp node_modules/@dagrejs/dagre/dist/dagre.min.js public/vendor/dagre.min.js
RUN cp node_modules/swagger-ui-dist/swagger-ui-bundle.js node_modules/swagger-ui-dist/swagger-ui.css node_modules/swagger-ui-dist/favicon-32x32.png public/vendor/ && node scripts/inventory.cjs > /app/dependency-inventory.json
RUN npm run build
FROM nginx:1.28.0-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
