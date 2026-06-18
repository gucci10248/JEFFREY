# BioMCP Security Policy

## Supported Versions

Only the latest release is actively supported. Critical security patches are backported to the prior minor version for 30 days.

| Version | Supported |
|---------|-----------|
| 0.8.x   | ✅ Active |
| < 0.8   | ❌ Unsupported |

## Reporting a Vulnerability

**Do not open a public issue.** Send vulnerability reports to:

📧 `gucci10248@proton.me`

Expect acknowledgment within 48 hours and a fix within 7 days for critical vulnerabilities.

## Architecture Safety

BioMCP is a **read-only** MCP server. It:

- Never mutates upstream biomedical databases
- Never collects telemetry or user data
- Never makes outbound calls except to public biomedical APIs you explicitly query
- Runs as a non-root user inside Docker with a read-only root filesystem

## Dependency Chain

- Single static binary — no runtime package managers (npm, pip, gem)
- Build-time dependencies are pinned via `Cargo.lock`
- Docker base image: `alpine:3.20` (minimal attack surface)

## Disclosure Policy

We publish advisories on GitHub Security Advisories after a fix is released. Commercial users subscribed to Pro/Team plans receive advance notice.
