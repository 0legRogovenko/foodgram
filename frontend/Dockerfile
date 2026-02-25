FROM node:21-alpine as build
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:1.22.1
COPY --from=build /app/build /usr/share/nginx/html