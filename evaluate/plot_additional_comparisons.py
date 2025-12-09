"""
Plot additional comparison figures:
1. Distortion levels comparison (light/medium/heavy)
2. Instrument vs Vocal comparison
3. Noise types comparison (room/street/people)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional

# Try to import seaborn for better styling (optional)
try:
    import seaborn as sns
    sns.set_style("whitegrid")
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False

# Set matplotlib style
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10
plt.style.use('default')


class AdditionalPlotter:
    """Plot additional comparisons based on manifest classifications."""
    
    def __init__(self, results_dir: str = "results/metrics", manifests_dir: str = "MedleyDB-Pitch-Experiments/manifests"):
        """
        Initialize plotter.
        
        Args:
            results_dir: Directory containing evaluation result CSV files
            manifests_dir: Directory containing manifest CSV files
        """
        self.results_dir = Path(results_dir)
        self.manifests_dir = Path(manifests_dir)
        self.metrics = ['OA', 'RPA', 'RCA', 'VR']
        self.models = ['librosa', 'crepe', 'basic_pitch']
        self.colors = {
            'librosa': '#1f77b4',      # Blue
            'crepe': '#ff7f0e',        # Orange
            'basic_pitch': '#2ca02c'   # Green
        }
    
    def load_manifests(self) -> Dict[str, pd.DataFrame]:
        """Load all manifest files."""
        manifests = {}
        
        # Load distortion manifest
        dist_file = self.manifests_dir / 'manifest_dist.csv'
        if dist_file.exists():
            manifests['distortion'] = pd.read_csv(dist_file)
        
        # Load noise manifest
        noise_file = self.manifests_dir / 'manifest_noise.csv'
        if noise_file.exists():
            manifests['noise'] = pd.read_csv(noise_file)
        
        # Load tuning manifest (for class_tag)
        tuning_file = self.manifests_dir / 'manifest_tuning.csv'
        if tuning_file.exists():
            manifests['tuning'] = pd.read_csv(tuning_file)
        
        return manifests
    
    def load_results_with_metadata(self, manifests: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Load all evaluation results and merge with manifest metadata.
        
        Returns:
            Dictionary: {model: DataFrame with merged metadata}
        """
        all_results = {}
        
        for model in self.models:
            model_results = []
            
            # Load clean results
            clean_file = self.results_dir / f"{model}_clean.csv"
            if clean_file.exists():
                df = pd.read_csv(clean_file)
                df = df[df['filename'] != 'AVERAGE']
                # Extract track_id from filename (remove .csv extension if present)
                df['track_id'] = df['filename'].str.replace('.csv', '', regex=False).str.replace('.wav', '', regex=False)
                df['condition'] = 'clean'
                model_results.append(df)
            
            # Load distortion results
            dist_file = self.results_dir / f"{model}_distortion.csv"
            if dist_file.exists() and 'distortion' in manifests:
                df = pd.read_csv(dist_file)
                df = df[df['filename'] != 'AVERAGE']
                df['track_id'] = df['filename'].str.replace('.csv', '', regex=False).str.replace('.wav', '', regex=False)
                df['condition'] = 'distortion'
                # Merge with distortion manifest
                df = df.merge(manifests['distortion'][['track_id', 'level_tag', 'class_tag']], 
                            on='track_id', how='left')
                model_results.append(df)
            
            # Load noise results
            for snr in ['5db', '15db']:
                noise_file = self.results_dir / f"{model}_noise_{snr}.csv"
                if noise_file.exists() and 'noise' in manifests:
                    df = pd.read_csv(noise_file)
                    df = df[df['filename'] != 'AVERAGE']
                    df['track_id'] = df['filename'].str.replace('.csv', '', regex=False).str.replace('.wav', '', regex=False)
                    df['condition'] = f'noise_{snr}'
                    df['snr'] = snr
                    # Merge with noise manifest
                    df = df.merge(manifests['noise'][['track_id', 'noise_tag', 'class_tag']], 
                                on='track_id', how='left')
                    model_results.append(df)
            
            # Load pitch shift results
            for cents in ['25cents', '50cents']:
                pitch_file = self.results_dir / f"{model}_pitch_shift_{cents}.csv"
                if pitch_file.exists() and 'tuning' in manifests:
                    df = pd.read_csv(pitch_file)
                    df = df[df['filename'] != 'AVERAGE']
                    df['track_id'] = df['filename'].str.replace('.csv', '', regex=False).str.replace('.wav', '', regex=False)
                    df['condition'] = f'pitch_shift_{cents}'
                    # Merge with tuning manifest for class_tag
                    df = df.merge(manifests['tuning'][['track_id', 'class_tag']], 
                                on='track_id', how='left')
                    model_results.append(df)
            
            if model_results:
                all_results[model] = pd.concat(model_results, ignore_index=True)
            else:
                all_results[model] = None
        
        return all_results
    
    def plot_instrument_vocal(self, results: Dict[str, pd.DataFrame], output_dir: str = "results/figures"):
        """
        Plot comparison between instrument and vocal tracks.
        
        Args:
            results: Loaded results with metadata
            output_dir: Directory to save figures
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for metric in self.metrics:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            x_positions = {'instrument': 0, 'vocal': 1}
            x_labels = ['Instrument', 'Vocal']
            
            # Collect all data across all conditions
            for model_idx, model in enumerate(self.models):
                if results[model] is None:
                    continue
                
                df = results[model]
                # Filter rows with class_tag
                df_with_class = df[df['class_tag'].notna()].copy()
                
                if len(df_with_class) == 0:
                    continue
                
                x_data = []
                y_data = []
                
                for class_type in ['instrument', 'vocal']:
                    class_data = df_with_class[df_with_class['class_tag'] == class_type]
                    if len(class_data) > 0 and metric in class_data.columns:
                        values = class_data[metric].dropna().values
                        x_pos = x_positions[class_type] + (model_idx - 1) * 0.2
                        x_data.extend([x_pos] * len(values))
                        y_data.extend(values)
                
                if len(y_data) > 0:
                    ax.scatter(x_data, y_data,
                             c=self.colors[model],
                             label=model.replace('_', ' ').title(),
                             alpha=0.5,
                             s=60,
                             edgecolors='white',
                             linewidths=0.8,
                             zorder=3)
                    
                    # Plot statistics
                    for class_type in ['instrument', 'vocal']:
                        class_data = df_with_class[df_with_class['class_tag'] == class_type]
                        if len(class_data) > 0 and metric in class_data.columns:
                            values = class_data[metric].dropna().values
                            if len(values) > 0:
                                x_pos = x_positions[class_type] + (model_idx - 1) * 0.2
                                median = np.median(values)
                                mean = np.mean(values)
                                
                                ax.plot([x_pos - 0.15, x_pos + 0.15],
                                       [median, median],
                                       color=self.colors[model],
                                       linewidth=3,
                                       alpha=0.9,
                                       zorder=4)
                                
                                ax.plot([x_pos - 0.15, x_pos + 0.15],
                                       [mean, mean],
                                       color=self.colors[model],
                                       linewidth=2.5,
                                       linestyle='--',
                                       alpha=0.9,
                                       zorder=4)
            
            # Set x-axis
            ax.set_xticks([x_positions[c] for c in ['instrument', 'vocal']])
            ax.set_xticklabels(x_labels, fontsize=12, fontweight='bold')
            ax.set_xlim(-0.5, 1.5)
            
            # Set y-axis
            ax.set_ylim(-0.05, 1.05)
            metric_name = self._get_metric_full_name(metric)
            ax.set_ylabel(f'{metric} Score', fontsize=13, fontweight='bold')
            ax.set_yticks(np.arange(0, 1.1, 0.1))
            ax.set_yticklabels([f'{v:.1f}' for v in np.arange(0, 1.1, 0.1)], fontsize=10)
            
            # Set title
            ax.set_title(f'{metric} - {metric_name}: Instrument vs Vocal',
                        fontsize=15, fontweight='bold', pad=20)
            
            # Add grid and legend
            ax.grid(True, alpha=0.3, linestyle='--', axis='y', zorder=0)
            ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, fontsize=11)
            ax.text(0.02, 0.98,
                   'Solid line: Median | Dashed line: Mean',
                   transform=ax.transAxes,
                   fontsize=9,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            plt.tight_layout()
            output_file = output_path / f"{metric.lower()}_instrument_vocal.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"  ✓ Saved: {output_file}")
            plt.close()
    
    def plot_noise_types(self, results: Dict[str, pd.DataFrame], output_dir: str = "results/figures"):
        """
        Plot comparison across noise types (room/street/people).
        
        Args:
            results: Loaded results with metadata
            output_dir: Directory to save figures
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for metric in self.metrics:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            x_positions = {'room': 0, 'street': 1, 'people': 2}
            x_labels = ['Room', 'Street', 'People']
            
            # Plot data for each model
            for model_idx, model in enumerate(self.models):
                if results[model] is None:
                    continue
                
                df = results[model]
                # Filter noise conditions
                noise_df = df[df['condition'].str.startswith('noise_')].copy()
                
                if len(noise_df) == 0 or 'noise_tag' not in noise_df.columns:
                    continue
                
                x_data = []
                y_data = []
                
                for noise_type in ['room', 'street', 'people']:
                    type_data = noise_df[noise_df['noise_tag'] == noise_type]
                    if len(type_data) > 0 and metric in type_data.columns:
                        values = type_data[metric].dropna().values
                        x_pos = x_positions[noise_type] + (model_idx - 1) * 0.2
                        x_data.extend([x_pos] * len(values))
                        y_data.extend(values)
                
                if len(y_data) > 0:
                    ax.scatter(x_data, y_data,
                             c=self.colors[model],
                             label=model.replace('_', ' ').title(),
                             alpha=0.5,
                             s=60,
                             edgecolors='white',
                             linewidths=0.8,
                             zorder=3)
                    
                    # Plot statistics
                    for noise_type in ['room', 'street', 'people']:
                        type_data = noise_df[noise_df['noise_tag'] == noise_type]
                        if len(type_data) > 0 and metric in type_data.columns:
                            values = type_data[metric].dropna().values
                            if len(values) > 0:
                                x_pos = x_positions[noise_type] + (model_idx - 1) * 0.2
                                median = np.median(values)
                                mean = np.mean(values)
                                
                                ax.plot([x_pos - 0.15, x_pos + 0.15],
                                       [median, median],
                                       color=self.colors[model],
                                       linewidth=3,
                                       alpha=0.9,
                                       zorder=4)
                                
                                ax.plot([x_pos - 0.15, x_pos + 0.15],
                                       [mean, mean],
                                       color=self.colors[model],
                                       linewidth=2.5,
                                       linestyle='--',
                                       alpha=0.9,
                                       zorder=4)
            
            # Set x-axis
            ax.set_xticks([x_positions[n] for n in ['room', 'street', 'people']])
            ax.set_xticklabels(x_labels, fontsize=12, fontweight='bold')
            ax.set_xlim(-0.5, 2.5)
            
            # Set y-axis
            ax.set_ylim(-0.05, 1.05)
            metric_name = self._get_metric_full_name(metric)
            ax.set_ylabel(f'{metric} Score', fontsize=13, fontweight='bold')
            ax.set_yticks(np.arange(0, 1.1, 0.1))
            ax.set_yticklabels([f'{v:.1f}' for v in np.arange(0, 1.1, 0.1)], fontsize=10)
            
            # Set title
            ax.set_title(f'{metric} - {metric_name} by Noise Type',
                        fontsize=15, fontweight='bold', pad=20)
            
            # Add grid and legend
            ax.grid(True, alpha=0.3, linestyle='--', axis='y', zorder=0)
            ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, fontsize=11)
            ax.text(0.02, 0.98,
                   'Solid line: Median | Dashed line: Mean',
                   transform=ax.transAxes,
                   fontsize=9,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            plt.tight_layout()
            output_file = output_path / f"{metric.lower()}_noise_types.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"  ✓ Saved: {output_file}")
            plt.close()
    
    def _get_metric_full_name(self, metric: str) -> str:
        """Get full name for metric."""
        names = {
            'OA': 'Overall Accuracy',
            'RPA': 'Raw Pitch Accuracy',
            'RCA': 'Raw Chroma Accuracy',
            'VR': 'Voicing Recall'
        }
        return names.get(metric, metric)
    
    def plot_all(self, output_dir: str = "results/figures"):
        """Generate all additional comparison plots."""
        print("=" * 70)
        print("Loading manifests and evaluation results...")
        print("=" * 70)
        
        # Load manifests
        manifests = self.load_manifests()
        print(f"Loaded manifests: {list(manifests.keys())}")
        
        # Load results with metadata
        results = self.load_results_with_metadata(manifests)
        for model in self.models:
            if results[model] is not None:
                print(f"{model}: {len(results[model])} results loaded")
        
        print("\n" + "=" * 70)
        print("Creating additional comparison plots...")
        print("=" * 70)
        
        # Plot instrument vs vocal
        print("\n[1/2] Plotting instrument vs vocal comparison...")
        self.plot_instrument_vocal(results, output_dir)
        
        # Plot noise types
        print("\n[2/2] Plotting noise types comparison...")
        self.plot_noise_types(results, output_dir)
        
        print("\n" + "=" * 70)
        print("All additional plots created successfully!")
        print(f"Figures saved to: {output_dir}")
        print("=" * 70)


def main():
    """Main function."""
    plotter = AdditionalPlotter(
        results_dir="results/metrics",
        manifests_dir="MedleyDB-Pitch-Experiments/manifests"
    )
    plotter.plot_all(output_dir="results/figures")


if __name__ == '__main__':
    main()

