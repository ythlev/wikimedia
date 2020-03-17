# Created by Chang Chia-huan
import json, csv, urllib.request, io, math

with open("data.json", newline = "", encoding = "utf-8") as file:
    main = json.loads(file.read())

source = {}
territories = []
for dataset in ["Confirmed", "Recovered"]:
    with urllib.request.urlopen("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-{}.csv".format(dataset)) as response:
        reader = csv.DictReader(io.TextIOWrapper(response, encoding = "utf-8"), delimiter = ",")
        for row in reader:
            row["Country/Region"] = row["Country/Region"].replace("*", "")
            if row["Province/State"] in main:
                row["Country/Region"] = row["Province/State"]
            elif row["Province/State"] != "":
                territories.append(row["Province/State"] + ", " + row["Country/Region"])
            if row["Country/Region"] not in source:
                source[row["Country/Region"]] = {}
            for col in row:
                if col not in ["Province/State", "Country/Region", "Lat", "Long"]:
                    if col not in source[row["Country/Region"]]:
                        source[row["Country/Region"]][col] = {}
                    if dataset not in source[row["Country/Region"]][col]:
                        source[row["Country/Region"]][col][dataset] = 0
                    source[row["Country/Region"]][col][dataset] += int(row[col])

with open("territories.json", "w", newline = "", encoding = "utf-8") as file:
    file.write(json.dumps(territories, indent = 2, ensure_ascii = False))

for place in source:
    for date in source[place]:
        source[place][date]["Active"] = source[place][date]["Confirmed"] - source[place][date]["Recovered"]

list = []
for place in main:
    if place in source:
        peak, peak_date = 0, ""
        for date in source[place]:
            if source[place][date]["Active"] > peak:
                peak = source[place][date]["Active"]
                peak_date = date
        main[place]["date"] = peak_date
        main[place]["cases"] = source[place][date]["Confirmed"]
        main[place]["recovered"] = source[place][date]["Recovered"]
        main[place]["active"] = source[place][date]["Active"]
        if main[place]["active"] != None and main[place]["population"] != None:
            main[place]["pcapita"] = main[place]["active"] / main[place]["population"]
            list.append(main[place]["pcapita"])

list.sort()
high = list[-9]
if list[8] > 0:
    low = list[8]
else:
    low = 1

step = math.log(high / low) / 5

thresholds = [0, 0, 0, 0, 0, 0]
for i in range(5):
    thresholds[i + 1] = round(low * math.exp(step * i), 2)

colours = ["#fee5d9","#fcbba1","#fc9272","#fb6a4a","#de2d26","#a50f15"]

with open("template.svg", "r", newline = "", encoding = "utf-8") as file_in:
    with open("peak.svg", "w", newline = "", encoding = "utf-8") as file_out:
        r = 0
        for row in file_in:
            r += 1
            if r == 158:
                levels = [[], [], [], [], [], []]
                for place in main:
                    if "pcapita" in main[place]:
                        i = 0
                        while i < 5:
                            if main[place]["pcapita"] >= thresholds[i + 1]:
                                i += 1
                            else:
                                break
                        main[place]["threshold met"] = thresholds[i]
                        main[place]["fill"] = colours[i]
                        levels[i].append(main[place]["code"])
                    else:
                        main[place]["fill"] = "#e0e0e0"
                for i in range(6):
                    file_out.write(", ".join(levels[i]) + "\n")
                    file_out.write("{" + "\n")
                    file_out.write("   fill:" + colours[i] + ";\n")
                    file_out.write("}" + "\n")
            else:
                file_out.write(row)

print("Number of data figures:", len(list))
print("Colours:", colours)
print("Thresholds:", thresholds, "Max:", max(list))

with open("data-generated.json", "w", newline = "", encoding = "utf-8") as file:
    file.write(json.dumps(main, indent = 2, ensure_ascii = False))
