# DERMAVISION AI - ML Skin Condition Detection

## Overview

DermaVision AI implements advanced machine learning-based skin condition detection using Convolutional Neural Networks (CNNs) and multi-label classification. The system can identify and score multiple skin conditions simultaneously from facial images.

## Features

### 🧠 ML-Powered Analysis
- **Multi-label Classification**: Detects 8 skin conditions simultaneously
- **CNN Architecture**: Custom CNN with EfficientNet backbone options
- **Real-time Processing**: Optimized for fast inference on facial images
- **Fallback System**: Traditional CV analysis when ML models unavailable

### 🎯 Detected Conditions
1. **Acne** - Classification and severity scoring
2. **Hyperpigmentation** - Dark spots and uneven skin tone
3. **Dark Circles** - Periorbital hyperpigmentation
4. **Wrinkles** - Fine lines and deep wrinkles
5. **Oiliness** - Sebum production assessment
6. **Large Pores** - Pore size estimation
7. **Dryness** - Skin hydration assessment
8. **Fine Lines** - Micro-wrinkles detection

## Architecture

### ML Pipeline
```
Input Image → Face Detection → ML Analysis → Multi-label Prediction → Condition Scores
```

### Model Architecture
- **Input**: 224x224 RGB facial images
- **Backbone**: EfficientNetB0 (pre-trained on ImageNet)
- **Head**: Custom multi-label classification head
- **Output**: 8 sigmoid-activated scores (0-100%)

### Training Data
The system is designed to work with dermatology datasets such as:
- **HAM10000**: 10,015 dermatoscopic images (7 classes)
- **ISIC Archive**: Various skin lesion datasets
- **Fitzpatrick17k**: Diverse skin tone dataset

## Installation

### Prerequisites
```bash
pip install tensorflow scikit-learn matplotlib pandas seaborn tqdm h5py
```

### Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create basic model for testing:
```bash
cd backend/services
python create_basic_model.py
```

## Usage

### Basic Analysis
```python
from backend.services.skin_analyzer import SkinAnalyzer

analyzer = SkinAnalyzer()
results = analyzer.analyze("path/to/face_image.jpg")

print(results)
# {
#     'acne': 25.3,
#     'hyperpigmentation': 15.7,
#     'dark_circles': 8.2,
#     'wrinkles': 12.1,
#     'oiliness': 45.8,
#     'large_pores': 18.9,
#     'dryness': 22.4,
#     'fine_lines': 9.6,
#     'health_score': 78.5,
#     'status': 'SUCCESS'
# }
```

### Training Custom Models

#### Using HAM10000 Dataset
```bash
# Download HAM10000 dataset and organize as:
# dataset/
# ├── HAM10000_images/
# └── HAM10000_metadata.csv

python backend/services/train_skin_model.py \
    --dataset_path /path/to/ham10000 \
    --model_name efficientnet_b0 \
    --epochs 50 \
    --batch_size 32
```

#### Custom Training Script
```python
from backend.services.train_skin_model import SkinConditionTrainer

trainer = SkinConditionTrainer(model_name="efficientnet_b0")
model, history = trainer.train(
    dataset_path="/path/to/dataset",
    epochs=50,
    batch_size=32
)
```

## Model Training

### Data Preparation
The training system expects datasets in the following format:
- Images in a directory structure
- CSV metadata file with image paths and labels
- Multi-label binary format (0/1) for each condition

### Training Parameters
- **Image Size**: 224x224 pixels
- **Batch Size**: 32 (adjust based on GPU memory)
- **Epochs**: 50-100 (with early stopping)
- **Learning Rate**: 1e-4 with decay
- **Loss**: Binary Crossentropy (multi-label)
- **Metrics**: AUC, Precision, Recall

### Data Augmentation
- Random rotation (±20°)
- Width/height shift (±20%)
- Horizontal flip
- Zoom (±20%)
- Brightness/color jitter

## API Integration

### REST API Endpoints
```python
# Analyze skin conditions
POST /api/analyze
- Content-Type: multipart/form-data
- Body: image file
- Response: {"status": "SUCCESS", "telemetry": {...}, "scan_id": 123}

# Chat with AI dermatologist
POST /api/chat
- Content-Type: application/json
- Body: {"message": "How to treat acne?"}
- Response: {"status": "SUCCESS", "response": "..."}
```

### Frontend Integration
The ML results are automatically integrated with the existing frontend:
- Real-time condition scoring
- Visual progress bars
- Clinical recommendations
- Report generation

## Performance

### Model Metrics (Example)
- **Accuracy**: 87.3%
- **AUC**: 0.91
- **Precision**: 0.84
- **Recall**: 0.79
- **F1-Score**: 0.81

### Inference Speed
- **CPU**: ~200ms per image
- **GPU**: ~50ms per image
- **Batch Processing**: ~20ms per image

## Advanced Features

### Face Detection Integration
- Uses MediaPipe for accurate face cropping
- Focuses analysis on facial regions
- Handles multiple faces in images

### Multi-Modal Analysis
- Combines ML predictions with traditional CV
- Weighted scoring system
- Confidence-based fallbacks

### Clinical Validation
- Designed for dermatologist review
- Provides confidence scores
- Includes uncertainty estimation

## Research & Datasets

### Recommended Datasets
1. **HAM10000** - https://www.kaggle.com/kmader/skin-cancer-mnist-ham10000
2. **ISIC 2019** - https://www.kaggle.com/datasets/salviohexia/isic-2019-skin-lesion-images-for-classification
3. **Fitzpatrick17k** - https://github.com/mattgroh/fitzpatrick17k

### Training Best Practices
- Use stratified sampling for imbalanced classes
- Implement data augmentation extensively
- Monitor for overfitting with validation metrics
- Use early stopping and learning rate scheduling

## Future Enhancements

### Planned Features
- **Vision Transformers**: Replace CNN with ViT for better performance
- **3D Analysis**: Depth estimation for wrinkle analysis
- **Temporal Analysis**: Track condition changes over time
- **Personalized Models**: User-specific fine-tuning
- **Multi-Spectral**: UV/IR imaging integration

### Research Directions
- Self-supervised learning for unlabeled data
- Few-shot learning for rare conditions
- Federated learning for privacy-preserving training
- Explainable AI for clinical decision support

## Troubleshooting

### Common Issues
1. **Model not loading**: Check model file path and TensorFlow version
2. **Memory errors**: Reduce batch size or image resolution
3. **Poor predictions**: Ensure proper face detection and image preprocessing
4. **Training instability**: Adjust learning rate and use gradient clipping

### Performance Optimization
- Use mixed precision training
- Implement model quantization for deployment
- Use ONNX/TensorRT for faster inference
- Optimize preprocessing pipeline

## Contributing

### Development Setup
```bash
# Clone repository
git clone https://github.com/your-repo/dermavision-ai.git
cd dermavision-ai

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest

# Start development server
python backend/app.py
```

### Code Structure
```
backend/services/
├── skin_analyzer.py          # Main analyzer (ML + CV fallback)
├── ml_skin_analyzer.py       # ML-based analysis
├── train_skin_model.py       # Training script
├── create_basic_model.py     # Model creation utility
└── models/                   # Trained models directory
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this work in your research, please cite:

```bibtex
@software{dermavision_ai_2026,
  title={DermaVision AI: ML-Powered Skin Condition Detection},
  author={Your Name},
  year={2026},
  url={https://github.com/your-repo/dermavision-ai}
}
```

## Contact

For questions or collaborations:
- Email: your.email@example.com
- GitHub Issues: https://github.com/your-repo/dermavision-ai/issues
- Documentation: https://your-docs-site.com/dermavision-ai