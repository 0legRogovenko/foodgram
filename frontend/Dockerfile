# --- Этап 1: сборка фронтенда ---
FROM node:21.7.1-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . ./
RUN npm run build

# --- Этап 2: Nginx для отдачи сборки ---
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]