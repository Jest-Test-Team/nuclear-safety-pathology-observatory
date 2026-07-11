FROM golang:1.25-alpine AS build
WORKDIR /src
COPY apps/api/go.mod apps/api/go.sum ./
COPY apps/api/ ./
RUN CGO_ENABLED=0 go build -o /out/nspo-api ./cmd/server

FROM alpine:3.21
RUN adduser -D -H app
USER app
COPY --from=build /out/nspo-api /usr/local/bin/nspo-api
EXPOSE 8080
ENTRYPOINT ["nspo-api"]
