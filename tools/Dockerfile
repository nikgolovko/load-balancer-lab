FROM debian:bookworm-slim

ARG GRPCURL_VERSION=1.9.3
ARG WEBSOCAT_VERSION=1.14.1
ARG TARGETARCH

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    curl \
    jq \
    tar \
    netcat-openbsd \
    iputils-ping \
    dnsutils \
    procps \
    && rm -rf /var/lib/apt/lists/*
#https://github.com/fullstorydev/grpcurl/releases/download/v1.9.3/grpcurl_1.9.3_linux_arm64.tar.gz
# Install grpcurl and websocat for amd64 or arm64
RUN set -eux; \
    case "${TARGETARCH}" in \
    "amd64") \
    GRPCURL_ARCH="arm64"; \
    WEBSOCAT_ARCH="x86_64-unknown-linux-musl"; \
    ;; \
    "arm64") \
    GRPCURL_ARCH="arm64"; \
    WEBSOCAT_ARCH="aarch64-unknown-linux-musl"; \
    ;; \
    *) \
    echo "Unsupported architecture: ${TARGETARCH}"; \
    exit 1; \
    ;; \
    esac; \
    curl -fsSL \
    "https://github.com/fullstorydev/grpcurl/releases/download/v${GRPCURL_VERSION}/grpcurl_${GRPCURL_VERSION}_linux_${GRPCURL_ARCH}.tar.gz" \
    | tar -xz -C /usr/local/bin grpcurl; \
    curl -fsSL \
    "https://github.com/vi/websocat/releases/download/v${WEBSOCAT_VERSION}/websocat.${WEBSOCAT_ARCH}" \
    -o /usr/local/bin/websocat; \
    chmod +x /usr/local/bin/grpcurl /usr/local/bin/websocat

WORKDIR /workspace

CMD ["sleep", "infinity"]