# RustFS Official Image
# Uses the pre-built rustfs binary from official releases
FROM rustfs/rustfs:latest

EXPOSE 9000 9001

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
  CMD sh -c "wget -q -O- http://127.0.0.1:9000/health || exit 1"

# Pre-create required directories as root before switching user
USER root
RUN mkdir -p /opt/tls /data /app/logs && \
    chmod 755 /opt/tls /data /app/logs && \
    chown -R rustfs:rustfs /opt/tls /data /app/logs || true

# Create entrypoint that generates self-signed certs if needed
COPY entrypoint.sh /entrypoint.sh
USER root
ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
