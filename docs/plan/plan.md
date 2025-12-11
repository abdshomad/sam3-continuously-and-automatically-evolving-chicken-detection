\[PLAN\] Implementation Plan 

Here is the detailed implementation plan for **Phase 1: Environment Setup & Infrastructure Initialization**.

This phase establishes the foundational hardware and software stack required to support the SAM 3 architecture, ensuring that the heavy computational requirements defined in **PRD Chapter 7** are met before data processing begins.

### **Phase 1: Environment Setup & Infrastructure Initialization**

#### **Step 1.1: Hardware Provisioning & Driver Verification**

**Objective:** Ensure the compute environment (Cluster or Local Workstation) has sufficient VRAM and compatible CUDA drivers to run the Vision Transformer backbone.

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **1.1.1** | **GPU Availability Check** | Run `nvidia-smi`. Verify GPU model (Target: A100/H100 or RTX 3090/4090). Ensure Driver Version $\\ge$ 525.xx. | \[x\] Script Created | 2025-12-12 |
| **1.1.2** | **CUDA Toolkit Verification** | Run `nvcc --version`. Ensure compatibility with PyTorch 2.x (Target: CUDA 11.8 or 12.1). | \[x\] Script Created | 2025-12-12 |
| **1.1.3** | **VRAM Health Check** | Ensure no other processes are consuming VRAM. For 24GB cards, ensure 100% availability. | \[x\] Script Created | 2025-12-12 |
| **1.1.4** | **Disk Space Allocation** | Provision fast storage (NVMe preferred) for the dataset. Reserve \~100GB+ for images and checkpoints. | \[x\] Script Created | 2025-12-12 |

#### **Step 1.2: Repository Setup & Dependency Installation**

**Objective:** Deploy the Meta SAM 3 codebase and install the necessary Python libraries for training and configuration management (Hydra).

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **1.2.1** | **Add SAM 3 as Git Submodule** | `git submodule add https://github.com/facebookresearch/sam3.git sam3` \`git submodule update --init --recursive\` | \[x\] Script Created | 2025-12-12 |
| **1.2.2** | **Create Virtual Environment** | Create a dedicated virtual environment using uv to prevent conflicts: \`uv venv\` \`source .venv/bin/activate\` (or \`source .venv/Scripts/activate\` on Windows) | \[x\] Script Created | 2025-12-12 |
| **1.2.3** | **Install PyTorch** | Install Pytorch with CUDA support: \`pip install torch torchvision \--index-url https://download.pytorch.org/whl/cu118\` (Adjust for CUDA version) | \[x\] Script Created | 2025-12-12 |
| **1.2.4** | **Install SAM 3 Dependencies** | Install core requirements and Hydra/Submitit: \`pip install \-e sam3/\` \`pip install hydra-core submitit\` | \[x\] Script Created | 2025-12-12 |
| **1.2.5** | **Download Pre-trained Weights** | Download the official SAM 3 checkpoint (e.g., `sam3_vit_h.pt`) to the `checkpoints/` directory. | \[x\] Script Created | 2025-12-12 |

#### **Step 1.3: Weights & Biases (WandB) & DVC Configuration**

**Objective:** Initialize the MLOps tools defined in **PRD Chapter 6** to track experiments and version the data from day one.

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **1.3.1** | **WandB Initialization** | Install and login to Weights & Biases: \`pip install wandb\` \`wandb login \` | \[x\] Script Created | 2025-12-12 |
| **1.3.2** | **DVC Initialization** | Initialize DVC in the project root: \`pip install dvc\` \`dvc init\` | \[x\] Script Created | 2025-12-12 |
| **1.3.3** | **Configure Remote Storage** | Set up the remote storage for DVC (S3, GDrive, or Shared Network Drive): \`dvc remote add \-d storage s3:///chicken-data\` | \[x\] Script Created | 2025-12-12 |
| **1.3.4** | **Verify Logging Integration** | Run a dummy Python script importing `wandb` to ensure it can reach the dashboard servers from the training node. | \[x\] Script Created | 2025-12-12 |

---

### **Phase 2: Data Engineering (ETL) & Schema Transformation**

#### **Step 2.1: Source Data Audit & Preparation**

**Objective:** Standardize the input directory structure and verify that "Not-Chicken" samples are clearly identifiable (either by folder organization or empty annotation files) before processing.

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **2.1.1** | **Directory Structure Setup** | Organize data into: \`raw\_data/images/chicken/\` \`raw\_data/images/not\_chicken/\` \`raw\_data/labels/\` (matching filenames) | \[x\] Script Created | 2025-12-12 |
| **2.1.2** | **Label Normalization** | Scan LabelMe JSONs/YOLO classes.txt. Create a mapping dictionary to merge synonymous tags (e.g., `{"rooster": "chicken", "chick": "chicken"}`). | \[x\] Script Created | 2025-12-12 |
| **2.1.3** | **Negative Sample Verification** | Ensure "Not-Chicken" images either have:  1\. No corresponding label file. 2\. An empty label file. 3\. Are located in the specific \`not\_chicken\` directory. | \[x\] Script Created | 2025-12-12 |

#### **Step 2.2: Developing the `etl_processor.py` (Conversion Logic)**

**Objective:** Write the Python script to parse source files and map them to the SA-Co `images` and `annotations` arrays.

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **2.2.1** | **Image Metadata Extraction** | Script must read image height/width.  \*\*Crucial:\*\* Set \`text\_input: "chicken"\` for \*every\* image (both positive and negative) in the \`images\` list. | \[x\] Script Created | 2025-12-12 |
| **2.2.2** | **YOLO BBox to Polygon Conversion** | For YOLO .txt inputs: Use `cv2` or `shapely` to convert normalized `[x,y,w,h]` into a 4-point polygon `[[x1,y1, x2,y1, x2,y2, x1,y2]]`. SAM 3 prefers polygons over simple boxes. | \[x\] Script Created | 2025-12-12 |
| **2.2.3** | **LabelMe Parsing** | Parse `points` from JSON. Convert to flat list format `[x1, y1, x2, y2, ...]` required by SA-Co segmentation field. | \[x\] Script Created | 2025-12-12 |
| **2.2.4** | **Exhaustiveness Flagging** | Set `is_instance_exhaustive: true` (or `1`) for all images to instruct the loss function that unannotated regions are true backgrounds. | \[x\] Script Created | 2025-12-12 |

#### **Step 2.3: Implementing Explicit Negative Mining (The "Not-Chicken" Logic)**

**Objective:** Implement the logic that creates the "Hard Negative" training signal for the Presence Head.

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **2.3.1** | **Negative Image Processing** | Condition: If image is in `not_chicken` folder OR has 0 annotations. Action: Add to \`images\` list with \`text\_input: "chicken"\`. \*\*Do NOT\*\* add any entry to \`annotations\` list. | \[x\] Script Created | 2025-12-12 |
| **2.3.2** | **Ambiguous Class Exclusion** | If the dataset contains "ambiguous" classes (e.g., "unknown bird") that are neither clearly chicken nor clearly background, exclude these images to prevent confusing the model. | \[x\] Script Created | 2025-12-12 |

#### **Step 2.4: JSON Validation & Dataset Splitting**

**Objective:** Finalize the dataset artifacts and ensure they conform to the schema before training.

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **2.4.1** | **Generate JSON Artifacts** | Run script to output `chicken_train.json` (80%) and `chicken_val.json` (20%). Ensure stratified sampling so both sets contain "Not-Chicken" examples. | \[x\] Script Created | 2025-12-12 |
| **2.4.2** | **Schema Validation** | Use `pycocotools` or a custom schema validator to check for type errors (e.g., ensure `id` is int, `segmentation` is list of lists). | \[x\] Script Created | 2025-12-12 |
| **2.4.3** | **Version Data with DVC** | Commit the new JSONs and the raw image directory to DVC: \`dvc add data/images\` \`dvc add data/annotations\` \`git commit \-m "Create v1.0 SA-Co dataset"\` | \[x\] Script Created | 2025-12-12 |

---

### **Phase 3: Baseline Evaluation & Configuration Strategy**

#### **Step 3.1: Zero-Shot Baseline Establishment**

**Objective:** Run the pre-trained SAM 3 model on the validation set *without* fine-tuning to quantify its default behavior. This establishes the benchmark for calculating ROI (Improvement in CGF1).

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **3.1.1** | **Run Zero-Shot Inference** | Execute the evaluation script using the base checkpoint: \`python sam3/eval/evaluate.py \--config configs/base\_eval.yaml \--checkpoint checkpoints/sam3\_vit\_h.pt \--json data/chicken\_val.json\` | \[x\] Script Created | 2025-12-12 |
| **3.1.2** | **Calculate Baseline Metrics** | Log the initial scores: 1\. \*\*pmF1:\*\* (Likely high for generic objects) 2\. \*\*IL\_MCC:\*\* (Likely low/random, as the model may hallucinate chickens in empty barns). 3\. \*\*CGF1:\*\* (Composite score). | \[x\] Script Created | 2025-12-12 |
| **3.1.3** | **Analyze False Positives** | Manually inspect the "Not-Chicken" subset results. Confirm if the model detects background objects (straw, feeders) as chickens. This confirms the need for fine-tuning. | \[x\] Script Created | 2025-12-12 |

#### **Step 3.2: Constructing the Hydra Configuration (`.yaml`)**

**Objective:** Create the master configuration file that governs the training pipeline, pointing it to the new SA-Co datasets and defining the architecture behavior.

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **3.2.1** | **Create Experiment Config** | Create `configs/sam3_chicken_finetune.yaml`. Inherit from the default fine-tuning config (e.g., `defaults: [roboflow_v100_ft]`). | \[x\] Script Created | 2025-12-12 |
| **3.2.2** | **Define Dataset Paths** | Update the `dataset` block: \`train\_json: "data/chicken\_train.json"\` \`val\_json: "data/chicken\_val.json"\` \`img\_dir: "data/images"\` | \[x\] Script Created | 2025-12-12 |
| **3.2.3** | **Set Prompt Mode** | Ensure the data loader is configured for PCS: \`use\_text\_prompts: True\` \`prompt\_column: "text\_input"\` | \[x\] Script Created | 2025-12-12 |
| **3.2.4** | **Hardware Optimization** | Enable memory savers in config: \`model.use\_gradient\_checkpointing: True\` \`trainer.precision: "bf16"\` (if A100) or \`"fp16"\` (if V100/RTX). | \[x\] Script Created | 2025-12-12 |

#### **Step 3.3: Loss Function & Hyperparameter Definition**

**Objective:** Engineer the loss function to prioritize **Negative Mining** (learning from the "Not-Chicken" images) via the Presence Head.

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **3.3.1** | **Configure Learning Rate** | Set a conservative LR schedule to protect the backbone: \`optimizer.lr: 1e-5\` \`scheduler: "cosine\_with\_warmup"\` | \[x\] Script Created | 2025-12-12 |
| **3.3.2** | **Engineer Loss Weights** | **CRITICAL:** Boost the Focal Loss to penalize hallucinations. \`loss.focal\_loss\_weight: 5.0\` (High priority for Presence) \`loss.dice\_loss\_weight: 1.0\` \`loss.iou\_loss\_weight: 1.0\` | \[x\] Script Created | 2025-12-12 |
| **3.3.3** | **Freeze Backbone** | Set `model.backbone.freeze: True`. This limits gradients to the Mask Decoder and Presence Head, saving VRAM and training time. | \[x\] Script Created | 2025-12-12 |

---

Here is the detailed implementation plan for **Phase 4: Model Fine-Tuning (The Training Loop)**.

This phase executes the training process defined in **PRD Chapter 5**, applying the custom configuration to the SAM 3 architecture to adapt the **Presence Head** and **Mask Decoder** to the avian dataset.

### **Phase 4: Model Fine-Tuning (The Training Loop)**

#### **Step 4.1: Initial Training Run (Frozen Backbone)**

**Objective:** Launch the training job. The strategy focuses on updating the "Heads" (Prompt Encoder, Mask Decoder, Presence Head) while keeping the heavy Vision Transformer backbone frozen to preserve general visual knowledge and reduce VRAM load.

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **4.1.1** | **Local Training Launch (Debugging)** | Run a short sanity check (1 epoch) locally to verify data loading: \`python sam3/train/train.py \-c configs/sam3\_chicken\_finetune.yaml \--use-cluster 0 \--num-gpus 1 train.max\_epochs=1\` | \[x\] Script Created | 2025-12-12 |
| **4.1.2** | **Cluster Training Launch (Production)** | Submit the full training job via SLURM/Submitit: \`python sam3/train/train.py \-c configs/sam3\_chicken\_finetune.yaml \--use-cluster 1 \--num-nodes 1 \--num-gpus 4\` | \[ \] Pending |  |
| **4.1.3** | **Batch Size Tuning** | Monitor VRAM usage via `nvidia-smi`. If utilization \< 80%, increase `train.batch_size` in the config. If OOM (Out of Memory) occurs, decrease batch size and enable `train.accumulate_grad_batches=2`. | \[ \] Pending |  |

#### **Step 4.2: Monitoring the Presence Head (Convergence Checks)**

**Objective:** Use **Weights & Biases (WandB)** to monitor specific loss components. Success is defined by the model learning to suppress "Not-Chicken" samples (Presence Loss) while accurately segmenting positive samples (Mask Loss).

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **4.2.1** | **Monitor Focal Loss (Presence)** | Check the `loss_focal` curve in WandB. It should decrease steadily.  \*\*Risk:\*\* If it stays flat, the model is ignoring the "Not-Chicken" samples. Increase \`loss.focal\_loss\_weight\`. | \[ \] Pending |  |
| **4.2.2** | **Monitor Dice/IoU Loss (Masks)** | Check `loss_dice` and `loss_iou`. These should decrease only for positive samples. | \[ \] Pending |  |
| **4.2.3** | **Watch Gradient Norms** | Monitor `grad_norm`. Spikes indicate instability. If observed, lower the Learning Rate (`optimizer.lr`) or increase Warm-up steps. | \[ \] Pending |  |

#### **Step 4.3: Checkpointing & Artifact Management**

**Objective:** Ensure that the best-performing model versions are saved and cataloged, preventing the loss of progress due to overfitting in later epochs.

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **4.3.1** | **Configure Checkpoint Callback** | Ensure Hydra config saves top-k checkpoints based on validation loss: \`checkpoint.monitor: "val\_loss"\` \`checkpoint.save\_top\_k: 3\` | \[ \] Pending |  |
| **4.3.2** | **Register Artifacts** | Upon training completion, tag the best checkpoint (`best.pt`) in the Model Registry (or WandB Artifacts) with the DVC Commit Hash used for training. | \[ \] Pending |  |
| **4.3.3** | **Archive Config** | Save the resolved `config.yaml` alongside the model weights to ensure the experiment is reproducible. | \[ \] Pending |  |

---

Here is the detailed implementation plan for **Phase 5: Quality Assurance & Metric Validation**.

This phase executes the rigorous evaluation protocol defined in **PRD Chapter 8**, ensuring the model has not only learned to segment chickens but, critically, has learned to *stop* segmenting background objects (the "Not-Chicken" class).

### **Phase 5: Quality Assurance & Metric Validation**

#### **Step 5.1: Calculating Classification-Gated F1 (CGF1)**

**Objective:** Run the full evaluation suite on the validation set to generate the primary Key Performance Indicators (KPIs). The **CGF1** metric combines segmentation quality with presence detection accuracy.

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **5.1.1** | **Run Evaluation Script** | Execute evaluation using the fine-tuned checkpoint: \`python sam3/eval/evaluate.py \--config configs/eval\_chicken.yaml \--checkpoint checkpoints/best.pt \--json data/chicken\_val.json\` | \[ \] Pending |  |
| **5.1.2** | **Extract Component Metrics** | Parse the output logs to retrieve: 1\. \*\*pmF1\*\* (Prompt-Mask F1): Mask precision on positive detections. 2\. \*\*IL\_MCC\*\* (Matthews Correlation Coeff): Binary classification accuracy. | \[ \] Pending |  |
| **5.1.3** | **Compute CGF1 Score** | Calculate the final composite score: $$CGF1 \= pmF1 \\times IL\\\_MCC$$ Record this value in the Experiment Tracker (WandB). | \[ \] Pending |  |

#### **Step 5.2: "Hard Negative" Holdout Analysis**

**Objective:** Specifically stress-test the **Presence Head** using a subset of data containing *only* "Not-Chicken" images (e.g., empty barns, ducks, equipment). This verifies the suppression of hallucinations.

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **5.2.1** | **Create Holdout JSON** | Generate `data/chicken_negatives_only.json` containing only image IDs where `annotations` list is empty. | \[ \] Pending |  |
| **5.2.2** | **Run Negative Inference** | Run the model on this subset. The goal is **Zero Detections**. \`python sam3/eval/inference.py \--json data/chicken\_negatives\_only.json \--output\_dir results/negatives/\` | \[ \] Pending |  |
| **5.2.3** | **Analyze Presence Scores** | Calculate the average **Presence Score** ($S\_{presence}$) across all negative images.  \*\*Success Criteria:\*\* Average Score $\< 0.1$. \*\*Failure:\*\* If Score $\> 0.5$, the model is hallucinating; Retraining with higher \`focal\_loss\_weight\` is required. | \[ \] Pending |  |

#### **Step 5.3: Visual Error Analysis & Benchmarking**

**Objective:** Qualitative review of the masks and final Go/No-Go decision based on ROI (Return on Investment) compared to the Zero-Shot baseline established in Phase 3\.

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **5.3.1** | **WandB Visual Inspection** | Review the `Media` panel in Weights & Biases. Look for: 1\. \*\*Bleeding:\*\* Masks spilling into background straw. 2\. \*\*Fragmentation:\*\* One chicken split into multiple masks. 3\. \*\*Ghosting:\*\* Masks appearing on rocks/feeders. | \[ \] Pending |  |
| **5.3.2** | **Baseline Comparison** | Compare Fine-Tuned metrics vs. Zero-Shot Baseline (Step 3.1). \*\*Target:\*\* Significant lift in \*\*IL\_MCC\*\* (indicating better background rejection). | \[ \] Pending |  |
| **5.3.3** | **Model Promotion** | If CGF1 improves by $\>5%$ and "Hard Negative" pass rate is $\>90%$, tag the model version as `production-candidate-v1`. | \[ \] Pending |  |

---

Here is the detailed implementation plan for **Phase 6: The Active Learning Data Engine (MLOps)**.

This phase operationalizes the "Data Engine" concept defined in **PRD Chapter 6**. Instead of treating training as a one-time event, this phase establishes the continuous loop of inferring on new data, finding failures, correcting them, and retraining.

### **Phase 6: The Active Learning Data Engine (MLOps)**

#### **Step 6.1: Inference Pipeline for Hard Example Mining**

**Objective:** Automate the discovery of "Hard Examples" (images where the model is confused) from the unlabeled production data stream, utilizing the model's own uncertainty as a filter.

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **6.1.1** | **Unlabeled Data Ingestion** | Script `mine_hard_examples.py`: Load a batch of \~1,000 raw, unlabeled images from the "Inbox" folder. | \[ \] Pending |  |
| **6.1.2** | **Uncertainty Filtering Logic** | Run inference. Flag images where: 1\. \*\*Presence Score ($S\_{presence}$)\*\* is between \*\*0.4 and 0.6\*\* (Ambiguous detection). 2\. \*\*IoU Score\*\* is low (Mask quality is poor). | \[ \] Pending |  |
| **6.1.3** | **Export for Annotation** | Copy flagged images to a `to_annotate/` directory. Generate a pre-filled LabelMe JSON with the model's (imperfect) predictions to serve as a starting point for humans. | \[ \] Pending |  |

#### **Step 6.2: Human-in-the-Loop (HITL) Correction Workflow**

**Objective:** Efficiently convert "Hard Examples" into high-value training data using human expertise.

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **6.2.1** | **Annotation Setup** | Annotators open the flagged images in LabelMe/CVAT. | \[ \] Pending |  |
| **6.2.2** | **Correction Protocol** |  1\. \*\*False Positives:\*\* Delete masks where the model detected a rock/shadow as a chicken. 2\. \*\*False Negatives:\*\* Add masks for chickens the model missed. 3\. \*\*Refinement:\*\* Fix "sloppy" boundaries on existing masks. | \[ \] Pending |  |
| **6.2.3** | **Interactive Prompting (Optional)** | *Advanced:* Use a script that allows annotators to click on a missed bird, calling the SAM 3 API to generate the mask instantly, rather than drawing it manually. | \[ \] Pending |  |

#### **Step 6.3: Dataset Versioning & Retraining Cycle**

**Objective:** Merge the new "Hard Positives/Negatives" into the training set in a controlled, reproducible manner using DVC.

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **6.3.1** | **Merge & Convert** | Run `etl_processor.py` (Step 2.2) on the new annotations. Append the output to `chicken_train.json`. | \[ \] Pending |  |
| **6.3.2** | **Version Control Update** | Commit the expanded dataset: \`dvc add data/images\` \`git commit \-m "Add batch 2 hard examples (v1.1)"\` \`git tag v1.1\` | \[ \] Pending |  |
| **6.3.3** | **Launch Retraining** | Execute the training loop (Phase 4\) using the new dataset version `v1.1`. Compare the new CGF1 score against `v1.0`. | \[ \] Pending |  |

---

Here is the detailed implementation plan for **Phase 7: Export, Optimization & Deployment**.

This final phase translates the research artifact (the fine-tuned PyTorch model) into a high-performance production asset, optimized for edge deployment and integrated into the broader computer vision pipeline as defined in **PRD Chapter 9**.

### **Phase 7: Export, Optimization & Deployment**

#### **Step 7.1: ONNX Export (Decoupled Architecture)**

**Objective:** Convert the PyTorch checkpoint into the interoperable ONNX format. Due to SAM 3's architecture, this requires exporting the **Perception Encoder** (Backbone) and the **Prompt Encoder / Mask Decoder** (Heads) as separate files to enable flexible inference strategies (e.g., caching the backbone).

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **7.1.1** | **Export Perception Encoder** | Export the heavy ViT backbone. Input: Image tensor ($1 \\times 3 \\times 1024 \\times 1024$). Output: Image Embeddings. \`python sam3/export/export\_onnx.py \--checkpoint checkpoints/best.pt \--component encoder \--output artifacts/sam3\_encoder.onnx\` | \[ \] Pending |  |
| **7.1.2** | **Export Decoder/Heads** | Export the lightweight heads. Inputs: Image Embeddings \+ Prompts. Output: Masks \+ Presence Score. \*\*Critical:\*\* Define dynamic axes for the prompt input to allow variable numbers of points/boxes. \`python sam3/export/export\_onnx.py \--component decoder \--output artifacts/sam3\_decoder.onnx\` | \[ \] Pending |  |
| **7.1.3** | **Verify ONNX Outputs** | Run a sanity check using `onnxruntime` to ensure the exported models produce identical outputs (within tolerance) to the PyTorch original. | \[ \] Pending |  |

#### **Step 7.2: TensorRT Optimization (FP16)**

**Objective:** Compile the ONNX models into **NVIDIA TensorRT Engines** (`.engine`) to maximize throughput on A100 (Cloud) or Jetson (Edge) hardware.

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **7.2.1** | **Compile Encoder Engine** | Use `trtexec` to build the engine with FP16 precision (mandatory for memory/speed). \`trtexec \--onnx=artifacts/sam3\_encoder.onnx \--saveEngine=artifacts/sam3\_encoder\_fp16.engine \--fp16\` | \[ \] Pending |  |
| **7.2.2** | **Compile Decoder Engine** | Compile the decoder. Note: If the decoder is very small, FP16 might offer negligible gains over FP32, but consistent precision is recommended. \`trtexec \--onnx=artifacts/sam3\_decoder.onnx \--saveEngine=artifacts/sam3\_decoder\_fp16.engine \--fp16\` | \[ \] Pending |  |
| **7.2.3** | **Benchmark Performance** | Measure FPS. Target: **\>15 FPS** end-to-end. \`python scripts/benchmark\_trt.py \--encoder artifacts/sam3\_encoder\_fp16.engine \--decoder artifacts/sam3\_decoder\_fp16.engine\` | \[ \] Pending |  |

#### **Step 7.3: Deployment Wrapper for Ultralytics Integration**

**Objective:** Create a Python wrapper class that allows the operational team to use the model within their existing workflows, abstracting away the complexity of the decoupled architecture and the text prompt injection.

| Task ID | Task Description | Technical Details / Commands | Status | Implementation Date |
| :---- | :---- | :---- | :---- | :---- |
| **7.3.1** | **Develop `SAM3Wrapper` Class** | Create `inference/sam3_wrapper.py`. \*\*Methods:\*\* \`\_\_init\_\_\`: Loads TRT engines. \`predict(image)\`: 1\. Preprocess image. 2\. Run Encoder Engine. 3\. Inject hardcoded prompt "chicken" into Decoder inputs. 4\. Run Decoder Engine. 5\. Apply Presence Score logic ($S\_{presence} \< Threshold \\to$ Return Empty). | \[ \] Pending |  |
| **7.3.2** | **Integrate with Video Stream** | Create a `run_stream.py` script that connects to an RTSP URL, grabs frames, passes them to `SAM3Wrapper`, and overlays the resulting masks for visualization. | \[ \] Pending |  |
| **7.3.3** | **Backbone Caching Logic (Edge)** | *Optimization:* Modify `run_stream.py` to run the Encoder Engine only once every $N$ frames (e.g., 1Hz) to detect new objects, while running the lightweight Tracker/Decoder at full FPS to update positions. | \[ \] Pending |  |

---

**End of Implementation Plan.**

