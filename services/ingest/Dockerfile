FROM golang:1.22-alpine AS build
WORKDIR /src
COPY go.mod main.go ./
RUN CGO_ENABLED=0 go build -o /ingest .

FROM alpine:3.20
COPY --from=build /ingest /usr/local/bin/ingest
VOLUME /data
ENV TRACES_FILE=/data/traces.jsonl
EXPOSE 8080
ENTRYPOINT ["ingest"]
