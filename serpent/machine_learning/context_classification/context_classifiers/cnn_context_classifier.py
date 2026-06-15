"""A small PyTorch/torchvision context classifier.

Replaces the dead TensorFlow/Keras Inception-V3 / Xception classifiers. A context
classifier labels which on-screen "context" a frame belongs to (e.g. menu vs.
in-game vs. game-over), trained from ``datasets/current/{training,validation}``
laid out as one subdirectory per class (the ImageFolder convention).

The network is a compact CNN with adaptive pooling (so it is input-size
agnostic) trained from scratch — no pretrained-weight download required. Runs on
the auto-detected device (CUDA/ROCm/MPS/CPU).
"""

from __future__ import annotations

import numpy as np
import skimage.transform
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import transforms
from torchvision.datasets import ImageFolder

from serpent.machine_learning.context_classification.context_classifier import ContextClassifier
from serpent.machine_learning.device import get_device

TRAINING_PATH = "datasets/current/training"
VALIDATION_PATH = "datasets/current/validation"
IMAGE_SIZE = (96, 96)
CONFIDENCE_THRESHOLD = 0.5


class _ContextCNN(nn.Module):
    def __init__(self, num_classes: int):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
        )
        self.classifier = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        return self.classifier(x)


class CNNContextClassifier(ContextClassifier):
    def __init__(self, input_shape=None):
        super().__init__()

        self.input_shape = input_shape
        self.device = get_device()

        self.class_names: list[str] | None = None
        self._transform = transforms.Compose(
            [transforms.Resize(IMAGE_SIZE), transforms.ToTensor()]
        )

    def train(self, epochs=3, autosave=False, validate=True, learning_rate=1e-3):
        dataset = ImageFolder(TRAINING_PATH, transform=self._transform)
        self.class_names = list(dataset.classes)

        loader = DataLoader(dataset, batch_size=32, shuffle=True)

        model = _ContextCNN(len(self.class_names)).to(self.device)
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        loss_fn = nn.CrossEntropyLoss()

        model.train()

        for epoch in range(epochs):
            epoch_loss = 0.0

            for images, labels in loader:
                images, labels = images.to(self.device), labels.to(self.device)

                optimizer.zero_grad()
                loss = loss_fn(model(images), labels)
                loss.backward()
                optimizer.step()

                epoch_loss += loss.item()

            print(f"Epoch {epoch + 1}/{epochs} - loss: {epoch_loss / max(len(loader), 1):.4f}")

            if autosave:
                self.classifier = model
                self.save_classifier(f"datasets/context_classifier_{epoch + 1:02d}.pth")

        self.classifier = model

        if validate:
            self.validate()

    def validate(self):
        import os

        if self.classifier is None or not os.path.isdir(VALIDATION_PATH):
            return None

        dataset = ImageFolder(VALIDATION_PATH, transform=self._transform)
        loader = DataLoader(dataset, batch_size=32)

        self.classifier.eval()
        correct = total = 0

        with torch.no_grad():
            for images, labels in loader:
                images, labels = images.to(self.device), labels.to(self.device)
                predictions = self.classifier(images).argmax(dim=1)
                correct += int((predictions == labels).sum())
                total += labels.numel()

        accuracy = correct / total if total else 0.0
        print(f"Validation accuracy: {accuracy:.2%} ({correct}/{total})")
        return accuracy

    def predict(self, input_frame):
        if self.classifier is None or not self.class_names:
            raise RuntimeError("The classifier has not been trained or loaded.")

        resized = skimage.transform.resize(input_frame, IMAGE_SIZE, anti_aliasing=True)
        tensor = torch.tensor(resized, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0)
        tensor = tensor.to(self.device)

        self.classifier.eval()

        with torch.no_grad():
            probabilities = torch.softmax(self.classifier(tensor), dim=1)[0]

        confidence, index = torch.max(probabilities, dim=0)

        if confidence.item() < CONFIDENCE_THRESHOLD:
            return None

        return self.class_names[int(index)]

    def save_classifier(self, file_path):
        if self.classifier is None:
            raise RuntimeError("There is no trained classifier to save.")

        torch.save(
            {"state_dict": self.classifier.state_dict(), "class_names": self.class_names},
            file_path,
        )

    def load_classifier(self, file_path):
        checkpoint = torch.load(file_path, map_location=self.device, weights_only=False)

        self.class_names = checkpoint["class_names"]

        model = _ContextCNN(len(self.class_names))
        model.load_state_dict(checkpoint["state_dict"])

        self.classifier = model.to(self.device)


__all__ = ["CNNContextClassifier"]
