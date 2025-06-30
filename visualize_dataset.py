# -----------------------------------------------------------------------------
# Copyright (c) 2025 [N.T.THANG]
# HO Chi Minh City University of Technology (HCMUT) - Vietnam National University (VNU)
# Department of Electrical and Electronics Engineering
# MVIKM ISEE 2025 Dataset Visualization
# -----------------------------------------------------------------------------
# All rights reserved.
#
# This file is part of the MVIKM ISEE 2025 Dataset Generator.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
#
# Author: [N.T.THANG - HCMUT]
# License: [Apache License, Version 2.0]
# -----------------------------------------------------------------------------
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import argparse

NUM_POINTS = 96
NUM_INDIVIDUAL_SAMPLES_TO_PLOT = 3

def visualize(dataset_dir):
    """Create a single multi-panel figure, keeping the original style."""
    print(f"--- Visualizing dataset in: {dataset_dir} ---")
    input_data_path = os.path.join(dataset_dir, 'input_data_tidy.csv')
    ground_truth_path = os.path.join(dataset_dir, 'ground_truth.csv')

    # Check if required files exist
    if not os.path.exists(input_data_path) or not os.path.exists(ground_truth_path):
        print(f"Error: 'input_data_tidy.csv' or 'ground_truth.csv' not found in '{dataset_dir}'")
        return
        
    df_input = pd.read_csv(input_data_path)
    df_truth = pd.read_csv(ground_truth_path)
    df_full = pd.merge(df_input, df_truth, on='customer_id')

    # Keep original style
    plt.style.use('seaborn-v0_8-paper')
    plt.rcParams.update({'font.size': 10, 'figure.autolayout': True, 'axes.grid': True, 'grid.linestyle': ':', 'grid.alpha': 0.7})

    fig = plt.figure(figsize=(8.5, 7))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.2, 1])
    fig.suptitle(f'Dataset Overview: {os.path.basename(dataset_dir)}', fontsize=14, weight='bold')

    time_axis = np.arange(NUM_POINTS) * (24 / NUM_POINTS)

    def plot_mean_and_individual_samples(ax, df, persona_id, color, label, view='p_value'):
        """Plot mean and individual sample profiles for a given persona."""
        persona_df = df[df['persona_id'] == persona_id]
        if view not in persona_df.columns: return
        
        matrix = persona_df.pivot(index='customer_id', columns='timestamp', values=view).values
        
        num_samples = min(NUM_INDIVIDUAL_SAMPLES_TO_PLOT, len(matrix))
        sample_indices = np.random.choice(len(matrix), num_samples, replace=False)
        for idx in sample_indices:
            ax.plot(time_axis, matrix[idx], color=color, alpha=0.2, linewidth=0.8)

        mean_profile = np.nanmean(matrix, axis=0) # Use nanmean for safety
        ax.plot(time_axis, mean_profile, color=color, label=label, linewidth=2.5)

    # --- Panel (a.1): Industrial & Commercial Profiles ---
    ax1 = fig.add_subplot(gs[0, 0])
    plot_mean_and_individual_samples(ax1, df_full, 'P1', 'blue', 'P1: FDI Compliant (Mean)')
    plot_mean_and_individual_samples(ax1, df_full, 'P2', 'red', 'P2: Industrial Violator (Mean)')
    plot_mean_and_individual_samples(ax1, df_full, 'P3', 'orange', 'P3: Commercial (Mean)')
    ax1.plot([], [], color='gray', linewidth=0.8, alpha=0.5, label='Individual Samples')
    ax1.set_title('(a.1) C&I Active Power (P) Profiles', loc='left', weight='bold')
    ax1.set_ylabel('Power (kW)')
    ax1.legend(fontsize=7)
    ax1.set_xlim(0, 24)
    ax1.set_xticks(np.arange(0, 25, 6))

    # --- Panel (a.2): Residential Profiles ---
    ax2 = fig.add_subplot(gs[0, 1])
    plot_mean_and_individual_samples(ax2, df_full, 'P4', 'purple', 'P4: Residential Peak (Mean)')
    plot_mean_and_individual_samples(ax2, df_full, 'P5', 'green', 'P5: Residential w/ Solar (Mean)')
    ax2.plot([], [], color='gray', linewidth=0.8, alpha=0.5, label='Individual Samples')
    ax2.axhline(0, color='black', linestyle='--', linewidth=0.8)
    ax2.set_title('(a.2) Residential Active Power (P) Profiles', loc='left', weight='bold')
    ax2.legend(fontsize=7)
    ax2.set_xlim(0, 24)
    ax2.set_xticks(np.arange(0, 25, 6))

    # --- Panel (b): Q Distribution ---
    ax3 = fig.add_subplot(gs[1, 0])
    if 'q_value' in df_full.columns:
        q_data = df_full[~df_full['persona_id'].isin(['P4', 'P5'])]['q_value'].dropna()
        if not q_data.empty:
            sns.kdeplot(q_data, ax=ax3, fill=True, color='darkcyan', alpha=0.6)
    ax3.set_title('(b) Q Distribution (C&I Customers)', loc='left', weight='bold')
    ax3.set_xlabel('Reactive Power (kVAr)')
    ax3.set_ylabel('Density')

    # --- Panel (c): Missing Data Percentage ---
    ax4 = fig.add_subplot(gs[1, 1])
    if 'q_value' in df_full.columns:
        summary_data = []
        sorted_personas = sorted(df_full['persona_id'].unique())
        for persona_id in sorted_personas:
            persona_df = df_full[df_full['persona_id'] == persona_id]
            missing_percentage = persona_df['q_value'].isna().mean() * 100
            summary_data.append({'persona_id': persona_id, 'missing_pct': missing_percentage})
        missing_summary_df = pd.DataFrame(summary_data)
        sns.barplot(x='persona_id', y='missing_pct', data=missing_summary_df, ax=ax4, palette='viridis')
        for p in ax4.patches:
            if p.get_height() == 0: 
                ax4.annotate('0%', (p.get_x() + p.get_width() / 2., 2), ha='center', va='bottom')
            elif p.get_height() == 100: 
                ax4.annotate('100%', (p.get_x() + p.get_width() / 2., p.get_height() - 5), ha='center', va='bottom', color='white')
    ax4.set_title('(c) Missing Q Data Percentage', loc='left', weight='bold')
    ax4.set_ylabel('% Missing')
    ax4.set_xlabel('Customer Persona ID')
    ax4.set_yticks(np.arange(0, 101, 25))
    ax4.set_ylim(0, 105)
    ax4.grid(axis='y', linestyle=':', alpha=0.7)

    fig.tight_layout(pad=1.0, rect=[0, 0, 1, 0.96])
    
    save_path = os.path.join(dataset_dir, f'dataset_overview.png')
    plt.savefig(save_path, dpi=300)
    plt.close()

    print(f"Done! Overview image saved to: {save_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Visualize the dataset in the original style.")
    parser.add_argument('dataset_dir', type=str, help="Path to the directory containing the dataset.")
    args = parser.parse_args()
    visualize(args.dataset_dir)
