import tensorflow as tf
import time

# Reference: https://www.tensorflow.org/guide/gpu

# List available GPUs
print("Num GPUs Available: ", len(tf.config.list_physical_devices("GPU")))

# Set this to True to explicitly show which device is used for each of the following computations
# NOTE: this is useful if you suspect that there is an issue utilising the GPU,
# as TensorFlow will silently fall back to using the CPU without throwing an error
tf.debugging.set_log_device_placement(False)


# Create two large random matrices
size = 5000  # Adjust size for larger computations
a = tf.random.uniform((size, size), minval=0, maxval=1, dtype=tf.float32)
b = tf.random.uniform((size, size), minval=0, maxval=1, dtype=tf.float32)

# Perform matrix multiplication on the GPU
with tf.device("/GPU:0"):
    print("Running matrix multiplication on GPU...")
    start_time = time.time()
    c = tf.matmul(a, b)
    gpu_time = time.time() - start_time
    print(f"GPU computation took: {gpu_time:.6f} seconds")

# Perform matrix multiplication on the CPU for comparison
with tf.device("/CPU:0"):
    print("Running matrix multiplication on CPU...")
    start_time = time.time()
    c_cpu = tf.matmul(a, b)
    cpu_time = time.time() - start_time
    print(f"CPU computation took: {cpu_time:.6f} seconds")
