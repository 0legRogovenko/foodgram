FROM node:21.7.1-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:1.22.1
COPY --from=build /app/build /usr/share/nginx/html
