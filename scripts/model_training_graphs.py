
# Script para graficar métricas de los entrenamientos realizados con diferentes configuraciones

import matplotlib.pyplot as plt
import csv

x_train24= []
y_train24 = []

with open('../scripts/runs/pose/train24/results.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter = ',')
    next(plots)  # Skip header
    for row in plots:
        x_train24.append(int(row[0].strip()))
        y_train24.append(float(row[14].strip()))

x_train2 = []
y_train2 = []
with open('../scripts/runs/pose/train2/results.csv','r') as csvfile:
    train2 = csv.reader(csvfile, delimiter = ',')
    next(train2)  # Skip header
    for row in train2:
        x_train2.append(int(row[0].strip()))
        y_train2.append(float(row[14].strip()))

x_train8 = []
y_train8 = []
with open('../scripts/runs/pose/train8/results.csv','r') as csvfile:
    train8 = csv.reader(csvfile, delimiter = ',')
    next(train8)  # Skip header
    for row in train8:
        x_train8.append(int(row[0].strip()))
        y_train8.append(float(row[14].strip()))

x_train15 = []
y_train15 = []
with open('../scripts/runs/pose/train15/results.csv','r') as csvfile:
    train15 = csv.reader(csvfile, delimiter = ',')
    next(train15)  # Skip header
    for row in train15:
        x_train15.append(int(row[0].strip()))
        y_train15.append(float(row[14].strip()))

plt.plot(x_train24, y_train24, color= "g", label = "mAP50 - Train 24")
plt.plot(x_train2, y_train2, color= "b", label = "mAP50 - Train 2")
plt.plot(x_train8, y_train8, color= "r", label = "mAP50 - Train 8")
plt.plot(x_train15, y_train15, color= "orange", label = "mAP50 - Train 15")
plt.xlabel("Epochs", labelpad=50)  # Increase distance from axis
plt.xticks(range(0, max(x_train24)+1, 2))
plt.ylabel("mAP50", labelpad=60)
plt.ylim(0.4, 1.00)
plt.yticks([i / 1000 for i in range(400, 1001, 15)])
plt.title('mAP50 vs Epochs')
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.4)
plt.show()


