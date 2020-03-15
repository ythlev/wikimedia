# Created by Chang Chia-huan
import argparse, json, re, csv, urllib.request, io, datetime, math

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

with open("data.json", newline = "", encoding = "utf-8") as file:
    main = json.loads(file.read())

# fetch figures from Wikipedia; credits: Dan Polansky
def grabFromTemplate():
    url="https://en.wikipedia.org/wiki/Template:2019%E2%80%9320_coronavirus_pandemic_data"
    allLines = []
    for line in urllib.request.urlopen(url):
      allLines.append((line.decode()).rstrip())
    allLines = " ".join(allLines)
    allLines = re.sub("^.*jquery-tablesorter", "", allLines)
    allLines = re.sub("</table.*", "", allLines)
    allLines = re.sub("<(th|td)[^>]*>", r"<td>", allLines)
    allLines = re.sub("</?(span|img|a|sup)[^>]*>", "", allLines)
    allLines = re.sub("</(th|td|tr)[^>]*>", "", allLines)
    allLines = re.sub("&#91.*?&#93", "", allLines)
    allLines = re.sub(",", "", allLines)
    allLines = re.sub("<small>.*?</small>;?", "", allLines)
    allLines = re.sub("</?i>", "", allLines)

    outData = {}
    rows = allLines.split("<tr> ")
    for row in rows:
        try:
            cols = row.split("<td>")
            cols.pop(0)
            cols.pop(0)
            place = cols.pop(0)
            cols = cols[0:3]
            cols = [int(col) for col in cols]
        except:
            continue
        outData[(place.rstrip()).replace(";", "")] = cols
    #for key, value in outData.items():
    #  print key, value
    return outData
template = grabFromTemplate()

for place in main:
    main[place]["updated"] = None
    for place2 in template:
        place2 = place2.replace(";", "")
        if place2.find(main[place]["names"]["JHU"]) > -1:
            main[place]["names"]["wikipedia"] = place2
            main[place]["cases"] = template[place2][0]
            main[place]["recovered"] = template[place2][2]
            main[place]["updated"] = "from Wikipedia"
            break

with urllib.request.urlopen("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv") as response:
    reader = csv.reader(io.TextIOWrapper(response, encoding = "utf-8"), delimiter = ",")
    for row in reader:
        if row[1] in ["Country/Region", "Cruise Ship"]:
            if row[1] == "Country/Region":
                global date
                date = row[-1]
            continue
        row[1] = row[1].replace("*", "")
        for place in main:
            if main[place]["updated"]:
                continue
            else:
                if main[place]["names"]["JHU"] == row[0]:
                    if row[0] in main:
                        main[row[0]]["cases"] = int(row[-1])
                        break
                    elif row[1] in main:
                        if row[0] != "":
                            places.append(row[0] + ", " + row[1])
                        main[row[1]]["cases"] += int(row[-1])
                        break
                    else:
                        print(row[0], row[1], "not found")
                        quit()
                main[place]["updated"] = "from JHU"

thresholds = [0, 1, 10, 100, 1000, 10000]
colours = ["#e0e0e0", "#ffC0C0","#ee7070","#c80200","#900000","#510000"]

with open("template.svg", "r", newline = "", encoding = "utf-8") as file_in:
    with open(get_value("counts.svg", "per-capita.svg"), "w", newline = "", encoding = "utf-8") as file_out:
        r = 0
        for row in file_in:
            r += 1
            if r == 158:
                list = [[], [], [], [], [], []]
                for place, attrs in main.items():
                    i = 0
                    while i < 5:
                        if get_value(attrs["cases"], attrs["pcapita"]) >= thresholds[i + 1]:
                            i += 1
                        else:
                            break
                    main[place]["threshold met"] = thresholds[i]
                    main[place]["fill"] = colours[i]
                    list[i].append(place)
                for i in range(6):
                    file_out.write(", ".join(list[i]) + "\n")
                    file_out.write("{" + "\n")
                    file_out.write("   fill:" + colours[i] + ";\n")
                    file_out.write("}" + "\n")
            else:
                file_out.write(row)

with open("data-generated.json", "w", newline = "", encoding = "utf-8") as file:
    file.write(json.dumps(main, indent = 2, ensure_ascii = False))

for place, attrs in main.items():
    print(place, attrs)

cases = []
for attrs in main.values():
    cases.append(attrs["cases"])
print("Total cases:", "{:,}".format(sum(cases)), "in", len(cases), "areas as of", date)
print("Colours:", colours)
print("Thresholds:", thresholds, "Max:", max(cases))
