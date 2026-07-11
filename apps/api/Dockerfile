FROM golang:1.25-alpine AS build
WORKDIR /src
COPY apps/api/go.mod apps/api/go.sum ./
COPY apps/api/ ./
RUN CGO_ENABLED=0 go build -o /out/nspo-api ./cmd/server

FROM alpine:3.21
RUN adduser -D -H app
WORKDIR /app
COPY --from=build /out/nspo-api /usr/local/bin/nspo-api
# Bake demo findings so Container Instances can start without a host bind-mount.
COPY data/derived /data/derived
RUN mkdir -p /data/runtime && chown -R app:app /data
USER app
ENV NSPO_API_ADDR=:8080 \
    NSPO_DATA_DIR=/data/derived \
    NSPO_REVIEW_STORE=/data/runtime/reviews.json
EXPOSE 8080
ENTRYPOINT ["nspo-api"]
