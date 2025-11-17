# AISentinel - Machine Learning Pipeline

Comprehensive guide to the custom TensorFlow sentiment analysis model.

## Overview

This project implements a production-ready sentiment analysis pipeline using:
- **Custom TensorFlow/Keras models** (LSTM + Attention, Transformers)
- **Multi-source training data** (SST-2, IMDB, synthetic AI tool reviews)
- **Comprehensive evaluation** (accuracy, precision, recall, F1-score)
- **Model versioning and checkpointing**
- **Real-time inference** via the AdvancedSentimentAnalyzer

## Architecture

### Model Options

1. **LSTM with Attention** (Recommended)
   - Bidirectional LSTM layers for sequence modeling
   - Custom attention mechanism to focus on important words
   - Dropout and regularization for robustness
   - ~500K parameters

2. **Transformer-based**
   - Multi-head self-attention
   - Positional encoding
   - Feed-forward networks
   - ~300K parameters

### Model Architecture (LSTM)

```
Input (128 tokens)
    ↓
Embedding Layer (vocab_size → 128d)
    ↓
Spatial Dropout (0.25)
    ↓
Bidirectional LSTM (64 units) + Return Sequences
    ↓
Bidirectional LSTM (32 units) + Return Sequences
    ↓
Attention Layer (Custom)
    ↓
Dense (64, ReLU) + Dropout (0.5)
    ↓
Dense (32, ReLU) + Dropout (0.25)
    ↓
Dense (3, Softmax) → [negative, neutral, positive]
```

## Quick Start

### 1. Prepare Training Data

```bash
python src/data_collection/prepare_training_data.py
```

This downloads and preprocesses:
- Stanford Sentiment Treebank (SST-2): 67K+ samples
- IMDB Movie Reviews: 15K samples (subset)
- Synthetic AI tool reviews: 800 samples

**Output**: `data/processed/train.csv`, `val.csv`, `test.csv`

### 2. Train Model

```bash
python scripts/train_sentiment_model.py
```

Or using the dedicated training script:

```bash
python src/ml/train_model.py
```

**Training Configuration**:
- Epochs: 20 (with early stopping)
- Batch size: 32
- Optimizer: Adam (lr=0.001)
- Loss: Sparse categorical crossentropy
- Metrics: Accuracy, Precision, Recall

**Output**:
- Trained model: `models/run_YYYYMMDD_HHMMSS/sentiment_model.keras`
- Tokenizer: `models/run_YYYYMMDD_HHMMSS/tokenizer.pkl`
- Metrics: `models/run_YYYYMMDD_HHMMSS/metrics.json`
- Visualizations: `training_history.png`, `confusion_matrix.png`

### 3. Test Model

```bash
python scripts/test_model.py
```

Tests the latest trained model on sample AI tool reviews.

### 4. Explore with Jupyter

```bash
jupyter notebook notebooks/model_evaluation.ipynb
```

Interactive notebook with:
- Data exploration
- Model training
- Comprehensive evaluation
- Visualization

## Data Pipeline

### Data Sources

| Source | Samples | Domain | Labels |
|--------|---------|--------|--------|
| SST-2 | ~67K | General sentiment | Positive, Negative |
| IMDB | ~15K | Movie reviews | Positive, Negative |
| Synthetic | ~800 | AI tool reviews | Positive, Neutral, Negative |

### Data Preprocessing

1. **Text Cleaning**:
   - Remove URLs, mentions, hashtags
   - Normalize whitespace
   - Filter special characters

2. **Tokenization**:
   - Vocabulary size: 10,000 tokens
   - OOV token for unknown words
   - Sequence length: 128 tokens (padded/truncated)

3. **Label Encoding**:
   - `0`: Negative
   - `1`: Neutral
   - `2`: Positive

4. **Data Splitting**:
   - Train: 70%
   - Validation: 10%
   - Test: 20%

## Model Training

### Training Pipeline

```python
from src.ml.train_model import SentimentModelTrainer

trainer = SentimentModelTrainer(
    data_dir="data/processed",
    output_dir="models/my_run",
    max_vocab_size=10000,
    max_length=128,
    model_type="lstm",  # or "transformer"
)

# Load and prepare data
train_df, val_df, test_df = trainer.load_data()
tokenizer = trainer.prepare_tokenizer(train_df)
X_train, y_train = trainer.prepare_sequences(train_df)
X_val, y_val = trainer.prepare_sequences(val_df)

# Build and train
model = trainer.build_model()
history = trainer.train(X_train, y_train, X_val, y_val, epochs=20)

# Evaluate
metrics = trainer.evaluate(X_test, y_test)
trainer.save_model()
```

### Callbacks

- **EarlyStopping**: Stops training if validation loss doesn't improve for 5 epochs
- **ModelCheckpoint**: Saves best model based on validation accuracy
- **ReduceLROnPlateau**: Reduces learning rate if validation loss plateaus
- **TensorBoard**: Logs training metrics for visualization

### Hyperparameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Embedding Dim | 128 | Word embedding dimension |
| LSTM Units | 64 | Units per LSTM direction |
| Dropout Rate | 0.5 | Dropout for regularization |
| Learning Rate | 0.001 | Adam optimizer LR |
| Batch Size | 32 | Training batch size |
| Max Length | 128 | Maximum sequence length |

## Model Evaluation

### Metrics

The model is evaluated using:
- **Accuracy**: Overall correctness
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **F1-Score**: Harmonic mean of precision and recall
- **Confusion Matrix**: Per-class performance

### Expected Performance

Based on validation data:
- **Overall Accuracy**: 85-90%
- **Positive Sentiment**: 88-92% accuracy
- **Negative Sentiment**: 86-90% accuracy
- **Neutral Sentiment**: 70-80% accuracy (more challenging)

### Confusion Matrix Example

```
                Predicted
              Neg  Neu  Pos
Actual  Neg  [850  50  100]
        Neu  [100 700  200]
        Pos  [ 80  70  850]
```

## Inference

### Using the Trained Model

```python
from pathlib import Path
from src.sentiment_analysis.analyzer import AdvancedSentimentAnalyzer

# Initialize with custom model
analyzer = AdvancedSentimentAnalyzer(
    use_custom_model=True,
    custom_model_path=Path("models/run_20241117_120000/sentiment_model.keras"),
    custom_tokenizer_path=Path("models/run_20241117_120000/tokenizer.pkl"),
)

# Single prediction
result = analyzer.analyze("ChatGPT is amazing for coding!")
print(f"Sentiment: {result.label}")
print(f"Confidence: {result.confidence:.3f}")
print(f"Score: {result.score:.3f}")

# Batch prediction
texts = [
    "Claude is great for writing",
    "GitHub Copilot has too many bugs",
    "Midjourney is okay, nothing special"
]
results = analyzer.analyze_batch(texts)
for text, result in zip(texts, results):
    print(f"{text} → {result.label} ({result.confidence:.2f})")
```

### Output Format

```python
AdvancedSentimentResult(
    score=0.92,        # Sentiment score in [-1, 1]
    label="positive",  # "negative", "neutral", or "positive"
    confidence=0.92    # Model confidence [0, 1]
)
```

## Model Versioning

Models are saved with timestamps for version control:

```
models/
├── run_20241117_120000/
│   ├── sentiment_model.keras      # Full model
│   ├── tokenizer.pkl              # Tokenizer
│   ├── metrics.json               # Evaluation metrics
│   ├── config.json                # Training config
│   ├── training_history.png       # Training plots
│   ├── confusion_matrix.png       # Confusion matrix
│   ├── checkpoints/
│   │   └── best_model.keras       # Best checkpoint
│   └── logs/                      # TensorBoard logs
└── run_20241117_140000/
    └── ...
```

## Advanced Features

### Custom Attention Layer

```python
from src.ml.model import AttentionLayer

# Attention mechanism to focus on important words
# Learns weights to emphasize sentiment-bearing tokens
# Improves performance on long sequences
```

### Model Comparison

Train both architectures and compare:

```bash
# Train LSTM
python src/ml/train_model.py --model-type lstm

# Train Transformer
python src/ml/train_model.py --model-type transformer
```

### Transfer Learning

Fine-tune on domain-specific data:

```python
# Load pre-trained model
base_model = keras.models.load_model("models/run_1/sentiment_model.keras")

# Freeze early layers
for layer in base_model.layers[:-3]:
    layer.trainable = False

# Train on AI tool reviews only
trainer.train(X_ai_tools, y_ai_tools, epochs=5)
```

## Troubleshooting

### Common Issues

1. **Out of Memory**:
   - Reduce batch size: `batch_size=16`
   - Reduce vocab size: `max_vocab_size=5000`
   - Reduce sequence length: `max_length=64`

2. **Low Accuracy**:
   - Increase training epochs
   - Add more training data
   - Tune hyperparameters (dropout, learning rate)
   - Try different model architecture

3. **Overfitting**:
   - Increase dropout rate
   - Add more regularization
   - Use early stopping
   - Augment training data

4. **Model Not Loading**:
   ```python
   # If AttentionLayer error, import custom objects
   from src.ml.model import AttentionLayer
   model = keras.models.load_model(
       "path/to/model.keras",
       custom_objects={"AttentionLayer": AttentionLayer}
   )
   ```

## Best Practices

1. **Always split data**: Train/Val/Test to avoid overfitting
2. **Monitor validation metrics**: Not just training metrics
3. **Use callbacks**: Early stopping prevents overfitting
4. **Version models**: Keep track of experiments
5. **Test on real data**: Validate with actual AI tool reviews
6. **Document experiments**: Record configs and results

## Next Steps

1. **Deploy to production**:
   - Convert to TensorFlow Serving format
   - Set up inference API
   - Monitor performance

2. **Continuous improvement**:
   - Collect real user feedback
   - Retrain periodically with new data
   - A/B test model versions

3. **Expand capabilities**:
   - Multi-lingual sentiment
   - Aspect-based sentiment (features, pricing, support)
   - Fine-grained sentiment (1-5 stars)

## References

- [TensorFlow Keras Guide](https://www.tensorflow.org/guide/keras)
- [Attention Mechanisms](https://arxiv.org/abs/1706.03762)
- [Sentiment Analysis with Deep Learning](https://arxiv.org/abs/1801.07883)
- [SST-2 Dataset](https://nlp.stanford.edu/sentiment/)

## Support

For questions or issues:
1. Check the [main README](../README.md)
2. Review the Jupyter notebook examples
3. Open an issue on GitHub
