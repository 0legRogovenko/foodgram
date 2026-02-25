FROM 0legrogovenko/foodgram_frontend:latest AS build

FROM nginx:1.22.1

COPY --from=build /app/build /app/collected_static

COPY nginx.conf /etc/nginx/conf.d/default.conf
