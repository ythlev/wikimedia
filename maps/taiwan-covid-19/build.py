# 張嘉桓 製
import csv, urllib.request, json, math

main = {}

with open("populations.csv", newline = "", encoding = "utf-8-sig") as file:
    reader = csv.DictReader(file)
    for row in reader:
        if row["區域別"] != "總計":
            main[row["區域別"].replace("臺", "台")] = {
                "cases": 0,
                "population": int(row["總計"].replace(",", ""))
            }

with urllib.request.urlopen("https://od.cdc.gov.tw/eic/Weekly_Age_County_Gender_19CoV.json") as response:
    data = json.loads(response.read())
    for row in data:
        for place in main:
            if row["縣市"] == place:
                main[place]["cases"] += int(row["確定病例數"])
                break

for attrs in main.values():
    attrs["density"] = attrs["cases"] / attrs["population"]

list = []
for attrs in main.values():
    list.append(attrs["density"])
list.sort()

low = 0
if list[1] > 0:
    low = list[1]
else:
    for value in list:
        if value > 0:
            low = value
            break
high = list[-2]

step = math.log(high / low) / 5

thresholds = [0, 0, 0, 0, 0, 0]
for i in range(5):
    thresholds[i + 1] = low * math.exp(step * i)

colours = ["#fee5d9","#fcbba1","#fc9272","#fb6a4a","#de2d26","#a50f15"]

with open("template.svg", "r", newline = "", encoding = "utf-8") as file_in:
    with open("output.svg", "w", newline = "", encoding = "utf-8") as file_out:
        for row in file_in:
            written = False
            for place, attrs in main.items():
                if row.find(place) > -1:
                    i = 0
                    while i < 5:
                        if attrs["density"] >= thresholds[i + 1]:
                            i += 1
                        else:
                            break
                    main[place]["threshold met"] = thresholds[i]
                    main[place]["colour"] = colours[i]
                    file_out.write(row.replace('id="%s"' % place, 'style="fill:%s"' % attrs["colour"]))
                    written = True
                    break
            if written == False:
                file_out.write(row)

for place, attrs in main.items():
    print(place, attrs)

cases = []
for attrs in main.values():
    cases.append(attrs["cases"])
print("Total cases:", sum(cases))

print("Colours:", colours)

thresholds_rescaled = []
for value in thresholds:
    thresholds_rescaled.append(round(1000000 * value, 2))
print("Thresholds (ppm):", thresholds_rescaled, "Max:", round(1000000 * max(list), 2), "Second:", round(1000000 * high, 2))
