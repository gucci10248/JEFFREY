# BioMCP · Biomedical MCP Server

[![Apache-2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Docker Pulls](https://img.shields.io/docker/pulls/jackgucci/biomcp)](https://hub.docker.com/r/jackgucci/biomcp)
[![MCP](https://img.shields.io/badge/MCP-Protocol-blue)](https://modelcontextprotocol.io/)
[![Smithery](https://img.shields.io/badge/Smithery-Available-green)](https://smithery.ai/server/gucci10248/biomcp1)

> **One command grammar. 50+ biomedical databases. Zero learning curve.**
>
> Genes, variants, drugs, trials, papers, pathways, phenotypes — all through a single MCP endpoint.

BioMCP is a production-grade [Model Context Protocol](https://modelcontextprotocol.io/) server that unifies PubMed, ClinicalTrials.gov, ClinVar, gnomAD, OncoKB, Reactome, KEGG, UniProt, PharmGKB, CPIC, OpenFDA, CDC VAERS, Monarch Initiative, GWAS Catalog, DisGeNET, AlphaGenome, cBioPortal, and 40+ other biomedical sources behind one consistent read-only API.

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

# Test
curl http://localhost:8080/health   # → {"status":"ok"}
```

Your MCP server is live at `http://localhost:8080/mcp`.

---

## MCP Client Setup

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

### Any SSE/Streamable HTTP Client
```
Endpoint: http://localhost:8080/mcp
```

---

## Command Reference

### Genes
| Command | Example |
|---------|---------|
| `get gene <symbol>` | `get gene BRAF` |
| `get gene <symbol> diagnostics` | `get gene BRCA1 diagnostics` |
| `get gene <symbol> funding` | `get gene TP53 funding` |
| `search gene --region <chr:start-end>` | `search gene --region 7:140413127-140624564` |
| `gene pathways <symbol>` | `gene pathways EGFR` |
| `gene trials <symbol>` | `gene trials KRAS` |
| `gene articles <symbol>` | `gene articles PTEN` |
| `gene drugs <symbol>` | `gene drugs ALK` |

### Variants
| Command | Example |
|---------|---------|
| `get variant "<name>"` | `get variant "BRAF V600E"` |
| `search variant --gene <symbol> --impact high` | `search variant --gene CFTR --impact high` |
| `variant trials <id>` | `variant trials "BRAF V600E"` |
| `variant articles <id>` | `variant articles "EGFR L858R"` |

### Drugs
| Command | Example |
|---------|---------|
| `search drug --indication "<disease>"` | `search drug --indication hypertension` |
| `get drug <name>` | `get drug metformin` |
| `get drug <name> safety` | `get drug ibuprofen safety` |
| `get drug <name> regulatory --region eu` | `get drug rivaroxaban regulatory --region eu` |
| `drug interactions <name>` | `drug interactions warfarin` |
| `drug adverse-events <name>` | `drug adverse-events aspirin` |
| `drug trials <name>` | `drug trials pembrolizumab` |

### Diseases
| Command | Example |
|---------|---------|
| `get disease <name>` | `get disease melanoma` |
| `get disease <name> funding` | `get disease tuberculosis funding` |
| `get disease <name> diagnostics` | `get disease HIV diagnostics` |
| `get disease <name> survival` | `get disease "breast cancer" survival` |
| `get disease <name> phenotypes` | `get disease "Parkinson disease" phenotypes` |
| `disease drugs <name>` | `disease drugs diabetes` |
| `disease trials <name>` | `disease trials "acute myeloid leukemia"` |
| `disease articles <name>` | `disease articles atherosclerosis` |

### Articles (PubMed, Europe PMC, LitSense2)
| Command | Example |
|---------|---------|
| `search article -k "<query>" --type review` | `search article -k "CRISPR base editing" --type review` |
| `search article --gene <symbol> -k "<query>"` | `search article --gene APOE -k "Alzheimer risk"` |
| `search article --drug <name>` | `search article --drug metformin` |
| `get article <pmid>` | `get article 23193287` |
| `article citations <pmid>` | `article citations 23193287` |
| `article recommendations <pmid>` | `article recommendations 23193287` |
| `article entities <pmid>` | `article entities 23193287` |

### Clinical Trials
| Command | Example |
|---------|---------|
| `search trial -c "<condition>"` | `search trial -c "type 2 diabetes"` |
| `search trial --gene <symbol>` | `search trial --gene BRAF` |
| `search trial --has-results` | `search trial -c melanoma --has-results` |
| `get trial <nct_id>` | `get trial NCT04280705` |
| `get trial <nct_id> locations` | `get trial NCT04280705 locations --limit 20` |

### Pathways & Enrichment
| Command | Example |
|---------|---------|
| `search pathway "<name>"` | `search pathway "MAPK signaling"` |
| `get pathway <id>` | `get pathway hsa04010` |
| `pathway drugs <id>` | `pathway drugs hsa04151` |
| `enrich <gene list>` | `enrich TP53,EGFR,BRAF,KRAS` |

### Phenotypes
| Command | Example |
|---------|---------|
| `search phenotype "<symptoms>"` | `search phenotype "seizure, developmental delay"` |
| `search phenotype "HP:... HP:..."` | `search phenotype "HP:0001250 HP:0001263"` |

### GWAS
| Command | Example |
|---------|---------|
| `search gwas -g <gene>` | `search gwas -g APOE` |
| `search gwas --trait "<text>"` | `search gwas --trait "body mass index"` |
| `get gwas <id>` | `get gwas GCST90018969` |

### Cross-Entity Search
| Command | Example |
|---------|---------|
| `search all --gene <symbol> --disease <name>` | `search all --gene BRAF --disease melanoma` |
| `discover "<free text>"` | `discover "chest pain"` |
| `suggest "<question>"` | `suggest "What drugs treat melanoma?"` |

### Protein & Structure
| Command | Example |
|---------|---------|
| `get protein <accession>` | `get protein P00519` |
| `protein structures <accession>` | `protein structures P00519` |

### Pharmacogenomics
| Command | Example |
|---------|---------|
| `get pgx <gene>` | `get pgx CYP2D6` |
| `search pgx --drug <name>` | `search pgx --drug clopidogrel` |

### Adverse Events
| Command | Example |
|---------|---------|
| `search adverse-event --drug <name>` | `search adverse-event --drug metformin` |
| `search adverse-event --vaccine <name>` | `search adverse-event --vaccine "COVID-19 mRNA"` |

### Operations
| Command | Example |
|---------|---------|
| `health` | Check API connectivity |
| `version` | Print server version |
| `batch <entity> <id1,id2,...>` | `batch gene BRAF,EGFR,TP53 --sections funding` |

---

## Data Sources

| Source | Coverage |
|--------|----------|
| **PubMed** | 36M+ biomedical citations |
| **Europe PMC** | Full-text, preprints, patents |
| **ClinicalTrials.gov** | 500K+ registered trials |
| **ClinVar** | 3M+ variant-disease annotations |
| **gnomAD** | Population allele frequencies |
| **OncoKB** | Cancer variant clinical actionability |
| **OpenFDA** | FDA drug/device adverse events |
| **UniProt** | Protein function & structure |
| **KEGG** | Metabolic & signaling pathways |
| **Reactome** | Curated pathway database |
| **PharmGKB** | Pharmacogenomics knowledge |
| **CPIC** | Clinical pharmacogenetics guidelines |
| **Monarch Initiative** | Cross-species phenotype ontology |
| **GWAS Catalog** | Genome-wide association studies |
| **cBioPortal** | Cancer genomics datasets |
| **DDInter** | Drug-drug interaction database |
| **CDC VAERS** | Vaccine adverse events |
| **EMA** | European Medicines Agency data |
| **WHO Prequalification** | Essential medicines quality |
| **NCBI GTR** | Genetic testing registry |
| **AlphaGenome** | Genomic variant predictions |
| **DisGeNET** | Gene-disease associations |

---

## Features

- **Read-only by design** — no mutations to external data sources, safe for production
- **Single command grammar** — one pattern for all entity types, no learning curve
- **Resilient** — multi-source fallback, degraded responses with transparent source status
- **Non-root container** — runs as unprivileged `biomcp` user
- **Read-only root filesystem** — `docker compose` enforces `read_only: true`
- **Minimal attack surface** — single static binary, zero runtime dependencies
- **Zero telemetry** — no outbound calls except to public biomedical APIs
- **SHA256-verified binary** — `build.sh` verifies checksum from GitHub Releases
- **Auto-updating data caches** — EMA, WHO, GTR feeds auto-refresh on stale detection

---

## Health & Monitoring

```bash
curl http://localhost:8080/health    # → {"status":"ok"} — API connectivity
curl http://localhost:8080/readyz    # → 200 — ready to serve traffic
curl http://localhost:8080/          # → Welcome page (HTML)
```

---

## Requirements

- Docker 24+ & Docker Compose v2
- ~200MB disk (image + data volumes)
- Outbound internet access to public biomedical APIs
- Optional: `NCBI_API_KEY`, `S2_API_KEY`, `UNPAYWALL_EMAIL` for higher rate limits

---

## Contributing

See [SECURITY.md](SECURITY.md) for vulnerability reporting and [CODEOWNERS](CODEOWNERS) for maintainer contacts.

---

## License

Apache License 2.0 — see [LICENSE](LICENSE).
