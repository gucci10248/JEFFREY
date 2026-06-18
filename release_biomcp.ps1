# BioMCP GitHub Release Creator
# Reads GH_TOKEN from environment variable

$tag = "v0.8.22"
$repo = "gucci10248/JEFFREY"
$token = $env:GH_TOKEN
if (-not $token) {
    Write-Host "Error: GH_TOKEN not set. Run: `$env:GH_TOKEN='your_pat'" -ForegroundColor Red
    Read-Host
    exit 1
}

Write-Host "Creating GitHub Release $tag..." -ForegroundColor Cyan

$body = @{
    tag_name = $tag
    name = "BioMCP v0.8.22 - Official MCP Registry"
    body = @"
## BioMCP v0.8.22

**Now listed on the official MCP Registry** 🎉

### What is BioMCP?
50+ biomedical data sources in one MCP server - PubMed, ClinicalTrials.gov, ClinVar, gnomAD, OncoKB, Reactome, KEGG, UniProt, PharmGKB, CPIC, OpenFDA, GWAS Catalog, and more.

### Quick Start

```bash
docker pull jackgucci/biomcp:0.8.22
docker run -p 8080:8080 jackgucci/biomcp:0.8.22
```

### MCP Registry
https://registry.modelcontextprotocol.io/servers/io.github.gucci10248/biomcp

### Documentation
https://gucci10248.github.io/JEFFREY
"@
    draft = $false
    prerelease = $false
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Bearer $token"
    "Accept" = "application/vnd.github+json"
}

try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/releases" `
        -Method Post -Headers $headers -Body $body -ContentType "application/json"
    Write-Host "Release created!" -ForegroundColor Green
    Write-Host $response.html_url
} catch {
    if ($_.Exception.Response.StatusCode -eq 422) {
        Write-Host "Release $tag already exists, fetching..." -ForegroundColor Yellow
        $response = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/releases/tags/$tag" `
            -Method Get -Headers $headers
        Write-Host "Existing release: $($response.html_url)" -ForegroundColor Green
    } else {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`nCheck: https://github.com/$repo/releases" -ForegroundColor Cyan
Write-Host "Press Enter to close..."
Read-Host
