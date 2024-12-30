# Contributors:
# * Contributor: <rokanas@student.chalmers.se>
# build svelte client
FROM node:22 as build
WORKDIR /app
COPY ./ ./

ARG VITE_BACKEND_SKINSCAN
ENV VITE_BACKEND_SKINSCAN=${VITE_BACKEND_SKINSCAN}
RUN echo "Building with VITE_BACKEND_SKINSCAN=${VITE_BACKEND_SKINSCAN}"

RUN npm install && npm run build

# serve built app with lightweight web server
FROM nginx:alpine

# copy the built files from the first stage
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# expose default port
EXPOSE 80

# run nginx as main process using config file
CMD ["nginx", "-g", "daemon off;"]