#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 Classification Assignment Status${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check Ollama notebook process
OLLAMA_PID=$(pgrep -f "classification_ollama.ipynb")
if [ ! -z "$OLLAMA_PID" ]; then
    echo -e "${YELLOW}⏳ Ollama Notebook: RUNNING${NC}"
    ps aux | grep "$OLLAMA_PID" | grep -v grep | awk '{print "   PID: " $2 " | CPU: " $3"% | Memory: " $6" KB | Elapsed: " $11}'
else
    echo -e "${GREEN}✅ Ollama Notebook: COMPLETED${NC}"
fi
echo ""

# Check output file
OUTPUT_FILE="data/export/ai_cleaned-up/ollama.csv"
if [ -f "$OUTPUT_FILE" ]; then
    LINE_COUNT=$(wc -l < "$OUTPUT_FILE")
    echo -e "${GREEN}✅ Output CSV: CREATED${NC}"
    echo -e "   Path: ${OUTPUT_FILE}"
    echo -e "   Lines: ${LINE_COUNT} (expected: 51 = 1 header + 50 videos)"
    echo -e "   Size: $(ls -lh "$OUTPUT_FILE" | awk '{print $5}')"
else
    echo -e "${RED}❌ Output CSV: NOT YET CREATED${NC}"
    echo -e "   Expected: ${OUTPUT_FILE}"
fi
echo ""

# Check human annotations
echo -e "${BLUE}📝 Human Annotations:${NC}"
if [ -f "data/export/human/Camila.csv" ]; then
    echo -e "   ${GREEN}✅ Camila.csv${NC} ($(wc -l < data/export/human/Camila.csv) lines)"
else
    echo -e "   ${RED}❌ Camila.csv${NC}"
fi

if [ -f "data/export/human/Jack.csv" ]; then
    echo -e "   ${GREEN}✅ Jack.csv${NC} ($(wc -l < data/export/human/Jack.csv) lines)"
else
    echo -e "   ${RED}❌ Jack.csv${NC}"
fi
echo ""

# Check if ready for next step
if [ -f "$OUTPUT_FILE" ] && [ -f "data/export/human/Camila.csv" ]; then
    echo -e "${GREEN}✅ Ready for next step:${NC}"
    echo "   Run: python -m jupyter nbconvert --to notebook --execute --inplace scripts/review/intercoder_reliability.ipynb"
else
    echo -e "${YELLOW}⏳ Waiting for:${NC}"
    [ ! -f "$OUTPUT_FILE" ] && echo "   - Ollama notebook to complete"
    [ ! -f "data/export/human/Camila.csv" ] && echo "   - More human annotations"
fi
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
