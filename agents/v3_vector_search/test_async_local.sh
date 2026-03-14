#!/bin/bash
# Async V3 Local Test Script
# Tüm servisleri başlatır ve test eder

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         V3 Async Orchestrator - Local Test                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Redis is running
echo -e "${YELLOW}[1/5] Checking Redis...${NC}"
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${RED}✗ Redis is not running${NC}"
    echo "Starting Redis..."
    redis-server --daemonize yes
    sleep 2
    
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Redis started${NC}"
    else
        echo -e "${RED}✗ Failed to start Redis${NC}"
        echo "Please install Redis: brew install redis"
        exit 1
    fi
fi

# Check dependencies
echo -e "\n${YELLOW}[2/5] Checking dependencies...${NC}"
if pip list | grep -q celery; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r agents/v3_vector_search/requirements_async.txt
fi

# Redis Cache Warmup (opsiyonel ama önerilen)
echo -e "\n${YELLOW}[2.5/5] Redis Cache Warmup...${NC}"
cd agents/v3_vector_search
python redis_knowledge_cache.py warmup 2>/dev/null || echo -e "${YELLOW}  ⚠️  Cache warmup skipped (MongoDB may not be available)${NC}"

# Start Celery worker in background
echo -e "\n${YELLOW}[3/5] Starting Celery worker...${NC}"

# Kill existing workers
pkill -f "celery.*async_orchestrator_v3" || true

celery -A async_orchestrator_v3.celery_app worker \
    --loglevel=info \
    --concurrency=10 \
    --logfile=celery_worker.log \
    --detach

sleep 3

# Check if worker started
if pgrep -f "celery.*async_orchestrator_v3" > /dev/null; then
    echo -e "${GREEN}✓ Celery worker started${NC}"
else
    echo -e "${RED}✗ Failed to start Celery worker${NC}"
    echo "Check celery_worker.log for errors"
    exit 1
fi

# Start FastAPI in background
echo -e "\n${YELLOW}[4/5] Starting FastAPI...${NC}"

# Kill existing API
pkill -f "uvicorn.*async_orchestrator_v3" || true

uvicorn async_orchestrator_v3:app \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info \
    > fastapi.log 2>&1 &

FASTAPI_PID=$!
sleep 3

# Check if API started
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ FastAPI started (PID: $FASTAPI_PID)${NC}"
else
    echo -e "${RED}✗ Failed to start FastAPI${NC}"
    echo "Check fastapi.log for errors"
    exit 1
fi

# Test analysis
echo -e "\n${YELLOW}[5/5] Running test analysis...${NC}"

RESPONSE=$(curl -s -X POST http://localhost:8000/api/v3/analyze \
    -H "Content-Type: application/json" \
    -d @test_incident.json)

JOB_ID=$(echo $RESPONSE | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$JOB_ID" ]; then
    echo -e "${RED}✗ Failed to start analysis${NC}"
    echo "Response: $RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Analysis started${NC}"
echo "Job ID: $JOB_ID"

# Poll for completion
echo -e "\n${YELLOW}Waiting for analysis to complete...${NC}"
for i in {1..60}; do
    STATUS=$(curl -s http://localhost:8000/api/v3/status/$JOB_ID | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    PROGRESS=$(curl -s http://localhost:8000/api/v3/status/$JOB_ID | grep -o '"progress":[0-9]*' | cut -d':' -f2)
    
    echo -ne "\rProgress: ${PROGRESS}% - Status: $STATUS"
    
    if [ "$STATUS" = "completed" ]; then
        echo -e "\n${GREEN}✓ Analysis completed!${NC}"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo -e "\n${RED}✗ Analysis failed${NC}"
        break
    fi
    
    sleep 5
done

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    Services Running                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 FastAPI:        http://localhost:8000"
echo "📊 Streaming UI:   http://localhost:8000/streaming?job_id=$JOB_ID"
echo "📝 API Docs:       http://localhost:8000/docs"
echo "🔧 Health Check:   http://localhost:8000/health"
echo ""
echo "Logs:"
echo "  FastAPI:  tail -f agents/v3_vector_search/fastapi.log"
echo "  Celery:   tail -f agents/v3_vector_search/celery_worker.log"
echo ""
echo "Stop services:"
echo "  pkill -f 'uvicorn.*async_orchestrator_v3'"
echo "  pkill -f 'celery.*async_orchestrator_v3'"
echo ""
