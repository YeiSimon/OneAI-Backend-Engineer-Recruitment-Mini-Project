FROM node:20 as build

WORKDIR src/app

COPY package*.json ./

RUN npm install

COPY ..

RUN npm run build --output-path=dist

FROM nginx:alpine

COPY --from=build /apt/dist/nba-mini-project /usr/share/nginx/html

EXPOSE 80

CMD["nginx", "-g", "daemon off;"]