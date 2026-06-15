# The concrete context classifiers (CNN Inception-V3 / Xception) are TensorFlow/
# Keras based and currently raise on import (deprecated pending a torchvision
# port — see MODERNIZATION.md Phase G). They are imported lazily where used
# (serpent.machine_learning.context_classification.context_classifier), so this
# package stays importable; importing a classifier directly is what raises.
