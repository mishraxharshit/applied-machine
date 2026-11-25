FROM rust:1 AS build
WORKDIR /src
COPY Cargo.toml ./
COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim
COPY --from=build /src/target/release/tracecore /usr/local/bin/tracecore
ENTRYPOINT ["tracecore"]
