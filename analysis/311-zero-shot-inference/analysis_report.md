# Zero-Shot Inference Analysis Report

**Generated:** 2025-12-12 07:08:24

---

## Executive Summary

This report provides a comprehensive analysis of the zero-shot inference results using the pre-trained SAM3 model on the chicken detection validation dataset.

### Key Metrics

- **pmF1 (Prompt-Mask F1):** 0.0000
- **IL_MCC (Image-Level Matthews Correlation Coefficient):** 0.0000
- **CGF1 (Composite Score):** 0.0000

---

## 1. Metrics Overview

### 1.1 Prompt-Mask F1 (pmF1)

The pmF1 score of **0.0000** measures the segmentation quality on positive detections.

- **Range:** 0.0 to 1.0 (higher is better)
- **Interpretation:** 
  - High pmF1 (>0.7): Model produces accurate masks when it detects chickens
  - Low pmF1 (<0.3): Model struggles with mask quality even when detecting objects

### 1.2 Image-Level Matthews Correlation Coefficient (IL_MCC)

The IL_MCC score of **0.0000** measures the binary classification accuracy (presence vs absence of chickens).

- **Range:** -1.0 to 1.0 (higher is better, 0 = random guessing)
- **Interpretation:** 
  - High IL_MCC (>0.5): Model correctly identifies when chickens are present/absent
  - Low IL_MCC (<0.2): Model struggles with presence detection, may hallucinate
  - Negative IL_MCC: Model performs worse than random guessing

### 1.3 Composite Score (CGF1)

The CGF1 score of **0.0000** is the product of pmF1 and IL_MCC, providing an overall performance metric.

- **Formula:** CGF1 = pmF1 × IL_MCC
- **Interpretation:** 
  - High CGF1 (>0.5): Good overall performance on both segmentation and presence detection
  - Low CGF1 (<0.2): Significant room for improvement in one or both components

---

## 2. False Positive Analysis

False positives are detections made on images that contain no chickens (negative samples).

- **Total negative images:** 426
- **Negative images with detections:** 169
- **Total false positive detections:** 12168
- **Average detections per negative image:** 28.56
- **Maximum detections on a single negative image:** 139

### 2.1 False Positive Rate

The false positive rate is **39.7%** of negative images have at least one detection.

⚠️ **MODERATE FALSE POSITIVE RATE** - Some false detections on background. Fine-tuning should improve background rejection.

### 2.2 Presence Scores on False Positives

- **Average score:** 0.6162
- **Minimum score:** 0.3027
- **Maximum score:** 0.9609

⚠️ High average presence scores (>0.5) indicate confident false detections.

### 2.3 Top False Positive Images

Images with the most false positive detections:

| Rank | Image | Detections | Avg Score | Max Score |
|------|-------|------------|-----------|-----------|
| 1 | raw_data/images/chicken/2025-11-11-chicken-000005 (1).jpg | 139 | 0.6794 | 0.8477 |
| 2 | raw_data/images/chicken/2025-11-03-chicken-000040.jpg | 138 | 0.5360 | 0.7266 |
| 3 | raw_data/images/chicken/2025-11-15-chicken-000054 (1).jpg | 137 | 0.7265 | 0.9062 |
| 4 | raw_data/images/chicken/2025-11-11-chicken-000009 (2).jpg | 134 | 0.6765 | 0.8867 |
| 5 | raw_data/images/chicken/2025-11-11-chicken-000013 (2).jpg | 132 | 0.6996 | 0.8945 |
| 6 | raw_data/images/chicken/2025-11-04-chicken-000026 (2).jpg | 129 | 0.5557 | 0.7539 |
| 7 | raw_data/images/chicken/2025-11-11-chicken-000042 (2).jpg | 128 | 0.7901 | 0.9141 |
| 8 | raw_data/images/chicken/2025-11-11-chicken-000035.jpg | 128 | 0.5563 | 0.7109 |
| 9 | raw_data/images/chicken/2025-11-11-chicken-000044 (3).jpg | 128 | 0.6365 | 0.8867 |
| 10 | raw_data/images/chicken/2025-11-11-chicken-000003.jpg | 127 | 0.6119 | 0.8516 |

---

## 3. False Negative Analysis

False negatives are missed detections on images that contain chickens (positive samples).

- **Total positive images:** 0
- **Positive images with detections:** 0
- **Positive images without detections:** 0
- **Total ground truth annotations:** 0
- **Total predictions on positive images:** 0
- **Average detections per positive image:** 0.00
- **Average GT annotations per positive image:** 0.00


### 3.2 Top False Negative Images

Images with missed detections:

No false negatives detected (or all positive images have detections).

---

## 4. Distribution Analysis

### 4.1 Prediction Score Distribution

- **Count:** 12168
- **Mean:** 0.6162
- **Min:** 0.3027
- **Max:** 0.9609
- **Median:** 0.6211

### 4.2 Detection Count Distribution

- **Count:** 169
- **Mean:** 72.00
- **Min:** 1
- **Max:** 139
- **Median:** 77

---

## 5. Key Findings and Recommendations

### 5.1 Key Findings

- **Low pmF1:** The model struggles with mask quality. Consider increasing Dice/IoU loss weights during fine-tuning.
- **Low IL_MCC:** The model has difficulty with presence detection. This suggests the need for fine-tuning with negative samples to suppress hallucinations.
- **Low CGF1:** Overall performance is low. Fine-tuning is essential to improve both segmentation and presence detection.
- **High false positive rate (39.7%):** The model frequently detects chickens in empty scenes. Fine-tuning with negative samples is critical.

### 5.2 Recommendations

1. **Proceed with Fine-Tuning:** Based on the zero-shot baseline, fine-tuning is recommended to improve performance.

2. **Focus Areas for Fine-Tuning:**
   - If IL_MCC is low: Increase focal loss weight to better handle negative samples
   - If pmF1 is low: Increase Dice/IoU loss weights to improve mask quality
   - If false positive rate is high: Ensure negative samples are included in training

3. **Training Configuration:**
   - Use frozen backbone initially to preserve general visual knowledge
   - Set conservative learning rate (1e-5) to protect the backbone
   - Monitor both pmF1 and IL_MCC during training

4. **Evaluation:**
   - Compare fine-tuned metrics against this zero-shot baseline
   - Target: Significant improvement in IL_MCC (presence detection)
   - Target: Maintain or improve pmF1 (segmentation quality)

---

## 6. Appendix: Detailed Statistics

See the following JSON files for detailed statistics:

- `metrics_summary.json`: Core metrics (pmF1, IL_MCC, CGF1)
- `false_positive_details.json`: Detailed false positive analysis
- `false_negative_details.json`: Detailed false negative analysis
- `per_image_performance.json`: Per-image performance breakdown
- `statistics.json`: Comprehensive statistics dictionary

---

*Report generated by analyze_zero_shot_inference.py*