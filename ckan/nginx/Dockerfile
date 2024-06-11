# Use nginx stable version on Alpine Linux as the base image
FROM nginx:stable-alpine

# Set an environment variable for the nginx configuration directory
ENV NGINX_DIR=/etc/nginx

# Update and upgrade Alpine packages, then install openssl for SSL certificates
RUN apk update --no-cache && \
    apk upgrade --no-cache && \
    apk add --no-cache openssl

# Copy the main nginx config file from the host to the container
COPY setup/default.conf ${NGINX_DIR}/conf.d/default.conf

# Copy the default web page from the host to the container's web directory
COPY setup/index.html /usr/share/nginx/html/index.html

# Create a directory for SSL certificates
RUN mkdir -p ${NGINX_DIR}/certs

# Define what happens when the container starts:
# - Generate a self-signed SSL certificate with openssl
# - Start nginx in the foreground so the container does not immediately exit
ENTRYPOINT \
  openssl req \
    -subj '/C=DE/ST=Berlin/L=Berlin/O=None/CN=localhost' \
    -x509 -newkey rsa:4096 \
    -nodes -keyout ${NGINX_DIR}/certs/ckan-local.key \
    -out ${NGINX_DIR}/certs/ckan-local.crt \
    -days 365 && \
  nginx -g 'daemon off;'
