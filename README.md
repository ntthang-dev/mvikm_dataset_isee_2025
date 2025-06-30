# The Definitive Grid Scenario Dataset (Version 1.0)

**Date Created:** June 26, 2025  
**Authors:** [N.T.THANG - HCMUT]  
**Contact:** [@ntthang-dev]

---

## 1. Purpose and Context

### 1.1. Scientific Purpose
This is a **synthetic dataset** created with the primary objective of **benchmarking and evaluating multi-view clustering algorithms** on electrical load profile data. It is not intended for general statistical inference but serves as a **"crucible"**—a challenging testbed designed to systematically assess an algorithm's ability to handle common real-world data issues.

The dataset is specifically crafted to test the performance of algorithms against the following core challenges, which are often cited as limitations in existing methodologies:
-   **Poor Data Quality:** Presence of impulsive noise and outliers.
-   **Data Heterogeneity:** Coexistence of structurally different data (i.e., samples with complete views and samples with missing views).
-   **Informational Redundancy:** Presence of highly correlated or co-dependent data sources.

### 1.2. Application Context
The scenario simulates a distribution grid in a large metropolitan area, serving a mixed customer base, including industrial manufacturing, commercial services, and residential households.

## 2. Structure and Format

-   **Scale:** 550 samples (customers), each with a time-series profile for a typical 24-hour period.
-   **Time Resolution:** 96 data points per time series, corresponding to a 15-minute measurement interval.
-   **Storage Format:** The dataset is provided in two standard CSV files:
    1.  **`input_data_tidy.csv`**: The primary input data for clustering algorithms, presented in a "tidy" (long) format.
    2.  **`ground_truth.csv`**: Contains the ground truth labels (`persona_id`) for each customer. **This file should only be used for a posteriori evaluation and NOT as an input to the clustering algorithm.**

## 3. Feature/View Description

The dataset consists of three distinct "views" for each customer, chosen to provide physically meaningful and relatively independent perspectives.

* **View 1: `active_power_profile` (P) [unit: kW]**
    * **Description:** The real power consumed by the load. This is the primary view reflecting the customer's operational scale and behavioral patterns.
    * **Data Type:** Floating-point time series.

* **View 2: `reactive_power_profile` (Q) [unit: kVAr]**
    * **Description:** The reactive power exchanged with the grid, which is crucial for indirectly assessing the power factor (`cosφ`).
    * **Data Type:** Floating-point time series. **Note:** This view contains `NaN` values for specific customer groups.

* **View 3: `volatility_profile` (V) [unit: kW]**
    * **Description:** A derived feature engineered to capture the "smoothness" or "choppiness" of the load. It is calculated as the standard deviation of the `active_power_profile` over a 5-point sliding window. This view provides information about the load's temporal "texture".
    * **Data Type:** Floating-point time series.

## 4. Data Quality - A Core Design Feature

The data quality issues in this dataset are **intentional design features**, not errors.

* **4.1. Missing Values (Structural Noise):**
    * **Description:** The entire `reactive_power_profile` (View Q) for all residential customers (`P4`, `P5`) is set to `NaN`.
    * **Purpose:** To simulate a realistic heterogeneous metering infrastructure and explicitly test an algorithm's ability to handle structurally missing views.

* **4.2. Outliers (Impulsive Noise):**
    * **Description:** The `active_power_profile` (View P) for a subset of industrial customers (`P2`) contains high-amplitude, short-duration spikes.
    * **Purpose:** To test the algorithm's robustness against transient events and non-Gaussian noise.

* **4.3. Redundancy:**
    * **Description:** A specific persona (`P6` in the generation script, though not explicitly separated in the final ground truth for this version) is designed to have highly correlated P views, simulating a facility with multiple co-dependent processes.
    * **Purpose:** To test the algorithm's ability to handle redundant information.

## 5. Statistics and Value Ranges

The following table summarizes the typical value ranges for the simulated customer personas.

| Persona ID | Description | `active_power_profile` (P) [kW] | `reactive_power_profile` (Q) [kVAr] |
| :--- | :--- | :--- | :--- |
| P1 | FDI - Compliant | [450, 500] | [-10, 10] |
| P2 | Industrial - Violator | [50, 300] (Spikes up to 800) | [200, 400] |
| P3 | Commercial | [100, 400] | [40, 120] |
| P4 | Residential - Peak Load | [0.5, 8] | `NaN` |
| P5 | Residential - w/ Solar PV | [-4, 5] | `NaN` |

## 6. Limitations

* **Synthetic Nature:** As a synthetic dataset, it may not capture the full complexity and unforeseen nuances of real-world data.
* **Not Statistically Representative:** The distribution of customer personas is deliberately biased to ensure all challenges are well-represented. It should not be used for demographic or population-level statistical analysis.
* **Temporal Scope:** The dataset covers a single 24-hour period and does not include weekly or seasonal variations.

## 7. Reproducibility

This dataset is fully reproducible. The Python script used for its generation (`generate_definitive_data.py`) is provided alongside this documentation to ensure complete transparency and allow other researchers to replicate or modify the experimental setup.