import sys

args = sys.argv

final = {}
for i in range(1, len(args)):
    with open(args[i], "r") as f:
        for line in f.readlines():
            data = line.split(" ")
            date, score = data[0].strip(), int(data[1].strip())
            if date in final:
                if final[date] < score:
                    final[date] = score
            else:
                final[date] = score
final_score = sorted(final.items(), key=lambda item:item[0])
with open("new_data.txt", "w") as f:
    for line in final_score:
        f.write(line[0] + " " + str(line[1]) + "\n")

#deal with increasing data
prev = 0
with open("new_plot_data.txt", "w") as f:
    for line in final_score:
        if prev < line[1]:
            prev = line[1]
        f.write(line[0] + " " + str(prev) + "\n")
