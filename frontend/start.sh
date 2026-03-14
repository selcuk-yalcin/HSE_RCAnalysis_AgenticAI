#!/bin/bash

# HSE Root Cause Analysis AI - Frontend Quick Start Script
# This script sets up and starts the React frontend

set -e  # Exit on error

echo "🚀 HSE RCA AI - Frontend Quick Start"
echo "===================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    echo "   Download from: https://nodejs.org/"
    exit 1
fi

# Check Node version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js version 16+ required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"
echo "✅ npm version: $(npm -v)"
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Check if backend is running
echo "🔍 Checking backend connection..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running on port 8000"
else
    echo "⚠️  Backend not detected on port 8000"
    echo "   Please start the backend server first:"
    echo "   cd .. && python api/main.py"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "🎨 Starting development server..."
echo ""
echo "📍 Frontend will be available at:"
echo "   http://localhost:3000"
echo ""
echo "📡 API proxy configured:"
echo "   /api → http://localhost:8000"
echo "   /ws  → ws://localhost:8000"
echo ""
echo "🌍 Supported languages:"
echo "   🇹🇷 Turkish (TR)"
echo "   🇬🇧 English (EN)"
echo "   🇩🇪 German (DE)"
echo "   🇫🇷 French (FR)"
echo "   🇪🇸 Spanish (ES)"
echo "   🇸🇦 Arabic (AR)"
echo ""
echo "Press Ctrl+C to stop the server"
echo "===================================="
echo ""

# Start development server
npm run dev
