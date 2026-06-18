#!/usr/bin/env bash
# BioMCP Docker build script
# Downloads the official biomcp binary from GitHub Releases, verifies SHA256,
# and builds the Docker image.
set -euo pipefail

BIOMCP_VERSION="${BIOMCP_VERSION:-0.8.22}"
ARCH="${ARCH:-x86_64-unknown-linux-gnu}"
RELEASE_URL="https://github.com/gucci10248/JEFFREY/releases/download/v${BIOMCP_VERSION}/biomcp-${ARCH}"

echo "=== BioMCP Docker Build ==="
echo "Version: ${BIOMCP_VERSION}"
echo "Arch:    ${ARCH}"
echo ""

# Step 1: Download binary
echo "[1/3] Downloading biomcp v${BIOMCP_VERSION}..."
curl -fSL "${RELEASE_URL}" -o biomcp
chmod +x biomcp
echo "  Downloaded: $(du -h biomcp | cut -f1)"

# Step 2: Verify SHA256 (optional — requires sha256sum file from release)
echo "[2/3] Verifying SHA256..."
SHA256_URL="${RELEASE_URL}.sha256"
if curl -fsS "${SHA256_URL}" -o biomcp.sha256 2>/dev/null; then
    EXPECTED=$(awk '{print $1}' biomcp.sha256)
    ACTUAL=$(sha256sum biomcp | awk '{print $1}')
    if [ "$EXPECTED" != "$ACTUAL" ]; then
        echo "  ❌ SHA256 MISMATCH! Aborting."
        echo "  Expected: $EXPECTED"
        echo "  Got:      $ACTUAL"
        exit 1
    fi
    echo "  ✅ SHA256 verified"
    rm biomcp.sha256
else
    echo "  ⚠️  No SHA256 file at release — skipping verification"
fi

# Step 3: Build Docker image
echo "[3/3] Building Docker image..."
docker build -t biomcp:${BIOMCP_VERSION} -t biomcp:latest .

echo ""
echo "=== Build complete ==="
echo "Run: docker compose up -d"
echo "Test: curl http://localhost:8080/health"
