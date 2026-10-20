# Builds the upstream ai-mcp-app-builder monorepo at a pinned commit.

FROM node:22-alpine AS builder

RUN corepack enable && corepack prepare pnpm@10.13.1 --activate

RUN apk add --no-cache git git-lfs && git lfs install

ARG REF=874bc13a57aa2ba1266a84f2444808ce3093efb6
RUN git init /src \
 && git -C /src remote add origin https://github.com/Shubhamsaboo/awesome-llm-apps.git \
 && git -C /src fetch --depth 1 origin ${REF} \
 && git -C /src checkout FETCH_HEAD

WORKDIR /src/generative_ui_agents/ai-mcp-app-builder

# The upstream repo's Git LFS objects 404 on the server, so image assets
# (e.g. apps/web/app/image.png) stay pointer files and break the Next.js
# build ("Invalid PNG signature"). Replace any pointer with a valid 1x1 PNG.
RUN find . -type f -name '*.png' -exec sh -c 'head -c 40 "$1" | grep -q "git-lfs" && echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" | base64 -d > "$1" || true' _ {} \;

RUN pnpm install --frozen-lockfile
RUN pnpm turbo run build --filter=web

FROM node:22-alpine AS runner

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

WORKDIR /app

COPY --from=builder /src/generative_ui_agents/ai-mcp-app-builder/apps/web/.next/standalone ./
COPY --from=builder /src/generative_ui_agents/ai-mcp-app-builder/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder /src/generative_ui_agents/ai-mcp-app-builder/apps/web/.download-kit ./apps/web/.download-kit

USER nextjs

ENV NODE_ENV=production
ENV HOSTNAME=0.0.0.0
ENV PORT=3000

EXPOSE 3000

CMD ["node", "apps/web/server.js"]
