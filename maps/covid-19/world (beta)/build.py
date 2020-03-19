# Created by Chang Chia-huan
import pathlib, json, csv, io, urllib.request, math, statistics

with open("data.json", newline = "", encoding = "utf-8") as file:
    main = json.loads(file.read())

territories = []
with urllib.request.urlopen("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv") as response:
    reader = csv.reader(io.TextIOWrapper(response, encoding = "utf-8"), delimiter = ",")
    for row in reader:
        if row[0] == "Province/State":
            continue
        row[1] = row[1].replace("*", "")
        if row[0] in main:
            row[1] = row[0]
        elif row[0] != "":
            territories.append(row[0] + ", " + row[1])
        if row[1] in main:
            if main[row[1]]["cases"] == None:
                main[row[1]]["cases"] = int(row[-1])
            else:
                main[row[1]]["cases"] += int(row[-1])

with open("territories.json", "w", newline = "", encoding = "utf-8") as file:
    file.write(json.dumps(territories, indent = 2, ensure_ascii = False))

values = []
for place in main:
    if main[place]["cases"] != None and main[place]["population"] != None:
        main[place]["pcapita"] = round(main[place]["cases"] / main[place]["population"], 2)
        values.append(main[place]["pcapita"])

step = math.sqrt(statistics.median(values)) / 3

thresholds = [0, 0, 0, 0, 0, 0, 0]
for i in range(7):
    thresholds[i] = round(math.pow(step * i, 2), 2)

colours = ['#fee5d9','#fcbba1','#fc9272','#fb6a4a','#ef3b2c','#cb181d','#99000d']

with open("template.svg", "r", newline = "", encoding = "utf-8") as file_in:
    with open("per-capita.svg", "w", newline = "", encoding = "utf-8") as file_out:
        r = 0
        for row in file_in:
            r += 1
            if r == 158:
                levels = [[], [], [], [], [], [], []]
                for place in main:
                    if "pcapita" in main[place]:
                        i = 0
                        while i < 6:
                            if main[place]["pcapita"] >= thresholds[i + 1]:
                                i += 1
                            else:
                                break
                        main[place]["threshold met"] = thresholds[i]
                        main[place]["fill"] = colours[i]
                        levels[i].append(main[place]["code"])
                    else:
                        main[place]["fill"] = "#e0e0e0"
                for i in range(7):
                    file_out.write(", ".join(levels[i]) + "\n")
                    file_out.write("{" + "\n")
                    file_out.write("   fill:" + colours[i] + ";\n")
                    file_out.write("}" + "\n")
            else:
                file_out.write(row)

print("Number of data figures:", len(values))
print("Colours:", colours)
print("Thresholds:", thresholds, "Max:", max(values))

with open("data-generated.json", "w", newline = "", encoding = "utf-8") as file:
    file.write(json.dumps(main, indent = 2, ensure_ascii = False))
