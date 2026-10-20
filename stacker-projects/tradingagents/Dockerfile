# Multi-stage build of tauricresearch/tradingagents at a pinned commit.
# Source is fetched at build time (see ARG REF) so the template stays small.

FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

ARG REF=e8f5503e9b86d5c2710b0c76b1f686703968c9df
RUN git init /build \
 && git -C /build remote add origin https://github.com/tauricresearch/tradingagents.git \
 && git -C /build fetch --depth 1 origin ${REF} \
 && git -C /build checkout FETCH_HEAD

WORKDIR /build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir .

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TRADINGAGENTS_IN_DOCKER=1

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN useradd --create-home appuser \
 && install -d -m 0755 -o appuser -g appuser /home/appuser/.tradingagents
USER appuser
WORKDIR /home/appuser/app

# tradingagents is a one-shot CLI (analysis runs and exits). Keep the
# container alive so analyses can be launched with:
#   docker exec -it <container> tradingagents --ticker NVDA --date 2026-10-20 ...
ENTRYPOINT []
CMD ["sleep", "infinity"]
