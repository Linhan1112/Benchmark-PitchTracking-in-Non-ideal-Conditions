# Librosa vs Basic Pitch 评估结果对比表

## 详细对比表

| 实验条件 | 方法 | OA (%) | RPA (%) | RCA (%) | VR (%) | 文件数 |
|---------|------|--------|---------|---------|--------|--------|
| clean | Librosa | 65.89 | 85.12 | 79.66 | 72.34 | 83 |
| clean | Basic Pitch | 72.16 | 79.23 | 77.24 | 79.78 | 83 |
| clean | **差异 (BP-L)** | **+6.27** | **-5.88** | **-2.41** | **+7.45** | - |
| distortion | Librosa | 67.03 | 86.46 | 80.92 | 72.59 | 104 |
| distortion | Basic Pitch | 72.37 | 80.98 | 79.42 | 79.14 | 104 |
| distortion | **差异 (BP-L)** | **+5.34** | **-5.48** | **-1.50** | **+6.54** | - |
| noise_5db | Librosa | 64.53 | 74.25 | 66.96 | 70.69 | 104 |
| noise_5db | Basic Pitch | 75.99 | 73.93 | 71.49 | 80.57 | 104 |
| noise_5db | **差异 (BP-L)** | **+11.46** | **-0.32** | **+4.52** | **+9.88** | - |
| noise_15db | Librosa | 69.33 | 84.63 | 77.98 | 75.42 | 43 |
| noise_15db | Basic Pitch | 76.49 | 75.91 | 73.19 | 82.42 | 43 |
| noise_15db | **差异 (BP-L)** | **+7.16** | **-8.72** | **-4.79** | **+6.99** | - |
| pitch_shift_25cents | Librosa | 64.57 | 80.73 | 73.26 | 72.81 | 104 |
| pitch_shift_25cents | Basic Pitch | 71.01 | 73.08 | 70.28 | 79.43 | 104 |
| pitch_shift_25cents | **差异 (BP-L)** | **+6.45** | **-7.65** | **-2.99** | **+6.61** | - |
| pitch_shift_50cents | Librosa | 47.46 | 47.12 | 44.80 | 69.72 | 42 |
| pitch_shift_50cents | Basic Pitch | 58.26 | 42.67 | 40.26 | 77.87 | 42 |
| pitch_shift_50cents | **差异 (BP-L)** | **+10.80** | **-4.45** | **-4.55** | **+8.15** | - |

## 汇总对比表（按指标）

### Overall Accuracy (OA)

| 实验条件 | Librosa | Basic Pitch | 差异 |
|---------|---------|-------------|------|
| clean | 65.89% | 72.16% | **+6.27%** |
| distortion | 67.03% | 72.37% | **+5.34%** |
| noise_5db | 64.53% | 75.99% | **+11.46%** |
| noise_15db | 69.33% | 76.49% | **+7.16%** |
| pitch_shift_25cents | 64.57% | 71.01% | **+6.45%** |
| pitch_shift_50cents | 47.46% | 58.26% | **+10.80%** |

### Raw Pitch Accuracy (RPA)

| 实验条件 | Librosa | Basic Pitch | 差异 |
|---------|---------|-------------|------|
| clean | 85.12% | 79.23% | **-5.88%** |
| distortion | 86.46% | 80.98% | **-5.48%** |
| noise_5db | 74.25% | 73.93% | **-0.32%** |
| noise_15db | 84.63% | 75.91% | **-8.72%** |
| pitch_shift_25cents | 80.73% | 73.08% | **-7.65%** |
| pitch_shift_50cents | 47.12% | 42.67% | **-4.45%** |

### Raw Chroma Accuracy (RCA)

| 实验条件 | Librosa | Basic Pitch | 差异 |
|---------|---------|-------------|------|
| clean | 79.66% | 77.24% | **-2.41%** |
| distortion | 80.92% | 79.42% | **-1.50%** |
| noise_5db | 66.96% | 71.49% | **+4.52%** |
| noise_15db | 77.98% | 73.19% | **-4.79%** |
| pitch_shift_25cents | 73.26% | 70.28% | **-2.99%** |
| pitch_shift_50cents | 44.80% | 40.26% | **-4.55%** |

### Voicing Recall (VR)

| 实验条件 | Librosa | Basic Pitch | 差异 |
|---------|---------|-------------|------|
| clean | 72.34% | 79.78% | **+7.45%** |
| distortion | 72.59% | 79.14% | **+6.54%** |
| noise_5db | 70.69% | 80.57% | **+9.88%** |
| noise_15db | 75.42% | 82.42% | **+6.99%** |
| pitch_shift_25cents | 72.81% | 79.43% | **+6.61%** |
| pitch_shift_50cents | 69.72% | 77.87% | **+8.15%** |

## 主要发现

1. **Overall Accuracy (OA)**: Basic Pitch 在所有条件下都优于 Librosa，特别是在噪声条件下（noise_5db: +11.46%）

2. **Raw Pitch Accuracy (RPA)**: Librosa 在大多数条件下略优于 Basic Pitch，但在 noise_5db 条件下两者接近

3. **Raw Chroma Accuracy (RCA)**: 在 noise_5db 条件下，Basic Pitch 优于 Librosa (+4.52%)，其他条件下 Librosa 略优

4. **Voicing Recall (VR)**: Basic Pitch 在所有条件下都明显优于 Librosa，说明在检测有声段方面更稳定

5. **极端条件**: 在 pitch_shift_50cents 条件下，两种方法表现都较差，但 Basic Pitch 的 OA 和 VR 更高

## 指标说明

- **OA (Overall Accuracy)**: 总体准确率，考虑有声/无声
- **RPA (Raw Pitch Accuracy)**: 原始音高准确率，50 cents 容差
- **RCA (Raw Chroma Accuracy)**: 原始音级准确率（音高类别）
- **VR (Voicing Recall)**: 有声召回率

