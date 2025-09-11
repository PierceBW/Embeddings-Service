# app/model_definitions.py
"""PyTorch CNN architectures used to transform SentenceTransformer
embeddings into scalar risk logits.

Classes
-------
EmbeddingCNN
    Treats the 384-dimensional embedding as a 1-D sequence.
EmbeddingCNN2D
    Treats the embedding as a 2-D matrix (e.g., 9×384) to leverage 2-D
    convolutions.
"""
import torch
import torch.nn as nn

class EmbeddingCNN(nn.Module):
    """1-D convolutional network that ingests a 384-dimensional vector
    and outputs a single logit representing predicted risk.
    """
    def __init__(self, in_len: int = 384):
        super().__init__()
        self.features = nn.Sequential(
            # [B,1,384] → [B,32,384]
            nn.Conv1d(1, 32, kernel_size=5, padding=2),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            # [B,32,192]
            nn.MaxPool1d(2),

            # [B,32,192] → [B,64,192]
            nn.Conv1d(32, 64, kernel_size=5, padding=2),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(2),           # → [B,64,96]

            # [B,64,96] → [B,128,96]
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveMaxPool1d(1)    # → [B,128,1]
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),              # [B,128]
            nn.Dropout(0.3),
            nn.Linear(128, 1)          # logit
        )

    def forward(self, x):
        x = x.unsqueeze(1)             # [B,384] → [B,1,384]
        x = self.features(x)
        return self.classifier(x)      # raw logits


class EmbeddingCNN2D(nn.Module):
    """2-D convolutional network variant that expects input shaped as
    `(batch, 1, 9, 384)` and outputs a single risk logit.
    """
    def __init__(self, in_len: int = 384):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=(3, 5), padding=(1, 2)),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d((1, 2)),            # halve only the embed-dim

            nn.Conv2d(32, 64, kernel_size=(3, 5), padding=(1, 2)),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d((1, 2)),

            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveMaxPool2d((1, 1))     # →  (B,128,1,1)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),                    # 128-d
            nn.Dropout(0.3),
            nn.Linear(128, 1)
        )

    def forward(self, x):
        # x already [B,1,9,384]; DON’T add another unsqueeze
        x = self.features(x)
        return self.classifier(x)

class EmbeddingMLP1D(nn.Module):
    def __init__(self, in_len = 2944):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(in_len, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(256, 1) # Output layer for binary classification
        )

    def forward(self, x):
        return self.layers(x)