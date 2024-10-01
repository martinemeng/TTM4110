import numpy as np
import matplotlib.pyplot as plt

# Parameters
#E[T] = 1/lamda_T = 2 -> lambda_T = 0.5
lambda_T = 0.5
samples = 1000

# Generate samples for Xi and Yi, negative exponentially distributed
X = np.random.exponential(scale=1/lambda_T, size=samples)
Y = np.random.exponential(scale=1/lambda_T, size=samples)

# Sort the samples in increasing order
X_sorted = np.sort(X)
Y_sorted = np.sort(Y)

# Step 3: Plot X(j) against Y(j)
plt.plot(X_sorted, Y_sorted, marker='o', linestyle='-', color='b')
plt.title("Plot of Exponentially Distributed Samples (X and Y)")
plt.xlabel("X (sorted)")
plt.ylabel("Y (sorted)")
plt.grid(True)
plt.show()
