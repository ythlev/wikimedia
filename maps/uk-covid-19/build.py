# Created by Chang Chia-huan
import urllib.request, json, csv, io, math

with open("subdivisions.json", newline = "", encoding = "utf-8") as file:
    places = json.loads(file.read())

main = {}
for place in places:
    if place.find("E") > -1:
        main[place] = {"cases": 0}

with urllib.request.urlopen("https://www.arcgis.com/sharing/rest/content/items/b684319181f94875a6879bbc833ca3a6/data") as response:
    reader = csv.DictReader(io.TextIOWrapper(response, encoding = 'utf-8'), delimiter=',')
    for row in reader:
        for place in main:
            if row["GSS_CD"] == place:
                main[place]["cases"] = int(row["TotalCases"])
                break

list = []
for attrs in main.values():
    list.append(attrs["cases"])
list.sort()

high = list[-2]
if list[1] == 0:
    low = 1
else:
    low = list[1]

step = math.log(high / low) / 5

thresholds = [0, 0, 0, 0, 0, 0]
for i in range(5):
    thresholds[i + 1] = round(low * math.exp(step * i))

colours = ["#fee5d9","#fcbba1","#fc9272","#fb6a4a","#de2d26","#a50f15"]

with open("template.svg", "r", newline = "", encoding = "utf-8") as file_in:
    with open("output.svg", "w", newline = "", encoding = "utf-8") as file_out:
        for row in file_in:
            written = False
            for place, attrs in main.items():
                if row.find(place) > -1:
                    i = 0
                    while i < 5:
                        if attrs["cases"] >= thresholds[i + 1]:
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

print("Total cases:", sum(list))
print("Colours:", colours)
print("Thresholds:", thresholds, "Max:", max(list))
