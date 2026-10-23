FROM astrocrpublic.azurecr.io/runtime-dev:3.4-1-alpha3

COPY --from=node:24.21.0-trixie-slim@sha256:173f125896c3b47ddf056734c7ea789d04595a6a08769a8f78e0df642781fb66 /usr/local/bin/node /usr/local/bin/node
