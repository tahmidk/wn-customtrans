# Use official Nginx docker image as base image
FROM nginx

# Remove default.conf
RUN rm /etc/nginx/conf.d/default.conf

# Place wnct.conf
COPY wnct.conf /etc/nginx/conf.d/