# Results目录查看脚本使用说明

## 概述

上传项目到HPC后，可以使用这些脚本快速查看results目录的结构和统计信息。

## 使用方法

### 方法1: Python脚本（推荐）

```bash
# 进入项目目录
cd /vast/zg2759/Final_Project

# 使用默认路径（results目录）
python scripts/view_results.py

# 或指定自定义路径
python scripts/view_results.py /path/to/results
```

### 方法2: Bash脚本

```bash
# 进入项目目录
cd /vast/zg2759/Final_Project

# 使用默认路径
bash scripts/view_results.sh

# 或指定自定义路径
bash scripts/view_results.sh /path/to/results
```

## 脚本功能

脚本会显示以下信息：

1. **目录结构** - 以树形结构显示results目录
2. **文件统计** - 总文件数和目录数
3. **每个目录的文件数** - 按目录统计文件数量
4. **按模型/实验分组** - 显示每个模型和实验条件的文件数
5. **磁盘使用情况** - results目录的总大小
6. **示例文件** - 显示前10个CSV文件
7. **文件类型统计** - 按文件扩展名统计

## 示例输出

```
============================================================
Results Directory Structure Viewer
============================================================

✓ Found results directory: /vast/zg2759/Final_Project/results
Absolute path: /vast/zg2759/Final_Project/results

============================================================
Directory Structure
============================================================
results
└── predictions
    ├── librosa
    │   ├── clean
    │   ├── distortion
    │   └── noise
    └── librosa_normalized
        ├── clean
        └── distortion

============================================================
File Statistics
============================================================
Total files: 517
Total directories: 8

============================================================
Breakdown by Model/Experiment
============================================================
librosa:
  └─ clean                                   103 files
  └─ distortion                               103 files
  └─ noise/5db                               103 files

librosa_normalized:
  └─ clean                                   103 files
  └─ distortion                                65 files
```

## 常见问题

### Q: 脚本找不到results目录？
A: 确保你在项目根目录运行脚本，或者使用绝对路径：
```bash
python scripts/view_results.py /vast/zg2759/Final_Project/results
```

### Q: 权限错误？
A: 确保脚本有执行权限：
```bash
chmod +x scripts/view_results.sh
chmod +x scripts/view_results.py
```

### Q: Python脚本报错？
A: 确保Python版本 >= 3.6：
```bash
python --version
python3 --version
```

## 快速检查命令

如果只想快速查看，也可以直接使用命令行：

```bash
# 查看目录结构
tree results/ -L 3
# 或
find results/ -type d | head -20

# 统计文件数
find results/ -type f | wc -l

# 查看每个子目录的文件数
find results/predictions -type d -exec sh -c 'echo "{}: $(find {} -type f | wc -l) files"' \;
```




