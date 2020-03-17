# Created by Chang Chia-huan
import argparse, csv, io, urllib.request, math

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

with open("populations.csv", newline = "", encoding = "utf-8-sig") as file:
    reader = csv.DictReader(file)
    for row in reader:
        main[row["nam"]] = {
            "cases": 0,
            "population": None
        }

with urllib.request.urlopen("https://dl.dropboxusercontent.com/s/6mztoeb6xf78g5w/COVID-19.csv") as response:
    reader = csv.DictReader(io.TextIOWrapper(response, encoding = 'utf-8'), delimiter=',')
    for row in reader:
        if row["Hospital Pref"] != "Unknown":
            if row["Hospital Pref"] in ["Nigata", "Niigata "]:
                row["Hospital Pref"] = "Niigata"
            main[row["Hospital Pref"]]["cases"] += 1

list = []
for attrs in main.values():
    # attrs["pcapita"] = round(attrs["cases"] / attrs["population"] * 1000000, 2)
    list.append(attrs[get_value("cases", "pcapita")])
list.sort()

high = list[-2]
if list[1] > 0:
    low = list[1]
else:
    low = 1

step = get_value(math.log(high / low) / 5, high / 5)

thresholds = [0, 0, 0, 0, 0, 0]
for i in range(5):
    thresholds[i + 1] = get_value(round(low * math.exp(step * i)), round(step * (i + 1), 2))

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

for place, attrs in main.items():
    print(place, attrs)

cases = []
for attrs in main.values():
    cases.append(attrs["cases"])
print("Total cases:", sum(cases))
print("Colours:", colours)
print("Thresholds:", thresholds, "Max:", max(list))
