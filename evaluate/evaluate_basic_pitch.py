#!/usr/bin/env python3
"""
Evaluate Basic Pitch predictions.

This script evaluates Basic Pitch predictions across different experimental conditions:
- Clean (baseline)
- Distortion
- Noise (5db, 15db)
- Pitch Shift (25cents, 50cents)

Metrics computed:
- OA (Overall Accuracy): Overall accuracy considering voiced/unvoiced
- RPA (Raw Pitch Accuracy): Pitch accuracy within 50 cents tolerance
- RCA (Raw Chroma Accuracy): Chroma (pitch class) accuracy
- VR (Voicing Recall): Voicing recall rate
"""

from src.evaluation import PitchEvaluator
from pathlib import Path


def main():
    """Main evaluation function."""
    # Initialize evaluator with 50 cents tolerance (quarter tone)
    evaluator = PitchEvaluator(pitch_tolerance=50.0)
    
    # Define experimental conditions
    experiments = {
        'clean': {
            'prediction_dir': 'results/predictions/basic_pitch_normalized/clean',
            'ground_truth_dir': 'MedleyDB-Pitch/pitch',
            'output_path': 'results/metrics/basic_pitch_clean.csv'
        },
        'distortion': {
            'prediction_dir': 'results/predictions/basic_pitch_normalized/distortion',
            'ground_truth_dir': 'MedleyDB-Pitch-Experiments/pitch',
            'output_path': 'results/metrics/basic_pitch_distortion.csv'
        },
        'noise_5db': {
            'prediction_dir': 'results/predictions/basic_pitch_normalized/noise/5db',
            'ground_truth_dir': 'MedleyDB-Pitch-Experiments/pitch',
            'output_path': 'results/metrics/basic_pitch_noise_5db.csv'
        },
        'noise_15db': {
            'prediction_dir': 'results/predictions/basic_pitch_normalized/noise/15db',
            'ground_truth_dir': 'MedleyDB-Pitch-Experiments/pitch',
            'output_path': 'results/metrics/basic_pitch_noise_15db.csv'
        },
        'pitch_shift_25cents': {
            'prediction_dir': 'results/predictions/basic_pitch_normalized/pitch_shift/25cents',
            'ground_truth_dir': 'MedleyDB-Pitch-Experiments/pitch',
            'output_path': 'results/metrics/basic_pitch_pitch_shift_25cents.csv'
        },
        'pitch_shift_50cents': {
            'prediction_dir': 'results/predictions/basic_pitch_normalized/pitch_shift/50cents',
            'ground_truth_dir': 'MedleyDB-Pitch-Experiments/pitch',
            'output_path': 'results/metrics/basic_pitch_pitch_shift_50cents.csv'
        }
    }
    
    print("=" * 60)
    print("Basic Pitch Evaluation")
    print("=" * 60)
    print(f"\nTolerance: 50 cents (quarter tone)")
    print(f"Metrics: OA, RPA, RCA, VR\n")
    
    # Evaluate each experimental condition
    for exp_name, config in experiments.items():
        pred_dir = Path(config['prediction_dir'])
        
        # Check if prediction directory exists and has files
        if not pred_dir.exists():
            print(f"⚠ Skipping {exp_name}: Prediction directory not found")
            print(f"  {pred_dir}\n")
            continue
        
        pred_files = list(pred_dir.glob("*.csv"))
        if len(pred_files) == 0:
            print(f"⚠ Skipping {exp_name}: No prediction files found")
            print(f"  {pred_dir}\n")
            continue
        
        print(f"\n{'='*60}")
        print(f"Evaluating: {exp_name}")
        print(f"{'='*60}")
        print(f"Prediction files: {len(pred_files)}")
        
        try:
            evaluator.evaluate(
                prediction_dir=config['prediction_dir'],
                ground_truth_dir=config['ground_truth_dir'],
                output_path=config['output_path']
            )
        except Exception as e:
            print(f"\n✗ Error evaluating {exp_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Evaluation Complete")
    print("=" * 60)


if __name__ == '__main__':
    main()