# Serves the upstream Excaliflow app at a pinned commit (plain Node, no build step).

FROM node:20-alpine

RUN apk add --no-cache git

ARG REF=874bc13a57aa2ba1266a84f2444808ce3093efb6
RUN git init /app \
 && git -C /app remote add origin https://github.com/Shubhamsaboo/awesome-llm-apps.git \
 && git -C /app fetch --depth 1 origin ${REF} \
 && git -C /app checkout FETCH_HEAD

WORKDIR /app/advanced_llm_apps/excaliflow

ENV PORT=3000
EXPOSE 3000

CMD ["node", "server.js"]
