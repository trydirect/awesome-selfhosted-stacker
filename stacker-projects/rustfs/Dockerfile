# RustFS Official Image
# Uses the pre-built rustfs binary from official releases
FROM rustfs/rustfs:latest

EXPOSE 9000 9001

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
  CMD sh -c "wget -q -O- http://127.0.0.1:9000/health && wget -q -O- http://127.0.0.1:9001/rustfs/console/health || exit 1"

CMD ["rustfs", "server"]
