#!/bin/bash

# Fix script for malformed frontend directories
# Run this if you extracted an older version of the zip file

echo "=================================="
echo "Frontend Directory Structure Fix"
echo "=================================="
echo ""

cd "$(dirname "$0")"

if [ -d "frontend/{public,src" ] || [ -d "frontend/{public,src/{components,pages,services,context,utils}}" ]; then
    echo "🔧 Found malformed directories, removing them..."
    cd frontend
    rm -rf "{public,src" "{public,src/{components,pages,services,context,utils}}"
    cd ..
    echo "✅ Malformed directories removed"
else
    echo "✅ No malformed directories found"
fi

# Verify structure
echo ""
echo "📁 Current frontend structure:"
ls -la frontend/

echo ""
echo "📄 Source files:"
find frontend/src -type f 2>/dev/null || echo "No src directory found"

echo ""
echo "✅ Directory structure is now correct!"
echo ""
echo "🚀 You can now run: docker-compose up -d --build"
echo ""
