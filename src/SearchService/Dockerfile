FROM golang:1.15.6-alpine AS build
COPY ./src/SearchService /searchservice
WORKDIR /searchservice/main
RUN apk add build-base
RUN go build

FROM golang:1.15.6-alpine AS runner
COPY --from=build /searchservice/main/main searchservice/main/main
COPY ./src/config.json /
EXPOSE 8080
CMD ["searchservice/main/main"]