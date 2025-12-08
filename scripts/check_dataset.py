#!/usr/bin/env python3
"""
检查数据集结构完整性
"""

from pathlib import Path
import sys

def check_directory(path, description):
    """检查目录是否存在"""
    p = Path(path)
    if p.exists() and p.is_dir():
        files = list(p.glob("*"))
        wav_files = list(p.glob("*.wav"))
        csv_files = list(p.glob("*.csv"))
        return True, len(files), len(wav_files), len(csv_files)
    return False, 0, 0, 0

def main():
    print("=" * 70)
    print("数据集结构检查")
    print("=" * 70)
    print()
    
    all_ok = True
    
    # MedleyDB-Pitch
    print("【MedleyDB-Pitch】")
    print("-" * 70)
    
    audio_ok, audio_total, audio_wav, _ = check_directory("MedleyDB-Pitch/audio", "Audio目录")
    pitch_ok, pitch_total, _, pitch_csv = check_directory("MedleyDB-Pitch/pitch", "Pitch目录")
    
    if audio_ok:
        print(f"✓ audio/         存在 - {audio_wav} 个WAV文件")
    else:
        print(f"✗ audio/         缺失")
        all_ok = False
    
    if pitch_ok:
        print(f"✓ pitch/         存在 - {pitch_csv} 个CSV文件")
    else:
        print(f"✗ pitch/         缺失")
        all_ok = False
    
    print()
    
    # MedleyDB-Pitch-Experiments
    print("【MedleyDB-Pitch-Experiments】")
    print("-" * 70)
    
    experiments = [
        ("distortion/audio", "Distortion音频"),
        ("noise/5db/audio", "Noise 5dB音频"),
        ("noise/15db/audio", "Noise 15dB音频"),
        ("pitch_shift/25cents/audio", "Pitch Shift 25cents音频"),
        ("pitch_shift/50cents/audio", "Pitch Shift 50cents音频"),
        ("pitch", "Ground Truth Pitch"),
    ]
    
    for rel_path, desc in experiments:
        full_path = f"MedleyDB-Pitch-Experiments/{rel_path}"
        ok, total, wav_count, csv_count = check_directory(full_path, desc)
        
        if ok:
            if wav_count > 0:
                print(f"✓ {rel_path:<30} 存在 - {wav_count} 个WAV文件")
            elif csv_count > 0:
                print(f"✓ {rel_path:<30} 存在 - {csv_count} 个CSV文件")
            else:
                print(f"✓ {rel_path:<30} 存在 - {total} 个文件")
        else:
            print(f"✗ {rel_path:<30} 缺失")
            all_ok = False
    
    print()
    
    # 总结
    print("=" * 70)
    if all_ok:
        print("✓ 所有必需的目录都存在！")
        print()
        print("数据集结构完整，可以运行pipeline。")
    else:
        print("✗ 发现缺失的目录！")
        print()
        print("请检查上述标记为 ✗ 的目录。")
        sys.exit(1)
    print("=" * 70)

if __name__ == "__main__":
    main()




