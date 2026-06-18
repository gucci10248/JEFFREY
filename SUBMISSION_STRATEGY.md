# BioMCP Marketplace Submission Strategy

> **XPack.io 调研结论：站点不可达（多次超时）。替代方案：13 个 MCP 注册中心，分三档优先级提交。**

---

## 一、MCP 注册中心全景

| 优先级 | 注册中心 | 类型 | 受众规模 | 提交方式 |
|--------|----------|------|----------|----------|
| **P0** | [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io) | 官方 Registry | ★★★★★ | `mcp-publisher` CLI |
| **P0** | [Smithery.ai](https://smithery.ai) | 最大三方市场 | ★★★★★ (42K+ uses) | API / Web |
| **P0** | [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) | GitHub 列表 | ★★★★ | PR |
| **P0** | [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | 官方列表 | ★★★★ | PR |
| P1 | [Glama.ai](https://glama.ai/mcp/servers) | 三方市场 | ★★★ | API |
| P1 | [mcp.so](https://mcp.so) | 目录站点 | ★★★ | Browser Form |
| P1 | [cline/mcp-marketplace](https://github.com/cline/mcp-marketplace) | Cline 市场 | ★★★ | PR |
| P2 | PulseMCP, Stork, Claude DXT, wong2, appcypher, VS Code Gallery | 长尾 | ★~★★ | PR/Form |

---

## 二、提交前准备

### 2.1 GitHub Release（必须）
```bash
git tag v0.8.22
git push origin v0.8.22
# GitHub Actions 自动构建 Docker image + 创建 Release
```

### 2.2 打包格式
- **Docker Image**: `biomcp:0.8.22` → Docker Hub
- **Binary**: 上传 `biomcp-x86_64-unknown-linux-gnu` 到 Release assets
- **SHA256**: 附带校验和文件

### 2.3 元数据文件（`mcp.json`）
```json
{
  "name": "biomcp",
  "displayName": "BioMCP",
  "description": "50+ biomedical databases unified behind one MCP endpoint. Genes, variants, drugs, trials, papers, pathways.",
  "version": "0.8.22",
  "repository": "https://github.com/gucci10248/JEFFREY",
  "transport": "streamableHttp",
  "license": "Apache-2.0",
  "homepage": "https://biomcp.io",
  "categories": ["science", "healthcare", "research"],
  "keywords": ["biomedical", "pubmed", "genomics", "clinical-trials", "pharmacology"],
  "tools": [
    {"name": "search", "description": "Search genes, variants, drugs, trials, articles, diseases"},
    {"name": "get", "description": "Fetch entity by ID with optional sections"},
    {"name": "health", "description": "Check API connectivity"},
    {"name": "enrich", "description": "Gene set enrichment analysis"}
  ]
}
```

---

## 三、P0 提交步骤

### Smithery (最大市场)
1. 注册 https://smithery.ai
2. Create Server → 填写名称/描述/图标
3. Deployment: `Streamable HTTP` → 提供 `https://your-host:8080/mcp`
4. 验证连接 → 发布

### 官方 MCP Registry
```bash
# Download official publisher CLI
curl -L https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_linux_amd64.tar.gz | tar xz
./mcp-publisher login github
./mcp-publisher publish
# Uses server.json in current directory for metadata
```

### awesome-mcp-servers (GitHub PR)
1. Fork `punkpeye/awesome-mcp-servers`
2. 在 `README.md` 的 **Science** 分类下添加
3. 格式: `- [BioMCP](https://github.com/gucci10248/JEFFREY) — 50+ biomedical databases unified behind one MCP endpoint`
4. 提交 PR

---

## 四、自动化（GitHub Actions）
```yaml
# .github/workflows/publish.yml
on:
  push:
    tags: ['v*']
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: |
          docker build -t jackgucci/biomcp:${{ github.ref_name }} .
          docker tag jackgucci/biomcp:${{ github.ref_name }} jackgucci/biomcp:latest
      - name: Push to Docker Hub
        run: |
          echo "${{ secrets.DOCKERHUB_TOKEN }}" | docker login -u jackgucci --password-stdin
          docker push jackgucci/biomcp:${{ github.ref_name }}
          docker push jackgucci/biomcp:latest
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: true
```

---

## 五、安全审计 Checklist（提交前）
- [ ] 二进制文件 SHA256 校验
- [ ] Docker image 漏洞扫描 (`docker scout quickview`)
- [ ] 无硬编码密钥
- [ ] 非 root 运行
- [ ] Read-only filesystem
- [ ] LICENSE 文件就位
- [ ] CODEOWNERS / SECURITY.md
