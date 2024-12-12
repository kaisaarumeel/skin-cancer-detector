# build svelte client
FROM node:22 as build
WORKDIR /app
COPY ./ ./
RUN npm install && npm run build

# serve built app with lightweight web server
FROM nginx:alpine

# copy the built files from the first stage
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# expose default port
EXPOSE 80
ENV CLIENT_API_BASE_URL=http://164.92.176.222:8000

# run nginx as main process using config file
CMD ["nginx", "-g", "daemon off;"]