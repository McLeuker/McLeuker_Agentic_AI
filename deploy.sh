#!/bin/bash
# McLeuker AI - Kimi 2.5 Deployment Script
# This script deploys the Kimi 2.5 backend to Railway

set -e

echo "McLeuker AI - Kimi 2.5 Deployment"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "apps/backend/main.py" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command_exists git; then
    echo -e "${RED}Error: git is not installed${NC}"
    exit 1
fi

if ! command_exists curl; then
    echo -e "${RED}Error: curl is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}Prerequisites check passed${NC}"

# Test Kimi API Key (from environment)
if [ -n "$KIMI_API_KEY" ]; then
    echo -e "${YELLOW}Testing Kimi API connection...${NC}"
    KIMI_TEST=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $KIMI_API_KEY" \
        https://api.moonshot.cn/v1/models)

    if [ "$KIMI_TEST" = "200" ]; then
        echo -e "${GREEN}Kimi API connection successful${NC}"
    else
        echo -e "${RED}Kimi API connection failed (HTTP $KIMI_TEST)${NC}"
        echo "Please check your KIMI_API_KEY environment variable"
    fi
else
    echo -e "${YELLOW}KIMI_API_KEY not set in environment - skipping API test${NC}"
fi

# Git operations
echo -e "${YELLOW}Preparing Git commit...${NC}"

# Configure git if not already done
if [ -z "$(git config --global user.email)" ]; then
    git config user.email "deploy@mcleuker.ai"
    git config user.name "McLeuker Deploy"
fi

# Add all changes
git add -A

# Commit
git commit -m "feat: Upgrade to Kimi 2.5 with multimodal, agent swarm, and vision-to-code capabilities

- Replace Grok with Kimi 2.5 (1T MoE, 256K context)
- Add Instant/Thinking/Agent/Swarm modes
- Implement Agent Swarm orchestrator (up to 20 parallel agents)
- Add Vision-to-Code pipeline (UI image to HTML/React/Vue)
- Add multimodal support (text + image)
- Integrate web search and perplexity tools
- Maintain backward compatibility with existing frontend
- Update API client with new endpoints

BREAKING CHANGE: Backend model changed from Grok to Kimi 2.5" || echo "No changes to commit"

# Push to GitHub
echo -e "${YELLOW}Pushing to GitHub...${NC}"
git push origin main
echo -e "${GREEN}Code pushed to GitHub${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment preparation complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Railway will auto-deploy from GitHub"
echo "2. Monitor deployment at: https://railway.app/dashboard"
echo "3. Verify health endpoint: https://web-production-29f3c.up.railway.app/api/v1/health"
echo ""
echo "API Endpoints available:"
echo "  - POST /api/chat/stream (Legacy streaming - backward compatible)"
echo "  - POST /api/v1/chat (Instant/Thinking/Agent modes)"
echo "  - POST /api/v1/swarm (Multi-agent tasks)"
echo "  - POST /api/v1/vision-to-code (Image to code)"
echo "  - POST /api/v1/multimodal (Text + Image)"
echo "  - POST /api/v1/research (Deep research)"
echo "  - GET  /api/v1/health (Status check)"
echo "  - POST /api/image/generate (Image generation)"
echo "  - POST /api/document/generate (Document generation)"
