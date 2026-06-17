# BioMCP · Biomedical MCP Server

> **One command. 50+ biomedical databases.** Genes, variants, drugs, trials, papers, pathways — all through a single MCP endpoint.

BioMCP is a production-grade [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that unifies PubMed, ClinicalTrials.gov, ClinVar, gnomAD, OncoKB, Reactome, KEGG, UniProt, PharmGKB, OpenFDA, GWAS Catalog, and 40+ other biomedical sources behind one consistent API.

---

## Quickstart

```bash
# Option A: Pull from Docker Hub (recommended)
docker pull jackgucci/biomcp:latest
docker compose up -d

# Option B: Build from source
git clone https://github.com/gucci10248/JEFFREY.git && cd JEFFREY
cp .env.example .env
bash build.sh
docker compose up -d

# 4. Test
curl http://localhost:8080/health
```

Your MCP server is live at `http://localhost:8080/mcp`.

---

## Connecting MCP Clients

### Claude Desktop
```json
{
  "mcpServers": {
    "biomcp": {
      "type": "streamableHttp",
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

### Hermes Agent
```yaml
# ~/.hermes/config.yaml
mcp:
  servers:
    biomcp:
      type: streamableHttp
      url: http://localhost:8080/mcp
      enabled: true
```

### Any SSE-compatible client
```
SSE endpoint: http://localhost:8080/mcp
```

---

## What You Can Query

| Entity | Example |
|--------|---------|
| **Gene** | `get gene BRAF` |
| **Variant** | `get variant "BRAF V600E"` |
| **Drug** | `search drug --indication hypertension` |
| **Disease** | `get disease melanoma` |
| **Article** | `search article -k "AMI biomarkers" --type review` |
| **Trial** | `search trial -c "type 2 diabetes"` |
| **Pathway** | `search pathway "MAPK signaling"` |
| **Phenotype** | `search phenotype "seizure, developmental delay"` |
| **GWAS** | `search gwas -g APOE` |
| **Gene Set Enrichment** | `enrich TP53,EGFR,BRAF` |

Full command reference: `docker exec biomcp biomcp list`

---

## Data Sources

PubMed · Europe PMC · PubTator3 · LitSense2 · ClinicalTrials.gov · ClinVar · gnomAD ·
OncoKB · OpenFDA · CDC VAERS · MyGene · MyVariant · MyChem · Enrichr · KEGG ·
Reactome · UniProt · PharmGKB · CPIC · DDInter · Monarch · GWAS Catalog ·
DisGeNET · AlphaGenome · EMA · WHO Prequalification · NCBI GTR · cBioPortal

---

## Pricing

| Plan | Price | What You Get |
|------|-------|--------------|
| **Community** | Free | Local deployment, no API keys needed |
| **Pro** | $9.99/mo | Pre-configured NCBI API key, priority support |
| **Team** | $49.99/mo | 5 seats, all Pro features, shared API key pool |

> [View full pricing →](https://biomcp.io/pricing)

---

## Security

- ✅ **Read-only** — no mutation of external data sources
- ✅ **Non-root** container — runs as unprivileged `biomcp` user
- ✅ **Minimal attack surface** — single static binary, no runtime dependencies
- ✅ **Read-only root filesystem** — `docker compose` enforces `read_only: true`
- ✅ **No telemetry** — zero outbound calls except to public biomedical APIs
- ✅ **SHA256-verified** — `build.sh` verifies binary checksum from GitHub Releases

---

## Health & Monitoring

```bash
curl http://localhost:8080/health    # API connectivity status
curl http://localhost:8080/readyz    # 200 = ready to serve
curl http://localhost:8080/          # Welcome page
```

---

## Requirements

- Docker 24+ & Docker Compose v2
- ~200MB disk (image + volumes)
- Outbound internet access to public biomedical APIs

---

## License

Apache 2.0
