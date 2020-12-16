FROM golang:1.15.6-alpine AS build
COPY ./src/DataService /dataservice
WORKDIR /dataservice/main
RUN apk add build-base
RUN go build

FROM golang:1.15.6-alpine AS runner
WORKDIR /
COPY --from=build /dataservice/main/main /dataservice/main/main
COPY ./src/DataService/main/papers.db /dataservice/main/
COPY ./src/config.json /
EXPOSE 8082
CMD ["dataservice/main/main"]