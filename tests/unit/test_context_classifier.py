"""The torchvision context classifier (replaces the dead TF/Keras ones)."""

import numpy as np
import pytest
from PIL import Image

from serpent.machine_learning.context_classification.context_classifier import ContextClassifier
from serpent.machine_learning.context_classification.context_classifiers import CNNContextClassifier


def _write_images(directory, color, count=4):
    directory.mkdir(parents=True, exist_ok=True)
    for i in range(count):
        array = np.zeros((16, 16, 3), dtype="uint8")
        array[:, :] = color
        Image.fromarray(array).save(directory / f"frame_{i}.png")


@pytest.fixture
def dataset(tmp_path, monkeypatch):
    for split in ("training", "validation"):
        _write_images(tmp_path / "datasets" / "current" / split / "menu", (220, 20, 20))
        _write_images(tmp_path / "datasets" / "current" / split / "game", (20, 20, 220))
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_default_mapping_is_torchvision():
    assert ContextClassifier.available_implementations() == ["CNNContextClassifier"]
    assert "CNNContextClassifier" in ContextClassifier.context_classifier_mapping()


def test_train_predict_and_roundtrip(dataset):
    classifier = CNNContextClassifier(input_shape=(16, 16, 3))
    classifier.train(epochs=2, validate=True)

    assert classifier.class_names == ["game", "menu"]  # ImageFolder sorts class names

    frame = np.zeros((16, 16, 3), dtype="uint8")
    frame[:, :] = (20, 20, 220)

    prediction = classifier.predict(frame)
    assert prediction is None or prediction in {"game", "menu"}

    # Save -> load round-trip preserves classes and is deterministic.
    model_path = dataset / "context.pth"
    classifier.save_classifier(str(model_path))

    restored = CNNContextClassifier(input_shape=(16, 16, 3))
    restored.load_classifier(str(model_path))

    assert restored.class_names == ["game", "menu"]
    assert restored.predict(frame) == classifier.predict(frame)
