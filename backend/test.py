import matplotlib.pyplot as plt
import numpy as np

# -----------------------------
# Force and Acceleration Vectors
# -----------------------------

# Given values
force = 20       # Newton
mass = 5         # Kilogram
acceleration = force / mass  # m/s² (Newton's second law)

# Create figure and axis
fig, ax = plt.subplots(figsize=(6, 6))

# Set axis limits
ax.set_xlim(0, 5)
ax.set_ylim(0, 5)

# Hide axis for cleaner look
ax.axis("off")

# Draw Force vector (to the right)
ax.arrow(
    0, 2.5, 2, 0,
    head_width=0.3,
    head_length=0.3,
    fc="red", ec="red",
    label="Force (20 N)"
)

# Draw Acceleration vector (same direction, scaled down for visibility)
ax.arrow(
    0, 1, acceleration / 2, 0,
    head_width=0.3,
    head_length=0.3,
    fc="blue", ec="blue",
    label="Acceleration (4 m/s²)"
)

# Add labels near vectors
ax.text(2.1, 2.5, "Force (20 N)", color="red", fontsize=10)
ax.text(acceleration / 2 + 0.1, 1, "Acceleration (4 m/s²)", color="blue", fontsize=10)

# Add title
ax.set_title("Force and Acceleration Vectors", fontsize=14, fontweight="bold")

# Save plot
plt.savefig("plot.png", bbox_inches="tight")
plt.close()
