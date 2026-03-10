import matplotlib.pyplot as plt

# Data
tokens = [5, 19, 46, 75, 100]
time_seconds = [201, 82, 56, 33, 20]

# Create plot
plt.figure(figsize=(8, 6))
plt.plot(tokens, time_seconds, 'o-', color='#2196F3', linewidth=2, markersize=8)

# Labels
plt.xlabel('Prompt Complexity (tokens)', fontsize=12)
plt.ylabel('Time (s)', fontsize=12)
plt.title('Prompt Length vs Task Completion Time', fontsize=14, fontweight='bold')

# Grid
plt.grid(True, linestyle='--', alpha=0.7)

# Add labels to each point
for i, (x, y) in enumerate(zip(tokens, time_seconds)):
    plt.annotate(f'{y}s', (x, y), textcoords='offset points', 
                 xytext=(0, 10), ha='center', fontsize=10, fontweight='bold')

# Tight layout
plt.tight_layout()

plt.savefig('prompt_time_chart.png', dpi=300)
plt.show()