# PRD SAM3 Fine Tuning 2025

[**1\. Executive Summary & Product Scope	1**](#1.-executive-summary-&-product-scope)

[1.1. Product Vision	1](#1.1.-product-vision)

[1.2. Objective: Transition from Object Detection to Promptable Concept Segmentation (PCS)	1](#1.2.-objective:-transition-from-object-detection-to-promptable-concept-segmentation-\(pcs\))

[1.3. Key Deliverables	2](#1.3.-key-deliverables)

[1.4. Target Audience & Users	2](#1.4.-target-audience-&-users)

[**2\. Strategic Context & Problem Definition	3**](#2.-strategic-context-&-problem-definition)

[2.1. Current Limitations: Legacy YOLO/Object Detection Architectures	3](#2.1.-current-limitations:-legacy-yolo/object-detection-architectures)

[2.2. The Paradigm Shift: Visual Segmentation (PVS) vs. Concept Segmentation (PCS)	3](#2.2.-the-paradigm-shift:-visual-segmentation-\(pvs\)-vs.-concept-segmentation-\(pcs\))

[2.3. The "Not-Chicken" Challenge: Importance of Negative Mining	3](#2.3.-the-"not-chicken"-challenge:-importance-of-negative-mining)

[2.4. Business Impact & Operational Goals	4](#2.4.-business-impact-&-operational-goals)

[**3\. Functional Requirements: Data Engineering (ETL)	5**](#3.-functional-requirements:-data-engineering-\(etl\))

[3.1. Source Data Formats	5](#3.1.-source-data-formats)

[3.2. Target Schema: SA-Co / SAM 3 JSON Structure	5](#3.2.-target-schema:-sa-co-/-sam-3-json-structure)

[3.3. Transformation Logic (ETL Pipeline)	6](#3.3.-transformation-logic-\(etl-pipeline\))

[3.3.1. Normalization & Instance ID Assignment	6](#3.3.1.-normalization-&-instance-id-assignment)

[3.3.2. Explicit Negative Sampling (Handling "Not-Chicken" Images)	6](#3.3.2.-explicit-negative-sampling-\(handling-"not-chicken"-images\))

[3.3.3. Text Prompt & Annotation Mapping	6](#3.3.3.-text-prompt-&-annotation-mapping)

[3.4. Data Validation Criteria	6](#3.4.-data-validation-criteria)

[**4\. Technical Requirements: System Architecture (SAM 3\)	8**](#4.-technical-requirements:-system-architecture-\(sam-3\))

[4.1. Core Components	8](#4.1.-core-components)

[4.1.1. Perception Encoder (ViT Backbone)	8](#4.1.1.-perception-encoder-\(vit-backbone\))

[4.1.2. Decoupled Detector-Tracker	8](#4.1.2.-decoupled-detector-tracker)

[4.2. The Presence Head: Absence Modeling & False Positive Suppression	8](#4.2.-the-presence-head:-absence-modeling-&-false-positive-suppression)

[4.3. Promptable Interface Specifications	9](#4.3.-promptable-interface-specifications)

[**5\. Model Training & Optimization Strategy	10**](#5.-model-training-&-optimization-strategy)

[5.1. Configuration Management (Hydra & YAML)	10](#5.1.-configuration-management-\(hydra-&-yaml\))

[5.2. Hyperparameter Specifications	10](#5.2.-hyperparameter-specifications)

[5.2.1. Learning Rates & Schedules	10](#5.2.1.-learning-rates-&-schedules)

[5.2.2. Batch Sizing & Normalization	10](#5.2.2.-batch-sizing-&-normalization)

[5.3. Loss Function Engineering	11](#5.3.-loss-function-engineering)

[5.3.1. Focal Loss (Class Imbalance & Hard Negatives)	11](#5.3.1.-focal-loss-\(class-imbalance-&-hard-negatives\))

[5.3.2. Dice & IoU Loss (Mask Precision)	11](#5.3.2.-dice-&-iou-loss-\(mask-precision\))

[5.4. Transfer Learning Strategy	11](#5.4.-transfer-learning-strategy)

[**6\. MLOps & The Active Learning Data Engine	12**](#6.-mlops-&-the-active-learning-data-engine)

[6.1. The Active Learning Loop Workflow	12](#6.1.-the-active-learning-loop-workflow)

[6.1.1. Inference & Hard Example Mining	12](#6.1.1.-inference-&-hard-example-mining)

[6.1.2. Human-in-the-Loop (HITL) Correction	12](#6.1.2.-human-in-the-loop-\(hitl\)-correction)

[6.1.3. Auto-Annotation Acceleration	12](#6.1.3.-auto-annotation-acceleration)

[6.2. Dataset Version Control (DVC) Implementation	13](#6.2.-dataset-version-control-\(dvc\)-implementation)

[6.3. Experiment Tracking (Weights & Biases Integration)	13](#6.3.-experiment-tracking-\(weights-&-biases-integration\))

[6.4. Model Registry & Artifact Management	13](#6.4.-model-registry-&-artifact-management)

[**7\. Infrastructure & Hardware Specifications	14**](#7.-infrastructure-&-hardware-specifications)

[7.1. Compute Requirements	14](#7.1.-compute-requirements)

[7.1.1. Production Training (Enterprise)	14](#7.1.1.-production-training-\(enterprise\))

[7.1.2. Prototyping & Consumer Hardware	14](#7.1.2.-prototyping-&-consumer-hardware)

[7.2. Memory Optimization Techniques	14](#7.2.-memory-optimization-techniques)

[7.2.1. Gradient Checkpointing	15](#7.2.1.-gradient-checkpointing)

[7.2.2. Mixed Precision Training (AMP)	15](#7.2.2.-mixed-precision-training-\(amp\))

[7.3. Execution Environments	15](#7.3.-execution-environments)

[7.3.1. Cluster Execution (Submitit)	15](#7.3.1.-cluster-execution-\(submitit\))

[7.3.2. Local Execution	15](#7.3.2.-local-execution)

[**8\. Quality Assurance: Evaluation Metrics	17**](#8.-quality-assurance:-evaluation-metrics)

[8.1. Beyond mAP: The Need for Specialized Metrics	17](#8.1.-beyond-map:-the-need-for-specialized-metrics)

[8.2. Primary KPI: Classification-Gated F1 (CGF1)	17](#8.2.-primary-kpi:-classification-gated-f1-\(cgf1\))

[8.3. Component Metrics	17](#8.3.-component-metrics)

[8.3.1. Prompt-Mask F1 (pmF1)	17](#8.3.1.-prompt-mask-f1-\(pmf1\))

[8.3.2. Image-Level Matthews Correlation Coefficient (IL\_MCC)	17](#8.3.2.-image-level-matthews-correlation-coefficient-\(il_mcc\))

[8.4. Benchmarking Strategy	18](#8.4.-benchmarking-strategy)

[**9\. Deployment & Integration Strategy	19**](#9.-deployment-&-integration-strategy)

[9.1. Integration with Ultralytics Ecosystem	19](#9.1.-integration-with-ultralytics-ecosystem)

[9.1.1. Phase 1: Hybrid Workflow (Current State)	19](#9.1.1.-phase-1:-hybrid-workflow-\(current-state\))

[9.1.2. Phase 2: Native Integration (Future State)	19](#9.1.2.-phase-2:-native-integration-\(future-state\))

[9.2. Inference Optimization	19](#9.2.-inference-optimization)

[9.2.1. ONNX Export	19](#9.2.1.-onnx-export)

[9.2.2. TensorRT Optimization	20](#9.2.2.-tensorrt-optimization)

[9.3. Edge Deployment Considerations	20](#9.3.-edge-deployment-considerations)

[**10\. Future Roadmap & Lifecycle Management	21**](#10.-future-roadmap-&-lifecycle-management)

[10.1. Short-term: Stabilizing the Fine-tuning Pipeline (Months 1-3)	21](#10.1.-short-term:-stabilizing-the-fine-tuning-pipeline-\(months-1-3\))

[10.2. Mid-term: Automated Active Learning Integration (Months 3-6)	21](#10.2.-mid-term:-automated-active-learning-integration-\(months-3-6\))

[10.3. Long-term: Multi-Species & Behavioral Expansion (Months 6+)	21](#10.3.-long-term:-multi-species-&-behavioral-expansion-\(months-6+\))

## 1\. Executive Summary & Product Scope {#1.-executive-summary-&-product-scope}

### 1.1. Product Vision {#1.1.-product-vision}

The **Avian Concept Segmentation System (ACSS)** aims to revolutionize automated agricultural monitoring by deploying a high-precision, semantic understanding engine capable of distinguishing target avian species ("chicken") from complex environmental noise and non-target objects ("not-chicken").

Moving beyond the constraints of traditional bounding-box detection, ACSS leverages **Meta’s Segment Anything Model 3 (SAM 3\)** to implement **Promptable Concept Segmentation (PCS)**. This system is designed to function in dynamic, open-world environments (e.g., poultry farms with variable lighting, occlusion, and clutter), providing pixel-level accuracy and robust "absence modeling" to eliminate false positives caused by visual distractors.

### 1.2. Objective: Transition from Object Detection to Promptable Concept Segmentation (PCS) {#1.2.-objective:-transition-from-object-detection-to-promptable-concept-segmentation-(pcs)}

The primary objective of this initiative is to transition the organization’s computer vision capabilities from legacy Object Detection architectures (specifically Ultralytics YOLO) to the foundation model-based SAM 3 architecture.

This transition addresses specific operational deficiencies in the current stack:

* **From Geometric to Semantic:** Shifting from "where is the object?" (bounding boxes) to "what is the concept?" (semantic masks), enabling granular morphological analysis of individual birds.  
* **From Implicit to Explicit Negative Mining:** Utilizing SAM 3’s **Presence Head** to explicitly model the "Not-Chicken" class. Unlike YOLO, which treats background implicitly, ACSS will actively train on negative samples to drive the model’s presence score to zero for non-target concepts, significantly reducing hallucinations.  
* **Unified Workflow:** Consolidating detection, segmentation, and tracking into a single "Decoupled Detector-Tracker" architecture to maintain object identity across video frames without external trackers.

### 1.3. Key Deliverables {#1.3.-key-deliverables}

The engineering and data science teams are responsible for delivering the following core components:

1. **ETL Transformation Pipeline:** A robust Python-based data engine to convert legacy **LabelMe JSON** and **Ultralytics YOLO** datasets into the **SA-Co (Segment Anything with Concepts)** JSON schema. This pipeline must handle the procedural generation of "negative" annotations for "not-chicken" images.  
2. **Fine-Tuned SAM 3 Model:** A version of the SAM 3 foundation model specifically fine-tuned on custom avian datasets, optimized to maximize the **Classification-Gated F1 (CGF1)** score.  
3. **Active Learning Data Engine:** An MLOps loop incorporating **Dataset Version Control (DVC)** and **Weights & Biases** to facilitate continuous "hard example mining" and human-in-the-loop (HITL) correction.  
4. **Deployment Artifacts:** Optimized model exports (ONNX/TensorRT) suitable for integration with edge inference systems, pending official Ultralytics API support.

### 1.4. Target Audience & Users {#1.4.-target-audience-&-users}

* **Primary Users (Development):** AI Engineers, Data Scientists, and MLOps Engineers responsible for model training, hyperparameter tuning, and infrastructure management.  
* **Secondary Users (Operational):** Agricultural Operations Managers and Veterinary Pathologists who utilize the segmentation outputs for flock counting, health monitoring, and behavior analysis.  
* **System Consumers:** Edge computing devices (e.g., NVIDIA Jetson) and cloud-based analytics dashboards consuming the inference stream.

## 2\. Strategic Context & Problem Definition {#2.-strategic-context-&-problem-definition}

### 2.1. Current Limitations: Legacy YOLO/Object Detection Architectures {#2.1.-current-limitations:-legacy-yolo/object-detection-architectures}

The current agricultural monitoring infrastructure relies on **Ultralytics YOLO** (You Only Look Once) architectures. While efficient for high-speed detection, these models present fundamental limitations when applied to precision avian analysis:

* **Geometric Constraints:** YOLO models output bounding boxes. This geometric approximation is insufficient for biological entities with irregular shapes (e.g., a chicken flapping wings or resting). Bounding boxes include significant background noise (straw, feeders), confounding downstream morphological analysis.  
* **Implicit Negative Handling:** YOLO architectures treat "background" implicitly. They are optimized to detect positive instances. When faced with "Not-Chicken" scenarios (e.g., a duck or a specific object that looks like a chicken), YOLO often struggles to suppress false positives effectively because it lacks a dedicated mechanism to model the *absence* of a specific concept.  
* **Lack of Temporal Identity:** Standard detection models process frames independently. Tracking requires external algorithms (e.g., BoT-SORT), introducing latency and potential ID switching errors during occlusion.

### 2.2. The Paradigm Shift: Visual Segmentation (PVS) vs. Concept Segmentation (PCS) {#2.2.-the-paradigm-shift:-visual-segmentation-(pvs)-vs.-concept-segmentation-(pcs)}

ACSS represents a migration from **Promptable Visual Segmentation (PVS)** to **Promptable Concept Segmentation (PCS)**, a capability unique to SAM 3\.

* **PVS (Legacy SAM 1/2):** Relies on geometric prompts (points, boxes). The model answers: *"Segment the object at pixel (x,y)."* It does not inherently understand *what* the object is.  
* **PCS (SAM 3 \- Target State):** Relies on semantic prompts (text, exemplars). The model answers: *"Find and segment all instances of the concept 'chicken' in this image."*  
  * **Mechanism:** This is achieved through a "match and update" logic where the model queries the image features against the text embedding of "chicken," allowing for open-world adaptability and zero-shot capabilities that can be fine-tuned for specific breeds or conditions.

### 2.3. The "Not-Chicken" Challenge: Importance of Negative Mining {#2.3.-the-"not-chicken"-challenge:-importance-of-negative-mining}

The most critical technical challenge—and the primary driver for adopting SAM 3—is the rigorous classification of **"Chicken" vs. "Not-Chicken."**

* **The Problem:** In open-world poultry farms, the environment contains numerous visual distractors (rocks, equipment, other bird species like ducks) that share textural similarities with chickens.  
* **The Solution (Presence Head):** ACSS utilizes SAM 3’s **Presence Head**. Unlike standard classifiers that might force a prediction with low confidence, the Presence Head explicitly models the probability of a concept's existence ($S\_{presence}$).  
* **Negative Mining Strategy:** By training on the explicit "Not-Chicken" dataset, we force the model to drive $S\_{presence} \\to 0$ for images containing distractors. This turns passive background data into active, gradient-driving "hard negatives," significantly reducing false positive rates in production.

### 2.4. Business Impact & Operational Goals {#2.4.-business-impact-&-operational-goals}

Implementing ACSS is projected to deliver the following operational benefits:

1. **High-Precision Counting:** Pixel-level masks prevent double-counting or missed detections common with overlapping bounding boxes in crowded flocks.  
2. **Health & Morphology Analysis:** Accurate segmentation allows for the calculation of bird size, posture, and feather condition, serving as early indicators for health issues or stress.  
3. **Automated Filtering:** The "Not-Chicken" capability allows the system to autonomously discard irrelevant footage (empty barns, maintenance activity) before it reaches the analytics pipeline, reducing storage and compute costs.

---

## 3\. Functional Requirements: Data Engineering (ETL) {#3.-functional-requirements:-data-engineering-(etl)}

### 3.1. Source Data Formats {#3.1.-source-data-formats}

The system must ingest and parse legacy annotation formats currently in use by the operational teams.

* **LabelMe JSON:**  
  * **Structure:** Individual JSON files per image containing `shapes` (polygons) and `label` (class names).  
  * **Limitation:** Lacks dataset-wide metadata; class names are often inconsistent (e.g., "Chicken", "chicken", "Rooster").  
* **Ultralytics YOLO (TXT):**  
  * **Structure:** Individual `.txt` files per image containing normalized coordinates (`<class-id> <x_center> <y_center> <width> <height>`).  
  * **Limitation:** Primarily geometric (bounding boxes). For SAM 3 training, these must be converted into polygonal approximations or used as prompt inputs, as SAM 3 requires segmentation masks for optimal PCS training.

### 3.2. Target Schema: SA-Co / SAM 3 JSON Structure {#3.2.-target-schema:-sa-co-/-sam-3-json-structure}

The ETL pipeline must output a single, monolithic JSON file aligned with the **SA-Co (Segment Anything with Concepts)** schema. This schema differs from standard COCO by integrating prompt-specific fields.

**Required JSON Structure:**

* **`images` Array:**  
  * `id`: Unique Integer (Internal System ID).  
  * `file_name`: Relative path to the image file.  
  * `height`, `width`: Absolute pixel dimensions.  
  * `text_input`: **CRITICAL FIELD.** This string must contain the concept prompt (e.g., "chicken"). It associates the image context with the semantic concept.  
  * `is_instance_exhaustive`: Boolean (`true/1`). Signals that all instances of the concept in the image are annotated.  
* **`annotations` Array:**  
  * `id`: Unique Integer.  
  * `image_id`: Foreign key to `images`.  
  * `category_id`: Integer mapping (e.g., 1 \= "chicken").  
  * `segmentation`: RLE or Polygon coordinates `[[x1, y1, x2, y2, ...]]`.  
  * `bbox`: `[x, y, w, h]` (Absolute pixels).  
  * `area`: Float (Area of mask).  
  * `iscrowd`: Boolean (`0` for individual birds).

### 3.3. Transformation Logic (ETL Pipeline) {#3.3.-transformation-logic-(etl-pipeline)}

The Data Engineering team must develop a Python-based ETL pipeline (`etl_processor.py`) implementing the following logic:

#### 3.3.1. Normalization & Instance ID Assignment {#3.3.1.-normalization-&-instance-id-assignment}

* **Class Mapping:** Normalize diverse labels (e.g., "rooster", "hen", "chick") to the single target concept "chicken" (Category ID: 1).  
* **Coordinate Conversion:** Convert YOLO normalized coordinates to absolute pixel values based on image dimensions.  
* **Polygon Generation:** For YOLO source data, generate polygonal masks from bounding boxes (if true segmentation data is unavailable) to satisfy the schema, acknowledging this provides a "coarse" segmentation baseline.

#### 3.3.2. Explicit Negative Sampling (Handling "Not-Chicken" Images) {#3.3.2.-explicit-negative-sampling-(handling-"not-chicken"-images)}

This logic is the cornerstone of the **Presence Head** training strategy.

* **Input:** An image identified as "Not-Chicken" (e.g., contains ducks, empty barn, equipment).  
* **Transformation Action:**  
  1. Add entry to `images` array.  
  2. Set `text_input` \= `"chicken"` (The prompt we are testing for).  
  3. **Do NOT** add any entries to the `annotations` array for this `image_id`.  
* **Result:** The data loader interprets the combination of **Prompt="chicken"** \+ **No Annotations** as a **Negative Training Example**. This drives the model to predict a Presence Score of 0.0, effectively training the model to recognize *absence*.

#### 3.3.3. Text Prompt & Annotation Mapping {#3.3.3.-text-prompt-&-annotation-mapping}

* Ensure that every positive instance of a chicken is linked to an image that contains the `text_input`: "chicken".  
* Populate the `noun_phrase` field in the annotation (if supported by the specific loader version) with the string "chicken" to reinforce the semantic link.

### 3.4. Data Validation Criteria {#3.4.-data-validation-criteria}

The ETL pipeline must pass the following validation checks before generating the final training artifact:

1. **Schema Compliance:** Output JSON must validate against the SA-Co schema definition.  
2. **File Integrity:** All `file_name` paths must resolve to existing image files on disk.  
3. **Negative Mining Verification:** Ensure that "Not-Chicken" images exist in the JSON with `text_input`\="chicken" but have an empty annotations list. A failure here (e.g., omitting the image entirely) renders the negative data useless.  
4. **Exhaustiveness Check:** `is_instance_exhaustive` must be set to `1` for all training samples to ensure the model learns to penalize missed detections.

---

## 4\. Technical Requirements: System Architecture (SAM 3\) {#4.-technical-requirements:-system-architecture-(sam-3)}

### 4.1. Core Components {#4.1.-core-components}

The ACSS is built upon the **Meta Segment Anything Model 3 (SAM 3\)** architecture. Unlike the monolithic CNNs of the past, SAM 3 is a composite system designed for multimodal interaction.

#### 4.1.1. Perception Encoder (ViT Backbone) {#4.1.1.-perception-encoder-(vit-backbone)}

* **Requirement:** The system must utilize a **Vision Transformer (ViT)** backbone (e.g., ViT-H or ViT-L) as the primary feature extractor.  
* **Function:** Processes raw input images into high-dimensional, patch-based embeddings.  
* **Justification:** Unlike YOLO’s CSPNet which focuses on edge and texture for bounding boxes, the ViT backbone captures global semantic context. This is essential for distinguishing a "chicken" from visually similar "ducks" or "beige rocks" by analyzing the relationship between patches across the entire scene.  
* **Constraint:** Due to its size (600M+ parameters), the backbone will largely remain **frozen** or be fine-tuned with a highly restricted learning rate to prevent catastrophic forgetting of general visual concepts.

#### 4.1.2. Decoupled Detector-Tracker {#4.1.2.-decoupled-detector-tracker}

* **Requirement:** The architecture must employ a **Decoupled Detector-Tracker** design.  
* **Function:**  
  * **Detector:** Uses a DETR-based (Detection Transformer) mechanism to query image features based on the prompt "chicken". It proposes candidate regions.  
  * **Tracker:** Maintains a "Memory Bank" of object states across video frames.  
* **Capability:** This component enables the system to handle **temporal occlusion**. If a chicken walks behind a feeder and re-emerges, the Tracker utilizes the Memory Bank to re-associate the new detection with the previous ID, eliminating the need for external algorithms like DeepSORT.

### 4.2. The Presence Head: Absence Modeling & False Positive Suppression {#4.2.-the-presence-head:-absence-modeling-&-false-positive-suppression}

The **Presence Head** is the critical architectural differentiator for the "Chicken vs. Not-Chicken" task.

* **Requirement:** The model must output a global scalar score ($S\_{presence}$) representing the probability of the concept's existence in the image *before* generating segmentation masks.  
* **Mathematical Logic:** The final confidence for any segmented instance $i$ must be modulated by this score: $$S\_{final}^i \= S\_{presence} \\times S\_{local}^i$$  
* **Operational Behavior:**  
  * **Input:** Image of an empty barn or a duck ("Not-Chicken").  
  * **Target Output:** $S\_{presence} \\to 0$.  
  * **Result:** This effectively suppresses all potential false positive masks in the image globally. It replaces the reliance on arbitrary "confidence thresholds" used in legacy object detectors with a learned, semantic probability of absence.

### 4.3. Promptable Interface Specifications {#4.3.-promptable-interface-specifications}

The system must support multimodal prompting to interact with the underlying model components.

* **Primary Input (Text Prompt):**  
  * **Input:** String literal `"chicken"`.  
  * **Processing:** The text is tokenized and embedded via a Text Encoder. This embedding serves as the "query" for the Detector to locate matching visual features.  
* **Secondary Input (Spatial Prompts):**  
  * **Input:** Points $(x, y)$ or Bounding Boxes $\[x, y, w, h\]$.  
  * **Use Case:** Reserved for **Human-in-the-Loop (HITL)** corrections. If the model misses a chicken, a human annotator provides a point prompt. The model must accept this geometric constraint to force-generate a mask at that location, which is then added to the training set as a "hard example."

---

## 5\. Model Training & Optimization Strategy {#5.-model-training-&-optimization-strategy}

### 5.1. Configuration Management (Hydra & YAML) {#5.1.-configuration-management-(hydra-&-yaml)}

The training pipeline shall utilize **Hydra** for configuration management, ensuring reproducibility and modularity. A master `config.yaml` file acts as the single source of truth for each experiment.

* **Requirement:** Create a custom configuration file (e.g., `configs/sam3_chicken_finetune.yaml`) inheriting from the model's base configuration.  
* **Key Configuration Blocks:**  
  * `model_config`: Specifies the ViT backbone architecture (e.g., `vit_h`).  
  * `data_config`: Pointers to the SA-Co JSON training/validation sets.  
  * `optimizer_config`: Defines the optimizer (AdamW) and weight decay settings.  
  * `loss_config`: Explicit weights for individual loss components (Focal, Dice, IoU).

### 5.2. Hyperparameter Specifications {#5.2.-hyperparameter-specifications}

To optimize convergence and stability on the avian dataset, the following hyperparameter ranges are established:

#### 5.2.1. Learning Rates & Schedules {#5.2.1.-learning-rates-&-schedules}

* **Initial Learning Rate (LR):** Set between **1e-5** and **1e-4**.  
  * *Justification:* Foundation models like SAM 3 require conservative learning rates to avoid "catastrophic forgetting" of pre-trained knowledge.  
* **Scheduler:** Implement **Cosine Annealing** with a linear **Warm-up** period (first 5-10% of epochs).  
  * *Function:* Warm-up stabilizes gradients during the initial adaptation to the "Not-Chicken" negative samples, while cosine annealing facilitates efficient convergence into local minima.

#### 5.2.2. Batch Sizing & Normalization {#5.2.2.-batch-sizing-&-normalization}

* **Batch Size:** Target **8 to 32** per GPU, dependent on VRAM availability.  
  * *Constraint:* If batch size \< 8 (due to VRAM limits), **Gradient Accumulation** must be enabled to simulate a larger effective batch size and stabilize Batch Normalization statistics.  
* **Input Resolution:** Fixed at **1024x1024** pixels. Images must be resized/padded to this resolution during the data loading phase.

### 5.3. Loss Function Engineering {#5.3.-loss-function-engineering}

The loss function is a composite metric engineered to balance presence detection against segmentation precision.

$$L\_{total} \= \\lambda\_{focal}L\_{focal} \+ \\lambda\_{dice}L\_{dice} \+ \\lambda\_{iou}L\_{iou}$$

#### 5.3.1. Focal Loss (Class Imbalance & Hard Negatives) {#5.3.1.-focal-loss-(class-imbalance-&-hard-negatives)}

* **Role:** Primary driver for the **Presence Head**.  
* **Target:** Optimizes the classification of "Chicken" vs. "Not-Chicken."  
* **Configuration:** High priority weight ($\\lambda\_{focal} \\approx 2.0 \- 5.0$).  
* **Mechanism:** Down-weights easy examples (obvious background) and focuses training on "Hard Negatives" (e.g., ducks, similar textures). This effectively penalizes the model when it hallucinates chickens in "Not-Chicken" images.

#### 5.3.2. Dice & IoU Loss (Mask Precision) {#5.3.2.-dice-&-iou-loss-(mask-precision)}

* **Role:** Optimizes the **Mask Generator**.  
* **Target:** Maximizes the geometric overlap between the predicted mask and the ground truth polygon.  
* **Condition:** calculated *only* when the ground truth indicates a positive presence.  
* **Configuration:** Balanced weights ($\\lambda\_{dice} \\approx 1.0, \\lambda\_{iou} \\approx 1.0$).

### 5.4. Transfer Learning Strategy {#5.4.-transfer-learning-strategy}

* **Frozen Backbone (Perception Encoder):**  
  * **Strategy:** The weights of the generic Vision Transformer backbone shall be **Frozen** (or set to an extremely low LR relative to the heads).  
  * **Reasoning:** The backbone already understands general edges, textures, and biological shapes from the SA-Co pre-training. Freezing it drastically reduces VRAM usage and training time.  
* **Active Fine-Tuning (Heads):**  
  * **Strategy:** Gradients are computed primarily for the **Prompt Encoder**, **Mask Decoder**, and **Presence Head**.  
  * **Reasoning:** These components are responsible for mapping the semantic concept "chicken" to the specific visual features extracted by the backbone.

---

## 6\. MLOps & The Active Learning Data Engine {#6.-mlops-&-the-active-learning-data-engine}

### 6.1. The Active Learning Loop Workflow {#6.1.-the-active-learning-loop-workflow}

To combat model drift and address the "open-world" nature of agricultural environments, the system shall not rely on a static training set. Instead, it must implement a continuous **Active Learning Data Engine**.

#### 6.1.1. Inference & Hard Example Mining {#6.1.1.-inference-&-hard-example-mining}

* **Requirement:** An automated inference pipeline must process batches of unlabeled raw imagery from production feeds.  
* **Mining Logic:** The system shall filter and flag "Hard Examples" for human review based on specific uncertainty thresholds:  
  * **Ambiguity Range:** Images where the **Presence Score ($S\_{presence}$)** falls between **0.4 and 0.6**. These indicate the model is unsure if a chicken is present (e.g., a shadow looking like a bird).  
  * **Borderline Segmentation:** Instances where the mask confidence or IoU score is low, suggesting difficult occlusion or unusual lighting.  
* **Output:** A subset of "flagged" images is routed to the annotation queue, prioritizing the data that will provide the highest gradient signal during retraining.

#### 6.1.2. Human-in-the-Loop (HITL) Correction {#6.1.2.-human-in-the-loop-(hitl)-correction}

* **Requirement:** Integration with an annotation tool (e.g., LabelMe, CVAT, or Roboflow) to allow human experts to review flagged images.  
* **Workflow:**  
  * **False Positive Correction:** If the model detected a "Chicken" in a "Not-Chicken" image (e.g., a rock), the human must explicitly remove the annotation, confirming it as a negative sample.  
  * **False Negative Correction:** If the model missed a chicken, the human must add the instance.

#### 6.1.3. Auto-Annotation Acceleration {#6.1.3.-auto-annotation-acceleration}

* **Requirement:** The annotation tool must utilize SAM 3’s interactive inference API to accelerate labeling.  
* **Functionality:** Instead of manually drawing polygons, annotators shall use **Point Prompts** (clicking on the object).  
* **System Action:** The backend SAM 3 model generates a high-precision mask based on the click. The annotator only accepts or slightly refines the mask. This reduces labeling time per instance by approximately **10x** compared to manual polygon creation.

### 6.2. Dataset Version Control (DVC) Implementation {#6.2.-dataset-version-control-(dvc)-implementation}

* **Requirement:** **DVC (Data Version Control)** must be implemented to manage large binary image datasets, decoupling them from the lightweight codebase managed in Git.  
* **Storage Architecture:**  
  * **Local/Git:** Stores `.dvc` placeholder files (metadata pointers).  
  * **Remote Storage:** An S3 bucket or shared network drive stores the actual image and JSON blobs.  
* **Versioning Protocol:** Every iteration of the dataset (e.g., `v1.0-baseline`, `v2.0-hard-negatives-added`) must be tagged. This allows the team to mathematically reproduce any historical model by checking out the specific data commit hash used for training.

### 6.3. Experiment Tracking (Weights & Biases Integration) {#6.3.-experiment-tracking-(weights-&-biases-integration)}

* **Requirement:** All training runs must be logged to a centralized **Weights & Biases (WandB)** dashboard.  
* **Captured Metadata:**  
  * **Hyperparameters:** Learning rate, batch size, loss weights ($\\lambda\_{focal}, \\lambda\_{dice}$).  
  * **Data Lineage:** The specific DVC commit hash used for the run.  
  * **Performance Metrics:** Real-time graphs of Training Loss, Validation Loss, and the critical **CGF1** score.  
  * **System Metrics:** GPU VRAM usage and temperature to monitor infrastructure health.

### 6.4. Model Registry & Artifact Management {#6.4.-model-registry-&-artifact-management}

* **Requirement:** A formal Model Registry must be established to manage the lifecycle of trained artifacts.  
* **Artifacts:** For each successful training run, the system must archive:  
  1. The PyTorch model weights (`.pt`).  
  2. The exact `config.yaml` used.  
  3. A validation report comparing the model against the Zero-Shot baseline.  
* **Promotion Logic:** Only models that demonstrate a statistically significant improvement in **CGF1** on the "Hard Negative" holdout set shall be tagged as `production-candidate` and promoted to the deployment pipeline.

---

## 7\. Infrastructure & Hardware Specifications {#7.-infrastructure-&-hardware-specifications}

### 7.1. Compute Requirements {#7.1.-compute-requirements}

Training a foundation model architecture like SAM 3 requires significant computational throughput and Video RAM (VRAM) capacity. The choice of hardware directly impacts the allowable batch size, which is critical for the stability of the **Presence Head** (ensuring a mix of positive and negative samples in every update).

#### 7.1.1. Production Training (Enterprise) {#7.1.1.-production-training-(enterprise)}

For full-scale fine-tuning and production model generation, the system requires Data Center class GPUs.

* **Recommended Hardware:** **NVIDIA A100 (40GB/80GB)** or **NVIDIA H100 (80GB)**.  
* **Justification:**  
  * **VRAM Capacity:** 40GB+ allows for batch sizes $\\ge 16$ at $1024 \\times 1024$ resolution. High batch sizes provide a more accurate estimate of the gradient, essential for converging on the delicate "Chicken vs. Not-Chicken" decision boundary.  
  * **Throughput:** The Transformer Engine in H100s significantly accelerates the Vision Transformer (ViT) backbone computations.  
* **Minimum Enterprise Spec:** NVIDIA V100 (32GB). Note: This may require reducing batch sizes, potentially necessitating Gradient Accumulation to maintain training stability.

#### 7.1.2. Prototyping & Consumer Hardware {#7.1.2.-prototyping-&-consumer-hardware}

For initial debugging, code development, or small-scale experiments, consumer-grade hardware is permissible but requires strict optimization.

* **Supported Hardware:** **NVIDIA RTX 3090 / 4090 (24GB)**.  
* **Limitations:**  
  * Restricted to small batch sizes (approx. 2-4 images per GPU).  
  * Must rely heavily on memory optimization techniques (see 7.2) to prevent OOM (Out of Memory) errors.  
  * Multi-GPU scaling is limited due to the lack of high-speed NVLink interconnects found in data center cards.

### 7.2. Memory Optimization Techniques {#7.2.-memory-optimization-techniques}

To maximize the utility of available VRAM and allow for training larger models (e.g., ViT-Huge) on limited hardware, the following techniques must be implemented in the training configuration.

#### 7.2.1. Gradient Checkpointing {#7.2.1.-gradient-checkpointing}

* **Requirement:** Enable Gradient Checkpointing in the `model_config`.  
* **Function:** Instead of storing all intermediate activations during the forward pass (consuming massive memory), the system re-computes them during the backward pass.  
* **Trade-off:** Reduces VRAM usage by approximately **30-50%** at the cost of a slight increase in computation time ($\\approx 20%$ slower). This trade-off is acceptable and often necessary to fit the model into 24GB or 32GB VRAM.

#### 7.2.2. Mixed Precision Training (AMP) {#7.2.2.-mixed-precision-training-(amp)}

* **Requirement:** Utilize `torch.cuda.amp` for Automatic Mixed Precision.  
* **Configuration:**  
  * **FP16 (Half-Precision):** Standard for V100/RTX 3090\.  
  * **BF16 (Brain Float 16):** Mandatory for A100/H100. BF16 provides the dynamic range of FP32 with the memory footprint of FP16, preventing numerical instability (NaN losses) often seen when training large Transformers.  
* **Impact:** Halves the memory required for weights and gradients, significantly increasing the maximum possible batch size.

### 7.3. Execution Environments {#7.3.-execution-environments}

The training scripts must support two distinct execution modes controlled via command-line arguments.

#### 7.3.1. Cluster Execution (Submitit) {#7.3.1.-cluster-execution-(submitit)}

* **Flag:** `--use-cluster 1`  
* **Context:** For use on High-Performance Computing (HPC) clusters managed by **SLURM**.  
* **Mechanism:** The script utilizes the `submitit` library to automatically dispatch jobs to compute nodes.  
* **Configuration:** The `launcher` section in `config.yaml` must define the partition, QoS (Quality of Service), and timeout parameters specific to the organization’s cluster. This mode is required for distributed multi-node training.

#### 7.3.2. Local Execution {#7.3.2.-local-execution}

* **Flag:** `--use-cluster 0`  
* **Context:** For use on single workstations, solitary cloud instances (e.g., AWS EC2, Lambda Labs), or debugging sessions.  
* **Mechanism:** Runs the training loop as a direct Python process on the host machine.  
* **Use Case:** Development of the ETL pipeline, testing `config` syntax, and running short "sanity check" epochs before launching expensive cluster jobs.

---

## 8\. Quality Assurance: Evaluation Metrics {#8.-quality-assurance:-evaluation-metrics}

### 8.1. Beyond mAP: The Need for Specialized Metrics {#8.1.-beyond-map:-the-need-for-specialized-metrics}

Standard object detection metrics, such as **mean Average Precision (mAP)**, are insufficient for the "Chicken vs. Not-Chicken" paradigm. mAP primarily penalizes missed detections (False Negatives) and poor localization. However, it often fails to adequately penalize **hallucinations** (False Positives) in images that are completely empty of the target class ("Not-Chicken" images).

For ACSS, the ability to **correctly identify the absence** of a chicken is as critical as identifying its presence. Therefore, the evaluation strategy must decouple "Detection/Presence" performance from "Segmentation/Mask" performance.

### 8.2. Primary KPI: Classification-Gated F1 (CGF1) {#8.2.-primary-kpi:-classification-gated-f1-(cgf1)}

The holistic success of the model shall be measured by the **Classification-Gated F1 (CGF1)** score. This composite metric ensures the model is penalized effectively if it generates high-quality masks for objects that do not exist (hallucinations) or fails to identify the presence of the concept entirely.

**Formula:** $$CGF1 \= pmF1 \\times IL\_MCC$$ *(Scaled to 0-100 range for reporting)*

### 8.3. Component Metrics {#8.3.-component-metrics}

To diagnose model behavior, the CGF1 is broken down into its constituent parts:

#### 8.3.1. Prompt-Mask F1 (pmF1) {#8.3.1.-prompt-mask-f1-(pmf1)}

* **Definition:** The harmonic mean of Precision and Recall for the segmentation masks, calculated **only** on positive samples where the model correctly predicted the presence of a chicken.  
* **Question Answered:** *"When the model sees a chicken, how accurately does it draw the outline?"*  
* **Target:** High pmF1 indicates precise morphological understanding (feathers, beak, feet are included; background straw is excluded).

#### 8.3.2. Image-Level Matthews Correlation Coefficient (IL\_MCC) {#8.3.2.-image-level-matthews-correlation-coefficient-(il_mcc)}

* **Definition:** A correlation coefficient between the predicted presence (binary: Yes/No) and the ground truth presence.  
* **Range:** \-1 (Inverse prediction) to \+1 (Perfect prediction), with 0 being random guessing.  
* **Question Answered:** *"Did the model correctly identify that this image contains (or does not contain) a chicken?"*  
* **Critical Function:** This is the metric that validates the **Presence Head**. A high IL\_MCC proves the model has successfully learned to suppress false positives in "Not-Chicken" scenarios (ducks, empty barns).  
* **Diagnostic Signal:**  
  * **High pmF1 / Low IL\_MCC:** The model segments chickens well but hallucinates them everywhere (over-sensitive). *Action: Increase Focal Loss weight on negative samples.*  
  * **Low pmF1 / High IL\_MCC:** The model correctly identifies when chickens are present but draws poor masks. *Action: Increase Dice/IoU Loss weights.*

### 8.4. Benchmarking Strategy {#8.4.-benchmarking-strategy}

To quantify the ROI of the fine-tuning effort, performance must be compared against a strict baseline.

1. **Zero-Shot Baseline:**  
   * Execute the pre-trained, "out-of-the-box" SAM 3 model on the validation dataset using the generic prompt "chicken".  
   * Record CGF1, pmF1, and IL\_MCC. This establishes the "floor" performance of the foundation model without domain adaptation.  
2. **Fine-Tuned Performance:**  
   * Execute the custom-trained ACSS model on the same validation set.  
   * **Success Criteria:** The Fine-Tuned model must demonstrate a statistically significant improvement in **IL\_MCC** (indicating better handling of the specific farm environment and distractors) compared to the Zero-Shot baseline.  
3. **Hard Negative Holdout:**  
   * A specific subset of the validation set shall consist **exclusively** of "Not-Chicken" images (ducks, equipment, empty coops).  
   * **Requirement:** The model must achieve a near-zero average Presence Score on this subset. Any detection here is a critical failure.

---

## 9\. Deployment & Integration Strategy {#9.-deployment-&-integration-strategy}

### 9.1. Integration with Ultralytics Ecosystem {#9.1.-integration-with-ultralytics-ecosystem}

The operational goal is to integrate the fine-tuned SAM 3 model into the organization’s existing computer vision pipelines, which utilize the Ultralytics framework. However, due to the evolving nature of foundation model support, a phased integration strategy is required.

#### 9.1.1. Phase 1: Hybrid Workflow (Current State) {#9.1.1.-phase-1:-hybrid-workflow-(current-state)}

As of late 2025, native training support for SAM 3 within the `ultralytics` package is in active development.

* **Training:** Must occur within the upstream **Meta Research (`facebookresearch/sam3`)** repository using the configuration and datasets defined in Chapters 3-5.  
* **Inference:** The trained weights (`.pt`) shall be loaded using the `Sam3Predictor` class from the Meta repository or wrapped in a custom Python inference service.  
* **Constraint:** Direct usage of `yolo predict model=custom_sam3.pt` may not support all PCS features (specifically the Presence Head logic) immediately. The engineering team must write a wrapper script to handle the text prompt injection ("chicken") during inference.

#### 9.1.2. Phase 2: Native Integration (Future State) {#9.1.2.-phase-2:-native-integration-(future-state)}

* **Target:** Migration to full Ultralytics native support upon the release of **Ultralytics v8.3.x** (or equivalent feature update).  
* **Capability:** This will enable standard syntax: `yolo segment predict model=sam3_chicken.pt source=stream.mp4 args="chicken"`.  
* **Preparation:** The Data Engineering team must maintain the dataset in the **SA-Co JSON** format. This ensures that when the official Ultralytics SAM 3 data loader is released, no re-annotation or complex re-formatting will be required.

### 9.2. Inference Optimization {#9.2.-inference-optimization}

To achieve real-time performance, particularly given the heavy Vision Transformer backbone, the model must be compiled and optimized for the target hardware.

#### 9.2.1. ONNX Export {#9.2.1.-onnx-export}

* **Requirement:** The training pipeline must include an export step to convert the PyTorch checkpoint to **ONNX (Open Neural Network Exchange)** format.  
* **Architecture Handling:** The export process must handle the decoupled nature of SAM 3:  
  * **Encoder Export:** The heavy ViT backbone exported as a static graph.  
  * **Decoder/Prompt Encoder Export:** The lightweight heads exported to accept dynamic prompts.  
* **Benefit:** ONNX provides a platform-agnostic intermediate representation, allowing the model to be run on non-PyTorch runtimes (e.g., ONNX Runtime, OpenVINO).

#### 9.2.2. TensorRT Optimization {#9.2.2.-tensorrt-optimization}

* **Requirement:** For deployment on NVIDIA hardware (Data Center or Edge), the ONNX model must be compiled into a **TensorRT Engine (`.engine` or `.trt`)**.  
* **Quantization:**  
  * **FP16:** Mandatory. Converting FP32 weights to FP16 reduces memory bandwidth pressure and utilizes Tensor Cores.  
  * **INT8:** Optional/Experimental. Post-training quantization to INT8 may be explored for maximum throughput, provided the **CGF1** score does not degrade by more than 2%.  
* **Performance Target:** The optimized engine must achieve **\>15 FPS** on target hardware (e.g., NVIDIA Jetson Orin or RTX 40-series) to support live monitoring.

### 9.3. Edge Deployment Considerations {#9.3.-edge-deployment-considerations}

Deploying SAM 3 to edge devices (e.g., cameras inside poultry houses) requires specific architectural strategies to manage resource constraints.

* **Prompt Injection:** Unlike YOLO, which simply runs on an image, the deployment container must explicitly inject the text prompt `"chicken"` (tokenized) into every inference call. The system must be hard-coded to query this specific concept.  
* **Backbone Caching (Video Optimization):**  
  * **Strategy:** Leveraging SAM 3's temporal consistency, the heavy Perception Encoder does *not* necessarily need to run at full frame rate if the camera view is static.  
  * **Implementation:** Run the Detector (and full backbone) at a lower frequency (e.g., 1 Hz) to detect new birds or major scene changes. Run the **Tracker** (lightweight) at full frequency (30 Hz) to update the positions of known instances using the Memory Bank.  
  * **Impact:** This split-compute strategy significantly reduces the thermal and power load on edge devices.

---

## 10\. Future Roadmap & Lifecycle Management {#10.-future-roadmap-&-lifecycle-management}

### 10.1. Short-term: Stabilizing the Fine-tuning Pipeline (Months 1-3) {#10.1.-short-term:-stabilizing-the-fine-tuning-pipeline-(months-1-3)}

The immediate focus is to establish a reproducible and scientifically valid baseline for the ACSS.

* **Pipeline Validation:** Achieve end-to-end automation of the ETL process (`LabelMe` $\\to$ `SA-Co JSON`) without manual intervention or schema errors.  
* **"Not-Chicken" Proof of Concept:** Empirically validate the hypothesis that the **Presence Head** significantly reduces false positives. This will be confirmed when the **IL\_MCC** metric on the "Hard Negative" holdout set exceeds **0.85**.  
* **Manual Active Learning:** Execute one manual cycle of the "Data Engine" loop:  
  1. Train Model v1.0.  
  2. Run inference on 1,000 unlabeled images.  
  3. Manually identify low-confidence failures.  
  4. Retrain Model v1.1 and measure the delta in **CGF1**.

### 10.2. Mid-term: Automated Active Learning Integration (Months 3-6) {#10.2.-mid-term:-automated-active-learning-integration-(months-3-6)}

Transition from manual oversight to an automated MLOps workflow.

* **Automated Mining Triggers:** Implement logic in the inference pipeline that automatically routes images with **Presence Scores between 0.4 and 0.6** to the annotation queue via API (e.g., sending data to LabelMe/CVAT automatically).  
* **Auto-Annotation Deployment:** Equip the annotation team with the **SAM 3 Point-Prompting** tool. The goal is to reduce the average time-to-label per bird from 30 seconds (polygon drawing) to \<3 seconds (click-and-verify).  
* **Continuous Deployment (CD) for Models:** Establish a gate where if a new model version improves **CGF1** by \>1% without degrading inference speed, it is automatically converted to TensorRT and pushed to the staging environment.

### 10.3. Long-term: Multi-Species & Behavioral Expansion (Months 6+) {#10.3.-long-term:-multi-species-&-behavioral-expansion-(months-6+)}

Once the "Chicken vs. Not-Chicken" capability is mature, the system capabilities will be expanded to address broader operational needs.

* **Multi-Class Segmentation:** Move beyond binary classification to multi-class PCS.  
  * *Prompts:* "chicken", "duck", "human", "egg", "feeder".  
  * *Objective:* Monitor interaction between species and equipment usage.  
* **Morphological Health Analysis:** Leverage the high-precision masks to infer biological data.  
  * *Metrics:* Plumage quality (smooth vs. ruffled edges in the mask), growth rates (pixel area tracking over time), and gait analysis (using the Tracker’s trajectory data).  
* **Behavioral Concept Prompting:** Experiment with action-based prompts.  
  * *Prompts:* "eating chicken", "sleeping chicken".  
  * *Feasibility:* This requires temporal training data but allows for automated welfare monitoring without dedicated activity recognition models.

**End of Product Requirements Document.**

