import csv, statistics, math

main = {}
with open("data.csv", newline = "", encoding = "utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        main[row["name"]] = []

values = []
with open("105_165-9.csv", newline = "", encoding = "utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        if (row["﻿縣市"] + row["鄉鎮市區"]) in main:
            main[row["﻿縣市"] + row["鄉鎮市區"]].append(float(row["中位數"]))

for place in main:
    main[place] = statistics.median(main[place])
    values.append(main[place])

q = statistics.quantiles(values, n = 100)
step = math.sqrt(statistics.mean(values) - q[0]) / 3

threshold = [0, 0, 0, 0, 0, 0]
for i in range(1, 6):
    threshold[i] = math.pow(i * step, 2) + q[0]

colour = ['#f2f0f7','#dadaeb','#bcbddc','#9e9ac8','#756bb1','#54278f']
with open("template.svg", "r", newline = "", encoding = "utf-8") as file_in:
    with open("result.svg", "w", newline = "", encoding = "utf-8") as file_out:
        for row in file_in:
            written = False
            for place in main:
                if row.find('id="{}"'.format(place)) > -1:
                    i = 0
                    while i < 5:
                        if main[place] >= threshold[i + 1]:
                            i += 1
                        else:
                            break
                    file_out.write(row.replace('id="{}"'.format(place), 'style="fill:{}"'.format(colour[i])))
                    written = True
                    break
            if written == False:
                file_out.write(row)

for n in threshold:
    print(round(n, 3))
