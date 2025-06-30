# -----------------------------------------------------------------------------
# Copyright (c) 2025 [N.T.THANG/N.P.KHAI]
# HO Chi Minh City University of Technology (HCMUT) - Vietnam National University (VNU)
# Department of Electrical and Electronics Engineering
# MVIKM ISEE 2025 Dataset Generator
# -----------------------------------------------------------------------------
# All rights reserved.
#
# This file is part of the MVIKM ISEE 2025 Dataset Generator.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
#
# Author: [N.T.THANG/N.P.KHAI - HCMUT]
# License: [Apache License, Version 2.0]
# -----------------------------------------------------------------------------

import pandas as pd
import numpy as np
import os

# --- CONFIGURATION PARAMETERS ---
NUM_POINTS = 96  # 24 hours * 4 points/hour (15-minute intervals)
PERSONA_DISTRIBUTION = {
    'P1': 50,   # FDI Good Compliance
    'P2': 80,   # Enterprise Violation
    'P3': 60,   # Shopping Center
    'P4': 300,  # Household (Air Conditioner)
    'P5': 60,   # Household (Solar Power)
}

# --- PROFILE GENERATION FUNCTIONS ---
def add_gaussian_noise(signal, std_dev_ratio=0.005):
    noise_std = np.mean(np.abs(signal)) * std_dev_ratio
    noise = np.random.normal(0, noise_std, signal.shape)
    return signal + noise

def add_spikes(signal, num_spikes, spike_magnitude_ratio):
    signal_with_spikes = np.copy(signal)
    max_val = np.max(signal)
    spike_indices = np.random.choice(len(signal), num_spikes, replace=False)
    for idx in spike_indices:
        signal_with_spikes[idx] += max_val * spike_magnitude_ratio * (1 + np.random.rand())
    return signal_with_spikes

def calculate_volatility(signal, window_size=5):
    return pd.Series(signal).rolling(window=window_size, center=True, min_periods=1).std().bfill().values

def generate_p1_profile(length):
    p = np.full(length, 475) + np.random.uniform(-25, 25, length)
    q = np.random.uniform(-10, 10, length)
    p = add_gaussian_noise(p)
    q = add_gaussian_noise(q, 0.01)
    v = calculate_volatility(p)
    return p, q, v

def generate_p2_profile(length):
    p = np.full(length, 80)
    work_hours = (np.arange(length) >= 32) & (np.arange(length) < 68)
    p[work_hours] = 200 + 100 * np.sin(np.linspace(0, np.pi, np.sum(work_hours)))
    p = add_spikes(p, num_spikes=2, spike_magnitude_ratio=2.5)
    q = np.zeros(length)
    q[work_hours] = p[work_hours] * np.random.uniform(1.0, 1.2)
    p = add_gaussian_noise(p)
    q = add_gaussian_noise(q)
    v = calculate_volatility(p)
    return p, q, v

def generate_p3_profile(length):
    p = np.full(length, 120)
    open_hours = (np.arange(length) >= 36) & (np.arange(length) < 88)
    p[open_hours] = np.linspace(200, 400, np.sum(open_hours)) - np.linspace(0, 200, np.sum(open_hours)) * np.sin(np.linspace(0, np.pi, np.sum(open_hours)))
    q = np.zeros(length)
    q[open_hours] = p[open_hours] * np.random.uniform(0.3, 0.4)
    p = add_gaussian_noise(p)
    q = add_gaussian_noise(q)
    v = calculate_volatility(p)
    return p, q, v

def generate_p4_profile(length):
    p_base = 0.4 + 0.2 * np.sin(np.linspace(0, 4 * np.pi, length))
    p_base[p_base < 0.1] = 0.1
    evening_indices = (np.arange(length) >= 74) & (np.arange(length) < 94)
    p_base[evening_indices] += np.random.uniform(1.5, 2.5) * np.random.randint(0, 2, size=len(p_base[evening_indices]))
    p = add_gaussian_noise(p_base, 0.05)
    q = np.full(length, np.nan)  # Q is NaN
    v = calculate_volatility(p)
    return p, q, v

def generate_p5_profile(length):
    p_base = 0.5 + 0.3 * np.sin(np.linspace(0, 4 * np.pi, length))
    p_base[p_base < 0.2] = 0.2
    solar_indices = (np.arange(length) >= 36) & (np.arange(length) < 64)
    solar_gen = 4.5 * np.sin(np.linspace(0, np.pi, np.sum(solar_indices)))
    p_base[solar_indices] -= solar_gen
    p = add_gaussian_noise(p_base, 0.05)
    q = np.full(length, np.nan)  # Q is NaN
    v = calculate_volatility(p)
    return p, q, v

GENERATOR_MAP = {
    'P1': generate_p1_profile, 'P2': generate_p2_profile, 'P3': generate_p3_profile,
    'P4': generate_p4_profile, 'P5': generate_p5_profile,
}

def generate_dataset(output_dir):
    """Main function to generate the dataset (no_nan scenario only)."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Generating data in directory: {output_dir}...")
    
    ground_truth_data = []
    tidy_data_rows = []
    customer_counter = 1

    for persona_id, count in PERSONA_DISTRIBUTION.items():
        for _ in range(count):
            customer_id = f"CUST_{str(customer_counter).zfill(4)}"
            ground_truth_data.append({'customer_id': customer_id, 'persona_id': persona_id})
            generator_func = GENERATOR_MAP[persona_id]
            p, q, v = generator_func(NUM_POINTS)

            # Fill Q for households with a small noisy value if NaN
            if np.isnan(q).any():
                q = p * np.random.uniform(0.1, 0.25)
                q = add_gaussian_noise(q, 0.1)

            for i in range(NUM_POINTS):
                row = {
                    'customer_id': customer_id,
                    'timestamp': i,
                    'p_value': p[i],
                    'q_value': q[i],
                    'v_value': v[i]
                }
                tidy_data_rows.append(row)
            customer_counter += 1
            
    df_ground_truth = pd.DataFrame(ground_truth_data)
    df_input_data_tidy = pd.DataFrame(tidy_data_rows)

    gt_path = os.path.join(output_dir, 'ground_truth.csv')
    input_path = os.path.join(output_dir, 'input_data_tidy.csv')
    df_ground_truth.to_csv(gt_path, index=False)
    df_input_data_tidy.to_csv(input_path, index=False)

    print(f"-> Dataset successfully generated.")
    print(f"   - {gt_path}")
    print(f"   - {input_path}")
    print("-" * 50)

if __name__ == '__main__':
    print("Starting data generation process for the dataset...")
    generate_dataset('data')
    print("Dataset has been generated successfully.")
