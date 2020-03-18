# Created by Chang Chia-huan
import argparse, csv, urllib.request, io, math

parser = argparse.ArgumentParser(description = "This script generates an svg map for the COVID-19 outbreak in the UK")
parser.add_argument("-c", "--count", help = "Generate case count map", action = "store_const", const = "count", dest = "type")
parser.add_argument("-p", "--pcapita", help = "Generate per capita cases map", action = "store_const", const = "pcapita", dest = "type")
args = vars(parser.parse_args())

def get_value(count, pcapita):
    if args["type"] == "count":
        return count
    elif args["type"] == "pcapita":
        return pcapita

main = {}

with open("places.csv", newline = "", encoding = "utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        main[row["code"]] = {
            "cases": int(row["cases"]),
            "population": int(row["population"])
        }

with urllib.request.urlopen("https://www.arcgis.com/sharing/rest/content/items/b684319181f94875a6879bbc833ca3a6/data") as response:
    reader = csv.DictReader(io.TextIOWrapper(response, encoding = 'utf-8'), delimiter=',')
    for row in reader:
        if row["GSS_CD"] in main:
            main[row["GSS_CD"]]["cases"] = int(row["TotalCases"])

list = []
for place in main:
    main[place]["pcapita"] = round(main[place]["cases"] / main[place]["population"] * 100000, 2)
    list.append(main[place][get_value("cases", "pcapita")])
list.sort()

high = list[-19]
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
                if row.find(place.capitalize()) > -1:
                    i = 0
                    while i < 5:
                        if attrs[get_value("cases", "pcapita")] >= thresholds[i + 1]:
                            i += 1
                        else:
                            break
                    main[place]["threshold met"] = thresholds[i]
                    main[place]["colour"] = colours[i]
                    if place in ["s", "w", "n"]:
                        file_out.write(row.replace('id="', 'style="fill:{}" id="'.format(attrs["colour"])))
                    else:
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
print("Total cases:", sum(cases), "in", len(cases), "areas")
print("Colours:", colours)
print("Thresholds:", thresholds, "95th percentile:", high, "Max:", max(list))
