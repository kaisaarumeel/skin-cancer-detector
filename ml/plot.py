import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix


def plot(history, true_classes, predicted_classes, class_names):
    # Print classification report
    print("Classification Report:")
    print(
        classification_report(true_classes, predicted_classes, target_names=class_names)
    )

    # Plot confusion matrix
    plt.figure(figsize=(12, 8))
    cm = confusion_matrix(true_classes, predicted_classes)
    # Create the confusion matrix using seaborn heatmap function
    sns.heatmap(
        cm,
        annot=True,
        cmap="magma",
        fmt="d",
        xticklabels=class_names,
        yticklabels=class_names,
    )
    # Set labels for x and y axis
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")
    plt.show()

    # Plot training history
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history.history["loss"], label="Training Loss")
    plt.plot(history.history["val_loss"], label="Validation Loss")
    plt.title("Model Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(history.history["accuracy"], label="Training Accuracy")
    plt.plot(history.history["val_accuracy"], label="Validation Accuracy")
    plt.title("Model Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.tight_layout()
    plt.show()