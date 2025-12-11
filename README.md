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
└── README.md
```

## Quick Start

### Automated Task Execution

This project includes an automated workflow for executing tasks from the implementation plan. When you type **"next"** or **"n"** in the chat, the agent will:

1. Read the next 3 pending tasks from `docs/plan/plan.md`
2. Execute each task sequentially
3. Update task status to `[x] Done` with implementation date
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
