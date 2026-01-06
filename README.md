# SCEM Section C - Manufacturing Defect Classification

A machine learning project demonstrating Random Forest classification on an imbalanced manufacturing defect dataset. This project explores handling class imbalance, model comparison, and hyperparameter tuning.

## Overview

This project analyzes a manufacturing defect dataset to predict whether products are defective based on various production metrics. The dataset exhibits significant class imbalance (~84% defective vs ~16% non-defective), making it an excellent case study for imbalanced classification techniques.

## Dataset

**Primary Dataset**: `manufacturing_defect_dataset.csv`
- ~3,300 records with 16 features
- Target: `DefectStatus` (1 = Defective, 0 = Non-Defective)
- Class distribution: ~2,700 defective, ~500 non-defective

**Features include**:
- Production metrics (Volume, Cost, Defect Rate)
- Quality indicators (Supplier Quality, Quality Score)
- Operational data (Maintenance Hours, Downtime Percentage)
- Efficiency measures (Worker Productivity, Energy Efficiency)

**Additional datasets** for experimentation:
- `BankCustomerChurnPrediction.csv`
- `IBM_CHRN_CSV.csv`
- `smoke_detection_iot.csv`

## Methodology

### 1. Exploratory Data Analysis
- Class distribution visualization
- Correlation analysis
- Feature importance ranking
- Pairplot analysis of key features

### 2. Handling Imbalanced Data
- **Stratified sampling** to maintain class distribution in train/test splits
- **Class weighting** (`class_weight='balanced'`) in Random Forest
- **SMOTE** (Synthetic Minority Over-sampling Technique) - available for experimentation

### 3. Model Comparison
Models evaluated using cross-validation:
- Logistic Regression
- Support Vector Classifier (SVC)
- K-Nearest Neighbors (KNN)
- **Random Forest** (primary model)

### 4. Hyperparameter Tuning
RandomizedSearchCV with parameters:
- `n_estimators`: Number of trees
- `max_depth`: Tree depth
- `min_samples_split` / `min_samples_leaf`: Split criteria
- `max_features`: Feature selection strategy
- `criterion`: Gini vs Entropy

### 5. Feature Selection
Recursive Feature Elimination (RFE) to identify top 10 predictive features.

## Results

The Random Forest classifier with class weighting demonstrates strong performance on imbalanced data, evaluated using:
- Accuracy
- Precision, Recall, F1-Score (weighted)
- Specificity
- Confusion Matrix

## Project Structure

```
SCEM_Section-C/
├── Section_C.ipynb              # Main analysis notebook
├── manufacturing_defect_dataset.csv
├── BankCustomerChurnPrediction.csv
├── IBM_CHRN_CSV.csv
├── smoke_detection_iot.csv
├── .ai-docs/                    # Auto-documentation system
│   ├── config.yaml
│   ├── requirements.txt
│   ├── scripts/
│   └── templates/
└── .github/workflows/           # CI/CD
    └── update_wiki.yml
```

## Getting Started

### Prerequisites
```bash
pip install pandas numpy scikit-learn seaborn matplotlib imbalanced-learn
```

### Running the Analysis
1. Clone the repository
2. Open `Section_C.ipynb` in Jupyter Notebook/Lab
3. Run all cells sequentially

## Key Findings

1. **Random Forest** outperforms other classifiers on this imbalanced dataset
2. **Class weighting** effectively handles the imbalance without oversampling
3. **Feature importance** reveals key predictive variables for defect prediction
4. **Stratified cross-validation** provides reliable performance estimates

## Auto-Documentation

This repository includes an AI-powered documentation system that automatically generates Wiki documentation from the codebase. See the [Wiki](../../wiki) for auto-generated documentation.

### Features
- Automatic file discovery
- LLM-powered documentation generation
- GitHub Wiki integration
- Support for multiple file types (.ipynb, .py, .sql, etc.)

## License

This project is for educational purposes as part of SCEM certification coursework.
