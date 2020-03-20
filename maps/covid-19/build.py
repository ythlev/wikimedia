# Created by Chang Chia-huan
import pathlib, json, csv, io, urllib.request, math, statistics

main = {
    # "uk": {},
    "Japan": {},
    "US": {},
    "France": {},
    "Taiwan": {}
}
unit, outliers = {}, {}
colour = ["#fee5d9","#fcbba1","#fc9272","#fb6a4a","#de2d26","#a50f15"]

for country in main:
    with open((pathlib.Path() / "data" / "places" / country).with_suffix(".csv"), newline = "", encoding = "utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            main[country][row["key"]] = {
                "cases": int(row["cases"]),
                "population": int(row["population"].replace(",", ""))
            }

attrs = []
def arc_gis(query):
    global attrs
    attrs = []
    url = query + "?where=ObjectID%3E0" + "&outFields=*" + "&returnGeometry=false" + "&f=pjson"
    with urllib.request.urlopen(url) as response:
        for entry in json.loads(response.read())["features"]:
            attrs.append(entry["attributes"])

arc_gis("https://services6.arcgis.com/5jNaHNYe2AnnqRnS/arcgis/rest/services/COVID19_Japan/FeatureServer/0/query")
for place in attrs:
    if place["Hospital_Pref"] != "Unknown":
        main["Japan"][place["Hospital_Pref"]]["cases"] += 1

arc_gis("https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/Coronavirus_2019_nCoV_Cases/FeatureServer/1/query")
for place in attrs:
    if place["Country_Region"] == "US" and place["Province_State"] in main["US"]:
        main["US"][place["Province_State"]]["cases"] = int(place["Confirmed"])
arc_gis("https://services1.arcgis.com/5PzxEwuu4GtMhqQ6/arcgis/rest/services/Regions_DT_Project_Vue/FeatureServer/0/query")
for place in attrs:
    main["France"][place["nom"]]["cases"] = int(place["nb_cas"])

with urllib.request.urlopen("https://od.cdc.gov.tw/eic/Weekly_Age_County_Gender_19CoV.json") as response:
    data = json.loads(response.read())
    for row in data:
        main["Taiwan"][row["縣市"]]["cases"] += int(row["確定病例數"])

for country in main:
    values = []
    for place in main[country]:
        main[country][place]["pcapita"] = main[country][place]["cases"] / main[country][place]["population"] * 1000000
        values.append(main[country][place]["pcapita"])

    step = math.sqrt(statistics.median(values)) / 2.5

    threshold = [0, 0, 0, 0, 0, 0]
    for i in range(6):
        threshold[i] = math.pow(step * i, 2)

    with open((pathlib.Path() / "data" / "template" / country).with_suffix(".svg"), "r", newline = "", encoding = "utf-8") as file_in:
        with open((pathlib.Path() / "results" / "map" / country).with_suffix(".svg"), "w", newline = "", encoding = "utf-8") as file_out:
            for row in file_in:
                written = False
                for place in main[country]:
                    if row.find('id="{}"'.format(place)) > -1:
                        i = 0
                        while i < 5:
                            if main[country][place]["pcapita"] >= threshold[i + 1]:
                                i += 1
                            else:
                                break
                        main[country][place]["threshold met"] = threshold[i]
                        main[country][place]["fill"] = colour[i]
                        file_out.write(row.replace('id="{}"'.format(place), 'style="fill:{}"'.format(main[country][place]["fill"])))
                        written = True
                        break
                if written == False:
                    file_out.write(row)

    with open((pathlib.Path() / "results" / "legend" / country).with_suffix(".txt"), "w", newline = "", encoding = "utf-8") as file:
        file.write("Commons:\n")
        legend = ["|" + colour[0] + "|< " + "{:.2f}".format(threshold[1])]
        for i in range(1, 6):
            legend.append("|" + colour[i] + "|" + "{:.2f}".format(threshold[i]))
            if i == 5:
                legend[5] = legend[5] + "+"
        file.write("\n".join(legend))
        file.write("\n\nWikipedia:\n")
        for i in range(6):
            legend[i] = "{{legend" + legend[i] + "}}"
        file.write("\n".join(legend))

    cases = []
    for place in main[country]:
        cases.append(main[country][place]["cases"])
    print("{}: {} cases total in {} areas".format(country, sum(cases), len(cases)))
    print("Max: {}".format(max(values)))
