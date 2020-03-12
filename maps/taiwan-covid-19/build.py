# 張嘉桓 製
import argparse, csv, urllib.request, json, math

parser = argparse.ArgumentParser(description = "This script generates an svg map for the COVID-19 outbreak in Taiwan")
parser.add_argument("-c", "--count", help = "Generate case count map", action = "store_const", const = "count", dest = "type")
parser.add_argument("-d", "--density", help = "Generate case density map", action = "store_const", const = "density", dest = "type")
args = vars(parser.parse_args())

def get_value(count, density):
    if args["type"] == "count":
        return count
    elif args["type"] == "density":
        return density

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

list = []
for attrs in main.values():
    attrs["density"] = round(attrs["cases"] / attrs["population"] * 1000000, 2)
    list.append(attrs[get_value("cases", "density")])
list.sort()

high = list[-2]
if list[1] > 0:
    low = list[1]
else:
    low = 1

step = get_value(math.log(high / low) / 5, high / 5)

thresholds = [0, 0, 0, 0, 0, 0]
for i in range(5):
    thresholds[i + 1] = get_value(round(low * math.exp(step * i)), step * (i + 1))

colours = ["#fee5d9","#fcbba1","#fc9272","#fb6a4a","#de2d26","#a50f15"]

with open("template.svg", "r", newline = "", encoding = "utf-8") as file_in:
    with open(get_value("counts.svg", "densities.svg"), "w", newline = "", encoding = "utf-8") as file_out:
        for row in file_in:
            written = False
            for place, attrs in main.items():
                if row.find(place) > -1:
                    i = 0
                    while i < 5:
                        if get_value(attrs["cases"], attrs["density"]) >= thresholds[i + 1]:
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
print("Thresholds:", thresholds, "Max:", max(list))
