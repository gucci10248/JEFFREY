# BioMCP Docker Image
# Streamable HTTP MCP server for biomedical data
# Base: Debian Bookworm Slim (glibc required by Rust binary)
FROM debian:bookworm-slim AS runtime

# Security: create non-root user
RUN groupadd -r biomcp && useradd -r -g biomcp -d /app -s /sbin/nologin biomcp

# Create app directory
RUN mkdir -p /app/data /app/cache && chown -R biomcp:biomcp /app

# Copy the pre-built biomcp binary (build it externally or download from GitHub Releases)
COPY biomcp /usr/local/bin/biomcp
RUN chmod +x /usr/local/bin/biomcp

# Drop to non-root
USER biomcp
WORKDIR /app

# MCP Registry OCI annotation (required for official registry submission)
LABEL io.modelcontextprotocol.server.name="io.github.gucci10248/biomcp"

# MCP Streamable HTTP endpoint
EXPOSE 8080

# Health check: /readyz returns 200 when server is up
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q -O- http://localhost:8080/readyz || exit 1

# Optional API keys for enhanced functionality:
#   NCBI_API_KEY     - PubMed E-utilities rate boost
#   S2_API_KEY       - Semantic Scholar paper recommendations
#   ONCOKB_TOKEN     - OncoKB variant annotations
#   DISGENET_API_KEY - DisGeNET gene-disease associations
#   NCI_API_KEY      - NCI Clinical Trials Search
#   UMLS_API_KEY     - UMLS concept mapping
#   ALPHAGENOME_API_KEY - AlphaGenome variant data
#   UNPAYWALL_EMAIL  - Unpaywall full-text fallback

ENV BIOMCP_DATA_DIR=/app/data \
    BIOMCP_CACHE_DIR=/app/cache

ENTRYPOINT ["/usr/local/bin/biomcp", "serve-http", "--host", "0.0.0.0", "--port", "8080"]
