# Created by Chang Chia-huan
import argparse, pathlib, json, csv, io, urllib.request, math, statistics

parser = argparse.ArgumentParser(description = "This script generates an svg maps for the COVID-19 outbreak for select countries")
parser.add_argument("-c", "--country", help = "Name of country to generate; by default, a map for each country is generated")
args = vars(parser.parse_args())

if args["country"] != None:
    main = {args["country"]:{}}
else:
    main = {
        "Canada": {},
        "US": {},
        "Japan": {},
        # "France": {},
        "Germany": {},
        "UK": {},
        "Taiwan": {}
    }

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
    url = query + "&outFields=*" + "&returnGeometry=false" + "&f=pjson"
    with urllib.request.urlopen(url) as response:
        for entry in json.loads(response.read())["features"]:
            attrs.append(entry["attributes"])

if "US" in main:
    arc_gis("https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/Coronavirus_2019_nCoV_Cases/FeatureServer/1/query?where=ObjectID%3E0")
    for place in attrs:
        if place["Country_Region"] == "US" and place["Province_State"] in main["US"]:
            main["US"][place["Province_State"]]["cases"] = int(place["Confirmed"])

if "Canada" in main:
    arc_gis("https://services9.arcgis.com/pJENMVYPQqZZe20v/arcgis/rest/services/HealthRegionTotals/FeatureServer/0/query?where=ObjectID%3E0")
    for place in attrs:
        main["Canada"][place["HR_UID"]]["cases"] = int(place["CaseCount"])

if "Japan" in main:
    arc_gis("https://services6.arcgis.com/5jNaHNYe2AnnqRnS/arcgis/rest/services/COVID19_Japan/FeatureServer/0/query?where=ObjectID%3E0")
    for place in attrs:
        if place["Hospital_Pref"] != "Unknown":
            main["Japan"][place["Hospital_Pref"]]["cases"] += 1

if "France" in main:
    arc_gis("https://services1.arcgis.com/5PzxEwuu4GtMhqQ6/arcgis/rest/services/Regions_DT_Project_Vue/FeatureServer/0/query?where=ObjectID%3E0")
    for place in attrs:
        main["France"][place["nom"]]["cases"] = int(place["nb_cas"])

if "Germany" in main:
    arc_gis("https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/Kreisgrenzen_2018_mit_Einwohnerzahl/FeatureServer/0/query?where=ObjectID%3E0")
    for place in attrs:
        main["Germany"][place["RS"]]["cases"] = int(place["Fallzahlen"])

if "UK" in main:
    arc_gis("https://services1.arcgis.com/0IrmI40n5ZYxTUrV/arcgis/rest/services/NHSR_Cases/FeatureServer/0/query?where=FID%3E0")
    for place in attrs:
        main["UK"][place["GSS_CD"]]["cases"] = int(place["TotalCases"])
    arc_gis("https://services1.arcgis.com/0IrmI40n5ZYxTUrV/arcgis/rest/services/UK_Countries_cases/FeatureServer/0/query?where=FID%3E0")
    for place in attrs:
        if place["GSS_CD"] in main["UK"]:
            main["UK"][place["GSS_CD"]]["cases"] = int(place["TotalCases"])

if "Taiwan" in main:
    with urllib.request.urlopen("https://od.cdc.gov.tw/eic/Weekly_Age_County_Gender_19CoV.json") as response:
        data = json.loads(response.read())
        for row in data:
            main["Taiwan"][row["縣市"]]["cases"] += int(row["確定病例數"])

colour = ["#fee5d9","#fcbba1","#fc9272","#fb6a4a","#de2d26","#a50f15"]

for country in main:
    values = []
    for place in main[country]:
        main[country][place]["pcapita"] = main[country][place]["cases"] / main[country][place]["population"] * 1000000
        values.append(main[country][place]["pcapita"])
        
    step = math.sqrt(statistics.mean(values)) / 2.5

    threshold = [0, 0, 0, 0, 0, 0]
    for i in range(6):
        threshold[i] = math.pow(i * step, 2)

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
        if country == "UK":
            format = "{:.0f}"
        else:
            format = "{:.2f}"
        legend = ["|" + colour[0] + "|< " + format.format(threshold[1])]
        for i in range(1, 6):
            legend.append("|" + colour[i] + "|" + format.format(threshold[i]))
            if i == 5:
                legend[5] = legend[5] + "+"
        file.write("\n".join(legend))
        file.write("\n\nWikipedia:\n")
        for i in range(6):
            legend[i] = "{{legend" + legend[i] + "}}"
        legend.append("\nMax value: " + str(max(values)))
        file.write("\n".join(legend))

    cases = []
    for place in main[country]:
        cases.append(main[country][place]["cases"])
    print("{}: {} cases total in {} areas".format(country, sum(cases), len(cases)))
