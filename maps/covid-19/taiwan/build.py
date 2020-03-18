# 張嘉桓 製
import argparse, csv, urllib.request, json, math

parser = argparse.ArgumentParser(description = "This script generates an svg map for the COVID-19 outbreak in Taiwan")
parser.add_argument("-c", "--count", help = "Generate case count map", action = "store_const", const = "count", dest = "type")
parser.add_argument("-p", "--pcapita", help = "Generate per capita cases map", action = "store_const", const = "pcapita", dest = "type")
args = vars(parser.parse_args())

def get_value(count, pcapita):
    if args["type"] == "count":
        return count
    elif args["type"] == "pcapita":
        return pcapita

main = {}

with open("places.csv", newline = "", encoding = "utf-8-sig") as file:
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
        if row["縣市"] in main:
            main[row["縣市"]]["cases"] += int(row["確定病例數"])

list = []
for place in main:
    main[place]["pcapita"] = round(main[place]["cases"] / main[place]["population"] * 1000000, 2)
    list.append(main[place][get_value("cases", "pcapita")])
list.sort()

high = list[-2]
step = math.sqrt(high) / 5

thresholds = [0, 0, 0, 0, 0, 0]
for i in range(6):
    thresholds[i] = round(math.pow(step * i, 2), get_value(0, 2))

colours = ["#fee5d9","#fcbba1","#fc9272","#fb6a4a","#de2d26","#a50f15"]

with open("template.svg", "r", newline = "", encoding = "utf-8") as file_in:
    with open(get_value("counts.svg", "per-capita.svg"), "w", newline = "", encoding = "utf-8") as file_out:
        for row in file_in:
            written = False
            for place, attrs in main.items():
                if row.find(place) > -1:
                    i = 0
                    while i < 5:
                        if attrs[get_value("cases", "pcapita")] >= thresholds[i + 1]:
                            i += 1
                        else:
                            break
                    main[place]["threshold met"] = thresholds[i]
                    main[place]["colour"] = colours[i]
                    file_out.write(row.replace('id="{}"'.format(place), 'style="fill:{}"'.format(attrs["colour"])))
                    written = True
                    break
            if written == False:
                file_out.write(row)

for place in main:
    print(place, main[place])

cases = []
for attrs in main.values():
    cases.append(attrs["cases"])
print("Total cases:", sum(cases))
print("Colours:", colours)
print("Thresholds:", thresholds, "95th percentile:", high, "Max:", max(list))
