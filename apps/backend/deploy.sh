#!/bin/bash

# McLeuker Agentic AI - Critical Fixes Deployment Script
# =======================================================
# This script applies all critical fixes to the repository

set -e

echo "=========================================="
echo "McLeuker Agentic AI - Fix Deployment"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -d "apps" ]; then
    print_error "Please run this script from the repository root directory"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_status "Fix directory: $SCRIPT_DIR"
print_status "Repository root: $(pwd)"
echo ""

# ============================================
# Step 1: Backup existing files
# ============================================
print_status "Step 1: Backing up existing files..."

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup backend files
if [ -f "apps/backend/src/api/main_v8.py" ]; then
    cp apps/backend/src/api/main_v8.py "$BACKUP_DIR/"
    print_status "Backed up main_v8.py"
fi

if [ -f "apps/backend/src/api/agentic_routes.py" ]; then
    cp apps/backend/src/api/agentic_routes.py "$BACKUP_DIR/"
    print_status "Backed up agentic_routes.py"
fi

if [ -f "apps/backend/src/tools/code/github_tools.py" ]; then
    cp apps/backend/src/tools/code/github_tools.py "$BACKUP_DIR/"
    print_status "Backed up github_tools.py"
fi

# Backup frontend files
if [ -f "apps/frontend/src/components/agent/ExecutionPanel.tsx" ]; then
    cp apps/frontend/src/components/agent/ExecutionPanel.tsx "$BACKUP_DIR/"
    print_status "Backed up ExecutionPanel.tsx"
fi

print_status "Backups saved to: $BACKUP_DIR"
echo ""

# ============================================
# Step 2: Apply backend fixes
# ============================================
print_status "Step 2: Applying backend fixes..."

# Fix main_v8.py
if [ -f "$SCRIPT_DIR/backend/main_v8_fixed.py" ]; then
    cp "$SCRIPT_DIR/backend/main_v8_fixed.py" apps/backend/src/api/main_v8.py
    print_status "Applied main_v8.py fixes (WebSocket endpoint, file download)"
else
    print_error "main_v8_fixed.py not found in fix directory"
    exit 1
fi

# Fix agentic_routes.py
if [ -f "$SCRIPT_DIR/backend/agentic_routes_fixed.py" ]; then
    cp "$SCRIPT_DIR/backend/agentic_routes_fixed.py" apps/backend/src/api/agentic_routes.py
    print_status "Applied agentic_routes.py fixes (FileGenerationService integration)"
else
    print_error "agentic_routes_fixed.py not found in fix directory"
    exit 1
fi

# Fix github_tools.py
if [ -f "$SCRIPT_DIR/backend/github_tools_fixed.py" ]; then
    cp "$SCRIPT_DIR/backend/github_tools_fixed.py" apps/backend/src/tools/code/github_tools.py
    print_status "Applied github_tools.py fixes (file operation parsing)"
else
    print_error "github_tools_fixed.py not found in fix directory"
    exit 1
fi

echo ""

# ============================================
# Step 3: Apply frontend fixes
# ============================================
print_status "Step 3: Applying frontend fixes..."

# Create FileAttachment component
if [ -f "$SCRIPT_DIR/frontend/FileAttachment.tsx" ]; then
    cp "$SCRIPT_DIR/frontend/FileAttachment.tsx" apps/frontend/src/components/agent/FileAttachment.tsx
    print_status "Created FileAttachment.tsx component"
else
    print_error "FileAttachment.tsx not found in fix directory"
    exit 1
fi

# Fix ExecutionPanel.tsx
if [ -f "$SCRIPT_DIR/frontend/ExecutionPanel_fixed.tsx" ]; then
    cp "$SCRIPT_DIR/frontend/ExecutionPanel_fixed.tsx" apps/frontend/src/components/agent/ExecutionPanel.tsx
    print_status "Applied ExecutionPanel.tsx fixes (file handling, WebSocket)"
else
    print_error "ExecutionPanel_fixed.tsx not found in fix directory"
    exit 1
fi

echo ""

# ============================================
# Step 4: Update requirements.txt
# ============================================
print_status "Step 4: Checking requirements.txt..."

REQUIREMENTS_FILE="apps/backend/requirements.txt"

if [ -f "$REQUIREMENTS_FILE" ]; then
    # Check if required packages are present
    REQUIRED_PKGS=("python-docx" "python-pptx" "openpyxl" "fpdf2" "playwright")
    
    for pkg in "${REQUIRED_PKGS[@]}"; do
        if ! grep -q "$pkg" "$REQUIREMENTS_FILE"; then
            print_warning "Adding $pkg to requirements.txt"
            echo "$pkg>=0.0.1" >> "$REQUIREMENTS_FILE"
        fi
    done
    
    print_status "requirements.txt updated"
else
    print_warning "requirements.txt not found, skipping"
fi

echo ""

# ============================================
# Step 5: Verify fixes
# ============================================
print_status "Step 5: Verifying fixes..."

# Check backend files
if grep -q "/api/v2/ws/execute" apps/backend/src/api/main_v8.py; then
    print_status "✓ WebSocket endpoint fixed"
else
    print_error "✗ WebSocket endpoint not found"
fi

if grep -q "FileGenerationService" apps/backend/src/api/agentic_routes.py; then
    print_status "✓ FileGenerationService integrated"
else
    print_error "✗ FileGenerationService not found"
fi

if grep -q "parse_file_operations" apps/backend/src/tools/code/github_tools.py; then
    print_status "✓ GitHub tools fixed"
else
    print_error "✗ GitHub tools not fixed"
fi

# Check frontend files
if [ -f "apps/frontend/src/components/agent/FileAttachment.tsx" ]; then
    print_status "✓ FileAttachment component created"
else
    print_error "✗ FileAttachment component not found"
fi

if grep -q "generated_files" apps/frontend/src/components/agent/ExecutionPanel.tsx; then
    print_status "✓ ExecutionPanel file handling fixed"
else
    print_error "✗ ExecutionPanel file handling not found"
fi

echo ""

# ============================================
# Step 6: Build frontend
# ============================================
print_status "Step 6: Building frontend..."

cd apps/frontend

if [ -f "package.json" ]; then
    print_status "Installing dependencies..."
    npm install
    
    print_status "Building..."
    npm run build
    
    if [ $? -eq 0 ]; then
        print_status "Frontend build successful"
    else
        print_error "Frontend build failed"
        exit 1
    fi
else
    print_warning "package.json not found, skipping frontend build"
fi

cd ../..

echo ""

# ============================================
# Step 7: Final instructions
# ============================================
print_status "Step 7: Deployment complete!"
echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Commit the changes:"
echo "   git add -A"
echo "   git commit -m 'Apply critical fixes v8.5.1'"
echo "   git push"
echo ""
echo "2. Deploy to Railway:"
echo "   railway up"
echo ""
echo "3. Verify deployment:"
echo "   - Check health endpoint: /health"
echo "   - Test WebSocket: /api/v2/ws/execute/test"
echo "   - Test file generation: /api/v1/files/generate"
echo ""
echo "4. Environment variables to set:"
echo "   - KIMI_API_KEY (required)"
echo "   - GITHUB_TOKEN (for GitHub push)"
echo "   - RAILWAY_PUBLIC_URL (for file downloads)"
echo ""
echo "=========================================="
echo "Fixes Applied:"
echo "=========================================="
echo "✓ Issue 1: WebSocket endpoint path fixed"
echo "✓ Issue 2: FileGenerationService integrated"
echo "✓ Issue 3: GitHub push parsing fixed"
echo "✓ Issue 4: FileAttachment component created"
echo "✓ Issue 5: ExecutionPanel file handling fixed"
echo ""
echo "Version: 8.5.1-fixed"
echo "Backup location: $BACKUP_DIR"
echo "=========================================="
