import pandas as pd
import matplotlib.pyplot as plt

# Sample data
data = pd.read_csv('results.csv')

# Create a DataFrame from the data
df = pd.DataFrame(data)
df.columns = df.columns.str.strip()
    
# Plotting
plt.figure(figsize=(10, 6))

# Plot precision
plt.plot(df['epoch'], df['metrics/precision(B)'], label='Precision')

# Plot recall
plt.plot(df['epoch'], df['metrics/recall(B)'], label='Recall')

# Plot mAP50
plt.plot(df['epoch'], df['metrics/mAP50(B)'], label='mAP50')

# Plot mAP50-95
plt.plot(df['epoch'], df['metrics/mAP50-95(B)'], label='mAP50-95')

# Set plot labels and title
plt.xlabel('Epoch')
plt.ylabel('Percentage (%)')
plt.title('Object Detection Metrics Over Epochs')
plt.legend()
plt.grid(True)

# Show the plot
plt.show()