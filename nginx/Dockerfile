# Use Nginx base image
FROM nginx:latest

# Copy the Nginx configuration
COPY default.conf /etc/nginx/conf.d/default.conf
RUN apt-get update -y
RUN apt-get install vim -y
# Expose the Nginx port
EXPOSE 8070

