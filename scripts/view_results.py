#!/usr/bin/env python3
"""
View results directory structure on HPC
Usage: python scripts/view_results.py [results_path]
"""

import os
import sys
from pathlib import Path
from collections import defaultdict


def format_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def count_files(directory):
    """Count files in a directory"""
    return len([f for f in directory.iterdir() if f.is_file()])


def get_dir_size(directory):
    """Get total size of directory"""
    total = 0
    try:
        for entry in directory.rglob('*'):
            if entry.is_file():
                total += entry.stat().st_size
    except (PermissionError, OSError):
        pass
    return total


def print_tree(directory, prefix="", max_depth=4, current_depth=0):
    """Print directory tree structure"""
    if current_depth >= max_depth:
        return
    
    try:
        entries = sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name))
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{entry.name}")
            
            if entry.is_dir():
                next_prefix = prefix + ("    " if is_last else "│   ")
                print_tree(entry, next_prefix, max_depth, current_depth + 1)
    except (PermissionError, OSError):
        pass


def main():
    # Get results path from argument or use default
    if len(sys.argv) > 1:
        results_path = Path(sys.argv[1])
    else:
        results_path = Path("results")
    
    # Check if results directory exists
    if not results_path.exists():
        print(f"⚠️  Warning: Results directory '{results_path}' not found!")
        print("\nSearching for results directory...")
        
        # Search for results directory
        current_dir = Path.cwd()
        found = list(current_dir.rglob("results"))
        if found:
            print("Found potential results directories:")
            for p in found[:5]:
                print(f"  - {p}")
        else:
            print("  No results directory found.")
        
        print("\nPlease specify the correct path:")
        print(f"  python scripts/view_results.py /path/to/results")
        sys.exit(1)
    
    results_path = results_path.resolve()
    
    print("=" * 60)
    print("Results Directory Structure Viewer")
    print("=" * 60)
    print(f"\n✓ Found results directory: {results_path}")
    print(f"Absolute path: {results_path}")
    print()
    
    # Display directory structure
    print("=" * 60)
    print("Directory Structure")
    print("=" * 60)
    print(results_path.name)
    print_tree(results_path, max_depth=4)
    print()
    
    # Count total files
    print("=" * 60)
    print("File Statistics")
    print("=" * 60)
    all_files = list(results_path.rglob("*"))
    files = [f for f in all_files if f.is_file()]
    dirs = [d for d in all_files if d.is_dir()]
    
    print(f"Total files: {len(files)}")
    print(f"Total directories: {len(dirs)}")
    print()
    
    # Count files by subdirectory
    print("=" * 60)
    print("Files per Directory")
    print("=" * 60)
    dir_file_counts = {}
    for directory in dirs:
        file_count = count_files(directory)
        if file_count > 0:
            rel_path = directory.relative_to(results_path)
            dir_file_counts[rel_path] = file_count
    
    # Sort by file count
    for dir_path, count in sorted(dir_file_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {str(dir_path):<60} {count:>5} files")
    print()
    
    # Breakdown by model/experiment
    print("=" * 60)
    print("Breakdown by Model/Experiment")
    print("=" * 60)
    predictions_dir = results_path / "predictions"
    if predictions_dir.exists():
        for model_dir in sorted(predictions_dir.iterdir()):
            if model_dir.is_dir():
                model_name = model_dir.name
                print(f"\n{model_name}:")
                
                # Count files in each experiment subdirectory
                exp_counts = {}
                for exp_dir in model_dir.rglob("*"):
                    if exp_dir.is_dir() and exp_dir != model_dir:
                        file_count = count_files(exp_dir)
                        if file_count > 0:
                            rel_exp = exp_dir.relative_to(model_dir)
                            exp_counts[rel_exp] = file_count
                
                for exp_path, count in sorted(exp_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"  └─ {str(exp_path):<50} {count:>5} files")
    print()
    
    # Disk usage
    print("=" * 60)
    print("Disk Usage")
    print("=" * 60)
    try:
        total_size = get_dir_size(results_path)
        print(f"Total size: {format_size(total_size)}")
    except Exception as e:
        print(f"Unable to calculate disk usage: {e}")
    print()
    
    # Sample files
    print("=" * 60)
    print("Sample Files (first 10)")
    print("=" * 60)
    csv_files = [f for f in files if f.suffix == '.csv']
    for file_path in sorted(csv_files)[:10]:
        rel_file = file_path.relative_to(results_path)
        try:
            size = file_path.stat().st_size
            print(f"  {str(rel_file):<60} {format_size(size)}")
        except Exception:
            print(f"  {str(rel_file):<60} (size unknown)")
    print()
    
    # File type summary
    print("=" * 60)
    print("File Type Summary")
    print("=" * 60)
    file_types = defaultdict(int)
    for file_path in files:
        ext = file_path.suffix or "(no extension)"
        file_types[ext] += 1
    
    for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ext:<20} {count:>5} files")
    print()
    
    print("=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()




