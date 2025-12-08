#!/bin/bash
# Script to view results directory structure on HPC
# Usage: ./scripts/view_results.sh [results_path]

set -e

# Default results path (can be overridden by argument)
RESULTS_PATH="${1:-results}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Results Directory Structure Viewer"
echo "=========================================="
echo ""

# Check if results directory exists
if [ ! -d "$RESULTS_PATH" ]; then
    echo -e "${YELLOW}Warning: Results directory '$RESULTS_PATH' not found!${NC}"
    echo ""
    echo "Searching for results directory..."
    find . -maxdepth 3 -type d -name "results" 2>/dev/null | head -5
    echo ""
    echo "Please specify the correct path:"
    echo "  ./scripts/view_results.sh /path/to/results"
    exit 1
fi

echo -e "${GREEN}✓ Found results directory: $RESULTS_PATH${NC}"
echo ""

# Get absolute path
ABS_PATH=$(cd "$RESULTS_PATH" && pwd)
echo "Absolute path: $ABS_PATH"
echo ""

# Display directory structure
echo -e "${BLUE}=== Directory Structure ===${NC}"
if command -v tree &> /dev/null; then
    tree -L 4 "$RESULTS_PATH" 2>/dev/null || find "$RESULTS_PATH" -type d | sed 's|[^/]*/| |g' | head -50
else
    find "$RESULTS_PATH" -type d | sed 's|[^/]*/| |g' | head -50
fi
echo ""

# Count total files
echo -e "${BLUE}=== File Statistics ===${NC}"
TOTAL_FILES=$(find "$RESULTS_PATH" -type f | wc -l)
echo "Total files: $TOTAL_FILES"
echo ""

# Count files by subdirectory
echo -e "${BLUE}=== Files per Directory ===${NC}"
find "$RESULTS_PATH" -type d | while read dir; do
    count=$(find "$dir" -maxdepth 1 -type f | wc -l)
    if [ "$count" -gt 0 ]; then
        rel_path=$(realpath --relative-to="$RESULTS_PATH" "$dir" 2>/dev/null || echo "$dir")
        printf "  %-60s %5d files\n" "$rel_path" "$count"
    fi
done
echo ""

# Show breakdown by model/experiment
echo -e "${BLUE}=== Breakdown by Model/Experiment ===${NC}"
if [ -d "$RESULTS_PATH/predictions" ]; then
    for model_dir in "$RESULTS_PATH/predictions"/*; do
        if [ -d "$model_dir" ]; then
            model_name=$(basename "$model_dir")
            echo -e "${GREEN}$model_name:${NC}"
            
            # Count files in each experiment subdirectory
            find "$model_dir" -mindepth 1 -maxdepth 2 -type d | while read exp_dir; do
                exp_name=$(realpath --relative-to="$model_dir" "$exp_dir" 2>/dev/null || basename "$exp_dir")
                file_count=$(find "$exp_dir" -maxdepth 1 -type f | wc -l)
                if [ "$file_count" -gt 0 ]; then
                    printf "  %-50s %5d files\n" "  └─ $exp_name" "$file_count"
                fi
            done
            echo ""
        fi
    done
fi

# Show disk usage
echo -e "${BLUE}=== Disk Usage ===${NC}"
du -sh "$RESULTS_PATH" 2>/dev/null || echo "Unable to calculate disk usage"
echo ""

# Show sample files
echo -e "${BLUE}=== Sample Files (first 10) ===${NC}"
find "$RESULTS_PATH" -type f -name "*.csv" | head -10 | while read file; do
    rel_file=$(realpath --relative-to="$RESULTS_PATH" "$file" 2>/dev/null || echo "$file")
    size=$(ls -lh "$file" | awk '{print $5}')
    echo "  $rel_file ($size)"
done
echo ""

# Check for common file patterns
echo -e "${BLUE}=== File Type Summary ===${NC}"
find "$RESULTS_PATH" -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -10 | while read count ext; do
    printf "  %-20s %5d files\n" ".$ext" "$count"
done
echo ""

echo "=========================================="
echo "Done!"
echo "=========================================="




