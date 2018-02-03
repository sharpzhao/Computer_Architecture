import matplotlib.pyplot as plt
import sys

args = sys.argv

names = []
X = []
Mobile_X = []
count = 1
legend = []
for m in range(2006, 2018):
    names.append(str(m)[2: 4])
    for n in range(1, 5):
        X.append(count)
        if n != 1:
            names.append("")
        if m >= 2012:
            Mobile_X.append(count)
        count = count + 1

for i in range(1, 3):
    with open(args[i], "r") as f:
        Y = []
        prev = 0
        for line in f.readlines():
            data = line.split(" ")
            if prev < int(data[1].strip()):
                prev = int(data[1].strip())
            Y.append(prev)
        leg, = plt.plot(X, Y, label=("PC SINGLE CORE" if i == 1 else "PC MULTIPLE CORE"))
        legend.append(leg)
for i in range(3, 5):
    with open(args[i], "r") as f:
        Y = []
        prev = 0
        for line in f.readlines():
            data = line.split(" ")
            if prev < int(data[1].strip()):
                prev = int(data[1].strip())
            Y.append(prev)
        leg, = plt.plot(Mobile_X, Y, label=("MOBILE SINGLE CORE" if i == 1 else "MOBILE MULTIPLE CORE"))
        legend.append(leg)
plt.xticks(X, names)
plt.legend(handles=legend)
plt.savefig("plot", dpi = 500)
