# Created by Chang Chia-huan
import argparse, csv, urllib.request, io, datetime, math

parser = argparse.ArgumentParser(description = "This script generates an svg map for the COVID-19 outbreak globally")
parser.add_argument("-c", "--count", help = "Generate case count map", action = "store_const", const = "count", dest = "type")
parser.add_argument("-p", "--pcapita", help = "(Not yet available) Generate per capita cases map", action = "store_const", const = "pcapita", dest = "type")
# Only count works for now
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
        main[row["Name"]] = {
            "cases": 0,
            "code": row["Code"].lower(),
            "pcapita": None
        }
        if row["Cases"] != None:
            main[row["Name"]]["cases"] = int(row["Cases"])

places = []

with urllib.request.urlopen("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv") as response:
    reader = csv.reader(io.TextIOWrapper(response, encoding = "utf-8"), delimiter = ",")
    for row in reader:
        if row[1] in ["Country/Region", "Cruise Ship"]:
            if row[1] == "Country/Region":
                global date
                date = row[-1]
            continue
        row[1] = row[1].replace("*", "")
        if row[0] in main:
            main[row[0]]["cases"] = int(row[-1])
        elif row[1] in main:
            if row[0] != "":
                places.append(row[0] + ", " + row[1])
            main[row[1]]["cases"] += int(row[-1])
        else:
            print(row[0], row[1], "not found")
            quit()

with open("places-not-coloured-separately.txt", "w", newline = "", encoding = "utf-8") as file:
    file.write("\n".join(places))

thresholds = [0, 1, 10, 100, 1000, 10000]
colours = ["#e0e0e0", "#ffC0C0","#ee7070","#c80200","#900000","#510000"]

with open("template.svg", "r", newline = "", encoding = "utf-8") as file_in:
    with open(get_value("counts.svg", "per-capita.svg"), "w", newline = "", encoding = "utf-8") as file_out:
        r = 0
        for row in file_in:
            r += 1
            if r == 158:
                list = [[], [], [], [], [], []]
                for country, attrs in main.items():
                    i = 0
                    while i < 5:
                        if get_value(attrs["cases"], attrs["pcapita"]) >= thresholds[i + 1]:
                            i += 1
                        else:
                            break
                    main[country]["threshold met"] = thresholds[i]
                    main[country]["colour"] = colours[i]
                    list[i].append("." + main[country]["code"])
                for i in range(6):
                    file_out.write(", ".join(list[i]) + "\n")
                    file_out.write("{" + "\n")
                    file_out.write("   fill:" + colours[i] + ";\n")
                    file_out.write("}" + "\n")
            else:
                file_out.write(row)

for country, attrs in main.items():
    print(country, attrs)

cases = []
for attrs in main.values():
    cases.append(attrs["cases"])
print("Total cases:", "{:,}".format(sum(cases)), "in", len(cases), "areas as of", date)
print("Colours:", colours)
print("Thresholds:", thresholds, "Max:", max(cases))
