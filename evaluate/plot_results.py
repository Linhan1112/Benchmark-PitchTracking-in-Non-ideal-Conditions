"""
Plot evaluation results for pitch tracking comparison.

Creates 4 plots (one for each metric: OA, RPA, RCA, VR) showing:
- X-axis: Experimental conditions (clean, distortion light/medium/heavy, noise 5db, noise 15db, pitch shift 25cents, pitch shift 50cents)
- Y-axis: Metric values (0-1) for each audio file
- Different colors for different models (librosa, crepe, basic_pitch)
- Median and mean lines for each condition
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
plt.rcParams['figure.figsize'] = (16, 8)
plt.rcParams['font.size'] = 10
plt.style.use('default')


class ResultsPlotter:
    """
    Plot evaluation results for multiple models and experimental conditions.
    """
    
    def __init__(self, results_dir: str = "results/metrics"):
        """
        Initialize plotter.
        
        Args:
            results_dir: Directory containing evaluation result CSV files
        """
        self.results_dir = Path(results_dir)
        self.metrics = ['OA', 'RPA', 'RCA', 'VR']
        self.models = ['librosa', 'crepe', 'basic_pitch']
        self.colors = {
            'librosa': '#1f77b4',      # Blue
            'crepe': '#ff7f0e',        # Orange
            'basic_pitch': '#2ca02c'   # Green
        }
        
        # Experimental conditions (in order)
        # Distortion is split into light/medium/heavy levels
        self.conditions = [
            'clean',
            'distortion_light',
            'distortion_medium',
            'distortion_heavy',
            'noise_5db',
            'noise_15db',
            'pitch_shift_25cents',
            'pitch_shift_50cents'
        ]
        
        # Display names for conditions
        self.condition_labels = {
            'clean': 'Clean',
            'distortion_light': 'Distortion\nLight',
            'distortion_medium': 'Distortion\nMedium',
            'distortion_heavy': 'Distortion\nHeavy',
            'noise_5db': 'Noise 5dB',
            'noise_15db': 'Noise 15dB',
            'pitch_shift_25cents': 'Pitch Shift 25¢',
            'pitch_shift_50cents': 'Pitch Shift 50¢'
        }
        
        # Manifest directory for distortion level information
        self.manifests_dir = Path("MedleyDB-Pitch-Experiments/manifests")
    
    def load_results(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Load all evaluation results.
        For distortion conditions, split by level (light/medium/heavy).
        
        Returns:
            Dictionary: {model: {condition: DataFrame}}
        """
        results = {}
        
        # Load distortion manifest
        dist_manifest = None
        dist_manifest_path = self.manifests_dir / 'manifest_dist.csv'
        if dist_manifest_path.exists():
            dist_manifest = pd.read_csv(dist_manifest_path)
        
        for model in self.models:
            results[model] = {}
            for condition in self.conditions:
                if condition.startswith('distortion_'):
                    # Handle distortion levels separately
                    level = condition.split('_')[1]  # light, medium, or heavy
                    # Load the main distortion file
                    file_path = self.results_dir / f"{model}_distortion.csv"
                    
                    if file_path.exists() and dist_manifest is not None:
                        df = pd.read_csv(file_path)
                        df = df[df['filename'] != 'AVERAGE']
                        # Extract track_id from filename
                        df['track_id'] = df['filename'].str.replace('.csv', '', regex=False).str.replace('.wav', '', regex=False)
                        # Merge with manifest to get level_tag
                        df = df.merge(dist_manifest[['track_id', 'level_tag']], on='track_id', how='left')
                        # Filter by level
                        df_level = df[df['level_tag'] == level].copy()
                        if len(df_level) > 0:
                            # Remove helper columns
                            df_level = df_level.drop(['track_id', 'level_tag'], axis=1, errors='ignore')
                            results[model][condition] = df_level
                        else:
                            results[model][condition] = None
                    else:
                        results[model][condition] = None
                else:
                    # Handle other conditions normally
                    file_path = self.results_dir / f"{model}_{condition}.csv"
                    
                    if file_path.exists():
                        df = pd.read_csv(file_path)
                        # Remove AVERAGE row if exists
                        df = df[df['filename'] != 'AVERAGE']
                        results[model][condition] = df
                    else:
                        print(f"Warning: {file_path} not found, skipping...")
                        results[model][condition] = None
        
        return results
    
    def plot_metric(self,
                   metric: str,
                   results: Dict[str, Dict[str, pd.DataFrame]],
                   output_path: Optional[str] = None):
        """
        Plot a single metric across all conditions and models.
        
        Args:
            metric: Metric name (OA, RPA, RCA, or VR)
            results: Loaded results dictionary
            output_path: Optional path to save figure
        """
        fig, ax = plt.subplots(figsize=(16, 8))
        
        # Prepare data for plotting
        x_positions = {}
        x_offset = 0
        for condition in self.conditions:
            x_positions[condition] = x_offset
            x_offset += 1
        
        # Plot data for each model
        for model_idx, model in enumerate(self.models):
            x_data = []
            y_data = []
            
            for condition in self.conditions:
                if results[model][condition] is not None:
                    df = results[model][condition]
                    if metric in df.columns:
                        values = df[metric].values
                        # Add x positions with offset for each model (3 models centered around condition)
                        x_pos = x_positions[condition] + (model_idx - 1) * 0.2
                        x_data.extend([x_pos] * len(values))
                        y_data.extend(values)
            
            if len(y_data) > 0:
                # Scatter plot
                ax.scatter(x_data, y_data, 
                          c=self.colors[model], 
                          label=model.replace('_', ' ').title(),
                          alpha=0.5, 
                          s=60,
                          edgecolors='white',
                          linewidths=0.8,
                          zorder=3)
        
        # Calculate and plot statistics for each condition
        for condition in self.conditions:
            x_pos = x_positions[condition]
            
            for model_idx, model in enumerate(self.models):
                if results[model][condition] is not None:
                    df = results[model][condition]
                    if metric in df.columns:
                        values = df[metric].values
                        if len(values) > 0:
                            x_pos_model = x_pos + (model_idx - 1) * 0.2
                            
                            # Calculate statistics
                            median = np.median(values)
                            mean = np.mean(values)
                            
                            # Plot median line (thick solid)
                            ax.plot([x_pos_model - 0.15, x_pos_model + 0.15], 
                                   [median, median],
                                   color=self.colors[model],
                                   linewidth=3,
                                   alpha=0.9,
                                   zorder=4)
                            
                            # Plot mean line (dashed)
                            ax.plot([x_pos_model - 0.15, x_pos_model + 0.15], 
                                   [mean, mean],
                                   color=self.colors[model],
                                   linewidth=2.5,
                                   linestyle='--',
                                   alpha=0.9,
                                   zorder=4)
                            
                            # Add text annotations (only show for middle model to reduce clutter)
                            if model_idx == 1:  # Show for middle model (crepe)
                                ax.text(x_pos_model, median + 0.03, 
                                       f'M={median:.3f}',
                                       fontsize=9,
                                       ha='center',
                                       color=self.colors[model],
                                       weight='bold',
                                       bbox=dict(boxstyle='round,pad=0.3', 
                                               facecolor='white', 
                                               alpha=0.8,
                                               edgecolor=self.colors[model],
                                               linewidth=1.5))
        
        # Set x-axis
        ax.set_xticks([x_positions[c] for c in self.conditions])
        ax.set_xticklabels([self.condition_labels[c] for c in self.conditions],
                           fontsize=11, rotation=0, ha='center')
        
        # Set y-axis
        ax.set_ylim(-0.05, 1.05)
        ax.set_ylabel(f'{metric} Score', fontsize=13, fontweight='bold')
        ax.set_yticks(np.arange(0, 1.1, 0.1))
        ax.set_yticklabels([f'{v:.1f}' for v in np.arange(0, 1.1, 0.1)], fontsize=10)
        
        # Set title
        metric_name = self._get_metric_full_name(metric)
        ax.set_title(f'{metric} - {metric_name}',
                    fontsize=15, fontweight='bold', pad=20)
        
        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--', axis='y', zorder=0)
        ax.axhline(y=0, color='black', linewidth=0.8, zorder=0)
        ax.axhline(y=1, color='black', linewidth=0.8, zorder=0)
        
        # Add legend
        ax.legend(loc='upper left', 
                 frameon=True, 
                 fancybox=True, 
                 shadow=True,
                 fontsize=11,
                 ncol=1)
        
        # Add note about statistics
        ax.text(0.02, 0.98, 
               'Solid line: Median | Dashed line: Mean',
               transform=ax.transAxes,
               fontsize=9,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        # Save figure
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"  ✓ Saved: {output_path}")
        else:
            plt.show()
        
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
    
    def plot_all_metrics(self, output_dir: str = "results/figures"):
        """
        Plot all 4 metrics and save figures.
        
        Args:
            output_dir: Directory to save figures
        """
        print("=" * 60)
        print("Loading evaluation results...")
        print("=" * 60)
        
        results = self.load_results()
        
        # Check which models and conditions have data
        available = {}
        for model in self.models:
            available[model] = []
            for condition in self.conditions:
                if results[model][condition] is not None:
                    available[model].append(condition)
            print(f"{model}: {len(available[model])} conditions")
        
        print("\n" + "=" * 60)
        print("Creating plots...")
        print("=" * 60)
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Plot each metric
        for metric in self.metrics:
            print(f"\nPlotting {metric}...")
            output_file = output_path / f"{metric.lower()}_comparison.png"
            self.plot_metric(metric, results, str(output_file))
        
        print("\n" + "=" * 60)
        print("All plots created successfully!")
        print(f"Figures saved to: {output_dir}")
        print("=" * 60)


def main():
    """Main function."""
    plotter = ResultsPlotter(results_dir="results/metrics")
    plotter.plot_all_metrics(output_dir="results/figures")


if __name__ == '__main__':
    main()

