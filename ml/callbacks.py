from tensorflow.keras.callbacks import Callback


class StatusUpdateCallback(Callback):
    # Custom callback to update the status of the job
    def __init__(self, container, set_status_fn):
        super(StatusUpdateCallback, self).__init__()
        self.container = container
        self.set_status_fn = set_status_fn
        self.seen_batches = 0
        self.epochs = 0

    # Executed at the start of training
    def on_train_begin(self, logs=None):
        self.set_status_fn(self.container, "Starting training...")

    # Executed at the start of each epoch
    def on_epoch_begin(self, epoch, logs=None):
        self.seen_batches = 0  # Reset counter at start of epoch
        self.epochs += 1
        self.set_status_fn(
            self.container,
            f"Starting training epoch {epoch + 1}/{self.params['epochs']}",
        )

    # Executed at the end of each batch passed through the model
    def on_train_batch_end(self, batch, logs=None):
        self.seen_batches += 1
        if logs:
            total_batches = self.params["steps"]
            progress = (self.seen_batches / total_batches) * 100
            self.set_status_fn(
                self.container,
                f"Batch {self.seen_batches}/{total_batches} ({progress:.1f}%) {self.epochs}/{self.params['epochs']}",
            )

    # Executed at the end of training
    def on_train_end(self, logs=None):
        final_metrics = " - ".join(
            [f"{key}: {value:.4f}" for key, value in logs.items()]
        )
        self.set_status_fn(self.container, f"Training completed - {final_metrics}")
