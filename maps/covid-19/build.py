# Created by Chang Chia-huan
import pathlib, json, csv, io, urllib.request, math, statistics

main = {
    "Taiwan": {},
    # "uk": {},
    "Japan": {},
    "US": {}
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

unit["Taiwan"] = 1000000
with urllib.request.urlopen("https://od.cdc.gov.tw/eic/Weekly_Age_County_Gender_19CoV.json") as response:
    data = json.loads(response.read())
    for row in data:
        main["Taiwan"][row["縣市"]]["cases"] += int(row["確定病例數"])
'''
unit["uk"] = 100000
with urllib.request.urlopen("https://www.arcgis.com/sharing/rest/content/items/b684319181f94875a6879bbc833ca3a6/data") as response:
    reader = csv.DictReader(io.TextIOWrapper(response, encoding = 'utf-8'), delimiter=',')
    for row in reader:
        if row["GSS_CD"] in main["uk"]:
            main["uk"][row["GSS_CD"]]["cases"] = int(row["TotalCases"])
'''
unit["Japan"] = 1000000
with urllib.request.urlopen("https://services6.arcgis.com/5jNaHNYe2AnnqRnS/arcgis/rest/services/COVID19_Japan/FeatureServer/0/query?where=ObjectId%3E0&outFields=*&f=pjson") as response:
    data = json.loads(response.read())
    for row in data["features"]:
        if row["attributes"]["Hospital_Pref"] != "Unknown":
            main["Japan"][row["attributes"]["Hospital_Pref"]]["cases"] += 1

unit["US"] = 1000000
with urllib.request.urlopen("https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/Coronavirus_2019_nCoV_Cases/FeatureServer/1/query?where=OBJECTID%3E0&outFields=*&f=pjson") as response:
    data = json.loads(response.read())
    for row in data["features"]:
        if row["attributes"]["Country_Region"] == "US" and row["attributes"]["Province_State"] in main["US"]:
            main["US"][row["attributes"]["Province_State"]]["cases"] = int(row["attributes"]["Confirmed"])

for country in main:
    values = []
    for place in main[country]:
        main[country][place]["pcapita"] = round(main[country][place]["cases"] / main[country][place]["population"] * unit[country], 2)
        values.append(main[country][place]["pcapita"])

    step = math.sqrt(statistics.median(values)) / 2.5

    threshold = [0, 0, 0, 0, 0, 0]
    for i in range(6):
        threshold[i] = round(math.pow(step * i, 2), 2)

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
        legend = ["|" + colour[0] + "|< " + str(threshold[1])]
        for i in range(1, 6):
            legend.append("|" + colour[i] + "|" + str(threshold[i]))
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
