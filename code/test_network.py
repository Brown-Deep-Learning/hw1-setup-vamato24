import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

print("This tests TensorFlow by training a network to create spiral glaxies!")

def create_galaxy_data(n_points=2000):
    t = np.linspace(0, 4*np.pi, n_points)
    
    arms = []
    colors = []
    
    for arm in range(3): 
        angle_offset = arm * 2 * np.pi / 3
        
        r = 0.5 * np.exp(0.3 * t) + np.random.normal(0, 0.1, n_points)
        theta = t + angle_offset + np.random.normal(0, 0.05, n_points)
        
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        arms.extend(list(zip(x, y)))
        
        distance = np.sqrt(x**2 + y**2)
        arm_colors = plt.cm.plasma(distance / np.max(distance) + arm * 0.3)[:, :3]
        colors.extend(arm_colors)
    
    return np.array(arms), np.array(colors)

positions, colors = create_galaxy_data(2000)
X_train = positions
y_train = colors

model = tf.keras.Sequential([
    tf.keras.Input(shape=(2,)),  # x, y coordinates
    tf.keras.layers.Dense(64, activation="relu"),
    tf.keras.layers.Dense(32, activation="relu"),
    tf.keras.layers.Dense(16, activation="tanh"),
    tf.keras.layers.Dense(3, activation="sigmoid")
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.01), 
    loss='mean_squared_error'
)

history = model.fit(
    X_train, y_train, 
    epochs=75, 
    verbose=1,
    validation_split=0.2
)

x_range = np.linspace(-8, 8, 200)
y_range = np.linspace(-8, 8, 200)
X_grid, Y_grid = np.meshgrid(x_range, y_range)
grid_points = np.column_stack([X_grid.ravel(), Y_grid.ravel()])

predicted_colors = model.predict(grid_points)
predicted_colors = predicted_colors.reshape(200, 200, 3)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

ax1.scatter(X_train[:, 0], X_train[:, 1], c=y_train, s=1, alpha=0.6)
ax1.set_title("Original Galaxy Training Data", fontsize=14, fontweight='bold')
ax1.set_xlabel("X Coordinate")
ax1.set_ylabel("Y Coordinate")
ax1.set_aspect('equal')
ax1.grid(True, alpha=0.3)

ax2.imshow(predicted_colors, extent=[-8, 8, -8, 8], origin='lower', aspect='equal')
ax2.set_title("Neural Network's Galaxy", fontsize=14, fontweight='bold')
ax2.set_xlabel("X Coordinate")
ax2.set_ylabel("Y Coordinate")

plt.suptitle("Neural Network Galaxy Generator", 
             fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig("neural_galaxy.png", dpi=300, bbox_inches='tight')

print("If you make it to this point, CONGRATS! TensorFlow is working perfectly!")
