#!/usr/bin/env -S uv run python
"""
Task ID: 3.2.1
Description: Create Experiment Config
Created: 2025-01-15

Note: This script should be executed using 'uv run python script.py' to ensure
the virtual environment is used. Dependencies should be declared in pyproject.toml
and installed via 'uv sync' before running this script.
"""

import sys
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Get project root directory
project_root = Path(__file__).parent.parent

# Add project root to Python path to import config
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Import configuration from config.py
try:
    import config
except ImportError:
    print("Error: config.py not found. Please create config.py with required settings.", file=sys.stderr)
    sys.exit(1)


def load_example_config(example_path):
    """Load the example config file for reference."""
    try:
        with open(example_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"WARNING: Could not load example config: {e}", file=sys.stderr)
        return None


def create_chicken_finetune_config(output_path):
    """Create the SAM3 chicken fine-tuning configuration file."""
    
    # Configuration structure based on roboflow example but adapted for chicken dataset
    config_content = {
        '_package': '_global_',
        'defaults': [
            '_self_'
        ],
        
        # Paths Configuration
        'paths': {
            'dataset_root': '${project_root}/data',
            'experiment_log_dir': '${project_root}/results/chicken_finetune',
            'bpe_path': '${project_root}/sam3/sam3/assets/bpe_simple_vocab_16e6.txt.gz',
            'checkpoint_path': '${project_root}/checkpoints/sam3_vit_h.pt'
        },
        
        # Dataset Configuration
        'chicken_dataset': {
            # Dataset paths will be set in task 3.2.2
            'train_json': 'data/chicken_train.json',  # Placeholder - will be updated in task 3.2.2
            'val_json': 'data/chicken_val.json',      # Placeholder - will be updated in task 3.2.2
            'img_dir': 'data/images',                 # Placeholder - will be updated in task 3.2.2
            
            # Training transforms pipeline
            'train_transforms': [
                {
                    '_target_': 'sam3.train.transforms.basic_for_api.ComposeAPI',
                    'transforms': [
                        {
                            '_target_': 'sam3.train.transforms.filter_query_transforms.FlexibleFilterFindGetQueries',
                            'query_filter': {
                                '_target_': 'sam3.train.transforms.filter_query_transforms.FilterCrowds'
                            }
                        },
                        {
                            '_target_': 'sam3.train.transforms.point_sampling.RandomizeInputBbox',
                            'box_noise_std': 0.1,
                            'box_noise_max': 20
                        },
                        {
                            '_target_': 'sam3.train.transforms.segmentation.DecodeRle'
                        },
                        {
                            '_target_': 'sam3.train.transforms.basic_for_api.RandomResizeAPI',
                            'sizes': {
                                '_target_': 'sam3.train.transforms.basic.get_random_resize_scales',
                                'size': '${scratch.resolution}',
                                'min_size': 480,
                                'rounded': False
                            },
                            'max_size': {
                                '_target_': 'sam3.train.transforms.basic.get_random_resize_max_size',
                                'size': '${scratch.resolution}'
                            },
                            'square': True,
                            'consistent_transform': '${scratch.consistent_transform}'
                        },
                        {
                            '_target_': 'sam3.train.transforms.basic_for_api.PadToSizeAPI',
                            'size': '${scratch.resolution}',
                            'consistent_transform': '${scratch.consistent_transform}'
                        },
                        {
                            '_target_': 'sam3.train.transforms.basic_for_api.ToTensorAPI'
                        },
                        {
                            '_target_': 'sam3.train.transforms.filter_query_transforms.FlexibleFilterFindGetQueries',
                            'query_filter': {
                                '_target_': 'sam3.train.transforms.filter_query_transforms.FilterEmptyTargets'
                            }
                        },
                        {
                            '_target_': 'sam3.train.transforms.basic_for_api.NormalizeAPI',
                            'mean': '${scratch.train_norm_mean}',
                            'std': '${scratch.train_norm_std}'
                        },
                        {
                            '_target_': 'sam3.train.transforms.filter_query_transforms.FlexibleFilterFindGetQueries',
                            'query_filter': {
                                '_target_': 'sam3.train.transforms.filter_query_transforms.FilterEmptyTargets'
                            }
                        }
                    ]
                },
                {
                    '_target_': 'sam3.train.transforms.filter_query_transforms.FlexibleFilterFindGetQueries',
                    'query_filter': {
                        '_target_': 'sam3.train.transforms.filter_query_transforms.FilterFindQueriesWithTooManyOut',
                        'max_num_objects': '${scratch.max_ann_per_img}'
                    }
                }
            ],
            
            # Validation transforms pipeline
            'val_transforms': [
                {
                    '_target_': 'sam3.train.transforms.basic_for_api.ComposeAPI',
                    'transforms': [
                        {
                            '_target_': 'sam3.train.transforms.basic_for_api.RandomResizeAPI',
                            'sizes': '${scratch.resolution}',
                            'max_size': {
                                '_target_': 'sam3.train.transforms.basic.get_random_resize_max_size',
                                'size': '${scratch.resolution}'
                            },
                            'square': True,
                            'consistent_transform': False
                        },
                        {
                            '_target_': 'sam3.train.transforms.basic_for_api.ToTensorAPI'
                        },
                        {
                            '_target_': 'sam3.train.transforms.basic_for_api.NormalizeAPI',
                            'mean': '${scratch.train_norm_mean}',
                            'std': '${scratch.train_norm_std}'
                        }
                    ]
                }
            ],
            
            # Loss configuration (will be refined in task 3.3.2)
            'loss': {
                '_target_': 'sam3.train.loss.sam3_loss.Sam3LossWrapper',
                'matcher': '${scratch.matcher}',
                'o2m_weight': 2.0,
                'o2m_matcher': {
                    '_target_': 'sam3.train.matcher.BinaryOneToManyMatcher',
                    'alpha': 0.3,
                    'threshold': 0.4,
                    'topk': 4
                },
                'use_o2m_matcher_on_o2m_aux': False,
                'loss_fns_find': [
                    {
                        '_target_': 'sam3.train.loss.loss_fns.Boxes',
                        'weight_dict': {
                            'loss_bbox': 5.0,
                            'loss_giou': 2.0
                        }
                    },
                    {
                        '_target_': 'sam3.train.loss.loss_fns.IABCEMdetr',
                        'weak_loss': False,
                        'weight_dict': {
                            'loss_ce': 20.0,
                            'presence_loss': 20.0  # Will be boosted to 5.0 in task 3.3.2 (focal_loss_weight)
                        },
                        'pos_weight': 10.0,
                        'alpha': 0.25,
                        'gamma': 2,
                        'use_presence': True,
                        'pos_focal': False,
                        'pad_n_queries': 200,
                        'pad_scale_pos': 1.0
                    },
                    {
                        '_target_': 'sam3.train.loss.loss_fns.Masks',
                        'focal_alpha': 0.25,
                        'focal_gamma': 2.0,
                        'weight_dict': {
                            'loss_mask': 200.0,
                            'loss_dice': 10.0,
                            'loss_iou': 1.0  # Will be refined in task 3.3.2
                        },
                        'compute_aux': False
                    }
                ],
                'loss_fn_semantic_seg': None,
                'scale_by_find_batch_size': '${scratch.scale_by_find_batch_size}'
            }
        },
        
        # Helper parameters (scratch)
        'scratch': {
            'enable_segmentation': True,  # Using segmentation masks
            'd_model': 256,
            'pos_embed': {
                '_target_': 'sam3.model.position_encoding.PositionEmbeddingSine',
                'num_pos_feats': '${scratch.d_model}',
                'normalize': True,
                'scale': None,
                'temperature': 10000
            },
            
            # Box processing
            'use_presence_eval': True,
            'original_box_postprocessor': {
                '_target_': 'sam3.eval.postprocessors.PostProcessImage',
                'max_dets_per_img': -1,
                'use_original_ids': True,
                'use_original_sizes_box': True,
                'use_presence': '${scratch.use_presence_eval}'
            },
            
            # Matcher configuration
            'matcher': {
                '_target_': 'sam3.train.matcher.BinaryHungarianMatcherV2',
                'focal': True,
                'cost_class': 2.0,
                'cost_bbox': 5.0,
                'cost_giou': 2.0,
                'alpha': 0.25,
                'gamma': 2,
                'stable': False
            },
            'scale_by_find_batch_size': True,
            
            # Image processing parameters
            'resolution': 1024,  # Standard SAM3 resolution
            'consistent_transform': False,
            'max_ann_per_img': 200,
            
            # Normalization parameters
            'train_norm_mean': [0.5, 0.5, 0.5],
            'train_norm_std': [0.5, 0.5, 0.5],
            'val_norm_mean': [0.5, 0.5, 0.5],
            'val_norm_std': [0.5, 0.5, 0.5],
            
            # Training parameters
            'num_train_workers': 4,
            'num_val_workers': 2,
            'max_data_epochs': 20,
            'target_epoch_size': 1500,
            'hybrid_repeats': 1,
            'context_length': 2,
            'gather_pred_via_filesys': False,
            
            # Learning rate and scheduler parameters
            'lr_scale': 0.1,
            'lr_transformer': '${times:8e-4,${scratch.lr_scale}}',
            'lr_vision_backbone': '${times:2.5e-4,${scratch.lr_scale}}',
            'lr_language_backbone': '${times:5e-5,${scratch.lr_scale}}',
            'lrd_vision_backbone': 0.9,
            'wd': 0.1,
            'scheduler_timescale': 20,
            'scheduler_warmup': 20,  # Warm-up for 20% of training
            'scheduler_cooldown': 20,
            
            'val_batch_size': 1,
            'collate_fn_val': {
                '_target_': 'sam3.train.data.collator.collate_fn_api',
                '_partial_': True,
                'repeats': '${scratch.hybrid_repeats}',
                'dict_key': 'chicken',
                'with_seg_masks': '${scratch.enable_segmentation}'
            },
            
            'gradient_accumulation_steps': 1,
            'train_batch_size': 4,  # Will be tuned in task 4.1.3
            'collate_fn': {
                '_target_': 'sam3.train.data.collator.collate_fn_api',
                '_partial_': True,
                'repeats': '${scratch.hybrid_repeats}',
                'dict_key': 'all',
                'with_seg_masks': '${scratch.enable_segmentation}'
            }
        },
        
        # Trainer Configuration
        'trainer': {
            '_target_': 'sam3.train.trainer.Trainer',
            'skip_saving_ckpts': False,
            'empty_gpu_mem_cache_after_eval': True,
            'skip_first_val': True,
            'max_epochs': 20,
            'accelerator': 'cuda',
            'seed_value': 123,
            'val_epoch_freq': 1,  # Validate every epoch
            'mode': 'train',
            'gradient_accumulation_steps': '${scratch.gradient_accumulation_steps}',
            
            'distributed': {
                'backend': 'nccl',
                'find_unused_parameters': True,
                'gradient_as_bucket_view': True
            },
            
            'loss': {
                'all': '${chicken_dataset.loss}',
                'default': {
                    '_target_': 'sam3.train.loss.sam3_loss.DummyLoss'
                }
            },
            
            'data': {
                'train': {
                    '_target_': 'sam3.train.data.torch_dataset.TorchDataset',
                    'dataset': {
                        '_target_': 'sam3.train.data.sam3_image_dataset.Sam3ImageDataset',
                        'transforms': '${chicken_dataset.train_transforms}',
                        'load_segmentation': '${scratch.enable_segmentation}',
                        'max_ann_per_img': 500000,
                        'multiplier': 1,
                        'max_train_queries': 50000,
                        'max_val_queries': 50000,
                        'training': True,
                        'use_caching': False,
                        'use_text_prompts': True,  # Enable text prompts (PCS)
                        'prompt_column': 'text_input',  # Column name for text prompts
                        'img_folder': '${chicken_dataset.img_dir}',
                        'ann_file': '${chicken_dataset.train_json}'
                    },
                    'shuffle': True,
                    'batch_size': '${scratch.train_batch_size}',
                    'num_workers': '${scratch.num_train_workers}',
                    'pin_memory': True,
                    'drop_last': True,
                    'collate_fn': '${scratch.collate_fn}'
                },
                'val': {
                    '_target_': 'sam3.train.data.torch_dataset.TorchDataset',
                    'dataset': {
                        '_target_': 'sam3.train.data.sam3_image_dataset.Sam3ImageDataset',
                        'load_segmentation': '${scratch.enable_segmentation}',
                        'coco_json_loader': {
                            '_target_': 'sam3.train.data.coco_json_loaders.COCO_FROM_JSON',
                            'include_negatives': True,
                            'category_chunk_size': 2,
                            '_partial_': True
                        },
                        'img_folder': '${chicken_dataset.img_dir}',
                        'ann_file': '${chicken_dataset.val_json}',
                        'transforms': '${chicken_dataset.val_transforms}',
                        'max_ann_per_img': 100000,
                        'multiplier': 1,
                        'training': False,
                        'use_text_prompts': True,  # Enable text prompts
                        'prompt_column': 'text_input'  # Column name for text prompts
                    },
                    'shuffle': False,
                    'batch_size': '${scratch.val_batch_size}',
                    'num_workers': '${scratch.num_val_workers}',
                    'pin_memory': True,
                    'drop_last': False,
                    'collate_fn': '${scratch.collate_fn_val}'
                }
            },
            
            'model': {
                '_target_': 'sam3.model_builder.build_sam3_image_model',
                'bpe_path': '${paths.bpe_path}',
                'device': 'cpus',
                'eval_mode': False,
                'enable_segmentation': '${scratch.enable_segmentation}',
                'checkpoint_path': '${paths.checkpoint_path}',
                # Backbone freeze will be set in task 3.3.3
                # 'backbone': {
                #     'freeze': True
                # }
            },
            
            'meters': {
                'val': {
                    'chicken': {
                        'cgf1': {
                            '_target_': 'sam3.eval.coco_writer.PredictionDumper',
                            'iou_type': 'segm',
                            'dump_dir': '${launcher.experiment_log_dir}/dumps/chicken_val',
                            'merge_predictions': True,
                            'postprocessor': '${scratch.original_box_postprocessor}',
                            'gather_pred_via_filesys': '${scratch.gather_pred_via_filesys}',
                            'maxdets': 1000000,
                            'pred_file_evaluators': [
                                {
                                    '_target_': 'sam3.eval.cgf1_eval.CGF1Evaluator',
                                    'gt_path': '${chicken_dataset.val_json}',
                                    'iou_type': 'segm'
                                }
                            ]
                        }
                    }
                }
            },
            
            'optim': {
                'amp': {
                    'enabled': True,
                    'amp_dtype': 'bfloat16'  # Will be set based on GPU in task 3.2.4
                },
                'optimizer': {
                    '_target_': 'torch.optim.AdamW'
                },
                'gradient_clip': {
                    '_target_': 'sam3.train.optim.optimizer.GradientClipper',
                    'max_norm': 0.1,
                    'norm_type': 2
                },
                'param_group_modifiers': [
                    {
                        '_target_': 'sam3.train.optim.optimizer.layer_decay_param_modifier',
                        '_partial_': True,
                        'layer_decay_value': '${scratch.lrd_vision_backbone}',
                        'apply_to': 'backbone.vision_backbone.trunk',
                        'overrides': [
                            {
                                'pattern': '*pos_embed*',
                                'value': 1.0
                            }
                        ]
                    }
                ],
                'options': {
                    'lr': [
                        {
                            'scheduler': {
                                '_target_': 'sam3.train.optim.schedulers.InverseSquareRootParamScheduler',
                                'base_lr': '${scratch.lr_transformer}',
                                'timescale': '${scratch.scheduler_timescale}',
                                'warmup_steps': '${scratch.scheduler_warmup}',
                                'cooldown_steps': '${scratch.scheduler_cooldown}'
                            }
                        },
                        {
                            'scheduler': {
                                '_target_': 'sam3.train.optim.schedulers.InverseSquareRootParamScheduler',
                                'base_lr': '${scratch.lr_vision_backbone}',
                                'timescale': '${scratch.scheduler_timescale}',
                                'warmup_steps': '${scratch.scheduler_warmup}',
                                'cooldown_steps': '${scratch.scheduler_cooldown}'
                            },
                            'param_names': [
                                'backbone.vision_backbone.*'
                            ]
                        },
                        {
                            'scheduler': {
                                '_target_': 'sam3.train.optim.schedulers.InverseSquareRootParamScheduler',
                                'base_lr': '${scratch.lr_language_backbone}',
                                'timescale': '${scratch.scheduler_timescale}',
                                'warmup_steps': '${scratch.scheduler_warmup}',
                                'cooldown_steps': '${scratch.scheduler_cooldown}'
                            },
                            'param_names': [
                                'backbone.language_backbone.*'
                            ]
                        }
                    ],
                    'weight_decay': [
                        {
                            'scheduler': {
                                '_target_': 'fvcore.common.param_scheduler.ConstantParamScheduler',
                                'value': '${scratch.wd}'
                            }
                        },
                        {
                            'scheduler': {
                                '_target_': 'fvcore.common.param_scheduler.ConstantParamScheduler',
                                'value': 0.0
                            },
                            'param_names': [
                                '*bias*'
                            ],
                            'module_cls_names': [
                                'torch.nn.LayerNorm'
                            ]
                        }
                    ]
                }
            },
            
            'checkpoint': {
                'save_dir': '${launcher.experiment_log_dir}/checkpoints',
                'save_freq': 0,  # Only save last checkpoint
                'monitor': 'val_loss',  # Will be configured in task 4.3.1
                'save_top_k': 3  # Will be configured in task 4.3.1
            },
            
            'logging': {
                'tensorboard_writer': {
                    '_target_': 'sam3.train.utils.logger.make_tensorboard_logger',
                    'log_dir': '${launcher.experiment_log_dir}/tensorboard',
                    'flush_secs': 120,
                    'should_log': True
                },
                'wandb_writer': None,  # Will be configured if WandB is enabled
                'log_dir': '${launcher.experiment_log_dir}/logs',
                'log_freq': 10
            }
        },
        
        # Launcher Configuration
        'launcher': {
            'num_nodes': 1,
            'gpus_per_node': 1,  # Will be configured for cluster in task 4.1.2
            'experiment_log_dir': '${paths.experiment_log_dir}',
            'multiprocessing_context': 'forkserver'
        },
        
        # Submitit Configuration (for cluster execution)
        'submitit': {
            'account': None,
            'partition': None,
            'qos': None,
            'timeout_hour': 72,
            'use_cluster': False,  # Set to True for cluster execution
            'cpus_per_task': 10,
            'port_range': [10000, 65000],
            'constraint': None
        }
    }
    
    # Write YAML file - use yaml.dump which handles the structure correctly
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Use yaml.dump for proper YAML formatting
    yaml_str = yaml.dump(config_content, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000)
    
    # Fix the package header - replace the _package key with comment
    yaml_str = "# @package _global_\ndefaults:\n  - _self_\n\n" + yaml_str.replace("'_package': _global_\n", "").replace('_package: _global_\n', '')
    
    # Write to file
    with open(output_path, 'w') as f:
        f.write(yaml_str)
    
    return True


def main():
    """Create the SAM3 chicken fine-tuning experiment configuration file."""
    print("=" * 70)
    print("Task 3.2.1: Create Experiment Config")
    print("=" * 70)
    print()
    
    # Set paths
    example_config_path = project_root / "sam3" / "sam3" / "train" / "configs" / "roboflow_v100" / "roboflow_v100_full_ft_100_images.yaml"
    output_config_path = project_root / "configs" / "sam3_chicken_finetune.yaml"
    
    # Check if example config exists (for reference)
    if example_config_path.exists():
        print(f"Reading example config from: {example_config_path}")
        example_config = load_example_config(example_config_path)
        if example_config:
            print("✓ Loaded example config for reference")
        print()
    
    # Create the new config file
    print(f"Creating configuration file: {output_config_path}")
    
    try:
        success = create_chicken_finetune_config(output_config_path)
        if success:
            print(f"✓ Configuration file created successfully")
            print()
            print("Note: Dataset paths (train_json, val_json, img_dir) are placeholders.")
            print("      They will be properly set in task 3.2.2.")
            print()
            print("Next steps:")
            print("  - Task 3.2.2: Update dataset paths in this config file")
            print("  - Task 3.2.3: Set prompt mode configuration")
            print("  - Task 3.2.4: Configure hardware optimization settings")
            print("  - Task 3.3.1: Configure learning rate schedule")
            print("  - Task 3.3.2: Engineer loss weights (especially focal_loss_weight)")
            print("  - Task 3.3.3: Freeze backbone")
            return 0
        else:
            print("ERROR: Failed to create configuration file", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"ERROR: Failed to create configuration file: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
