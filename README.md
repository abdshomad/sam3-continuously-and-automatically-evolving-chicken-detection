# SAM3 Continuously and Automatically Evolving Chicken Detection

A machine learning project for fine-tuning Meta's SAM 3 (Segment Anything Model 3) to detect and segment chickens in agricultural settings, with an active learning data engine for continuous model improvement.

## Project Overview

This project implements a complete pipeline for:
- Fine-tuning SAM 3 on chicken detection datasets
- Active learning workflows for continuous model improvement
- MLOps integration with Weights & Biases and DVC
- Production deployment with ONNX and TensorRT optimization

## Project Structure

```
.
├── AGENTS.md              # Automated task execution instructions
├── docs/
│   ├── plan/
│   │   └── plan.md       # Implementation plan with tasks
│   └── prd/
│       └── prd.md        # Product Requirements Document
├── sam3/                  # SAM 3 repository (git submodule)
├── scripts/               # Task execution scripts
└── README.md
```

**Note**: The `sam3/` directory is a git submodule pointing to the official Meta Research SAM 3 repository. See [Setup](#setup) section for initialization instructions.

## Setup

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd sam3-continuously-and-automatically-evolving-chicken-detection
   ```

2. **Initialize git submodules**:
   ```bash
   git submodule update --init --recursive
   ```
   
   This will clone the SAM 3 repository as a submodule in the `sam3/` directory.

3. **Create and activate virtual environment using uv**:
   ```bash
   # Create virtual environment
   uv venv --python 3.10
   
   # Activate the environment
   source .venv/bin/activate  # On Linux/Mac
   # or
   source .venv/Scripts/activate  # On Windows
   ```

4. **Install dependencies**:
   ```bash
   # Install project dependencies from pyproject.toml
   uv pip install -e .
   
   # Install PyTorch with CUDA support (adjust CUDA version as needed)
   uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   
   # Install SAM 3 in editable mode from submodule
   uv pip install -e sam3/
   
   # Install other dependencies
   uv pip install hydra-core submitit wandb dvc
   ```

### Git Submodule Strategy

This project uses **git submodules** to include the official Meta Research SAM 3 repository. This approach provides:

- **Proper version control**: The submodule is tracked at a specific commit, ensuring reproducibility
- **Easy updates**: Update to latest version with `git submodule update --remote sam3`
- **Clean separation**: Keeps the main project and SAM 3 codebase separate
- **Flexibility**: Can make local modifications to SAM 3 if needed

**Important**: When cloning this repository, always run `git submodule update --init --recursive` to initialize the SAM 3 submodule.

**Updating the submodule**:
```bash
# Update to latest commit from upstream
git submodule update --remote sam3

# Commit the submodule update
git add sam3
git commit -m "Update sam3 submodule to latest version"
```

## Quick Start

### Automated Task Execution

This project includes an automated workflow for executing tasks from the implementation plan. When you type **"next"** or **"n"** in the chat, the agent will:

1. Read the next 3 pending tasks from `docs/plan/plan.md`
2. Execute each task sequentially
3. Update task status to `[x] Script Created` with implementation date
4. Commit and push changes automatically

See [AGENTS.md](AGENTS.md) for detailed instructions on the automated workflow.

### Manual Execution

To work through tasks manually, refer to the detailed implementation plan in [docs/plan/plan.md](docs/plan/plan.md).

## Documentation

- **[Product Requirements Document](docs/prd/prd.md)**: Complete project specifications and requirements
- **[Implementation Plan](docs/plan/plan.md)**: Detailed task breakdown organized by phases
- **[Agent Instructions](AGENTS.md)**: Automated task execution workflow

## Implementation Phases

1. **Phase 1**: Environment Setup & Infrastructure Initialization
2. **Phase 2**: Data Engineering (ETL) & Schema Transformation
3. **Phase 3**: Baseline Evaluation & Configuration Strategy
4. **Phase 4**: Model Fine-Tuning (The Training Loop)
5. **Phase 5**: Quality Assurance & Metric Validation
6. **Phase 6**: The Active Learning Data Engine (MLOps)
7. **Phase 7**: Export, Optimization & Deployment

## Key Features

- **SAM 3 Fine-tuning**: Custom training pipeline for chicken detection
- **Negative Mining**: Hard negative examples to reduce false positives
- **Active Learning**: Continuous improvement through hard example mining
- **MLOps Integration**: WandB for experiment tracking, DVC for data versioning
- **Production Ready**: ONNX export and TensorRT optimization

## Requirements

- NVIDIA GPU with CUDA support (A100/H100 or RTX 3090/4090 recommended)
- Python 3.10+
- PyTorch 2.x with CUDA 11.8 or 12.1
- See [docs/plan/plan.md](docs/plan/plan.md) for complete setup instructions

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]
