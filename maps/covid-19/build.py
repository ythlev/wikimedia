# Created by Chang Chia-huan
import pathlib, json, csv, io, urllib.request, math

main = {
    "taiwan": {},
    # "uk": {},
    "japan": {},
    "us": {}
}
unit, outliers = {}, {}
colours = ["#fee5d9","#fcbba1","#fc9272","#fb6a4a","#de2d26","#a50f15"]

for country in main:
    with open(pathlib.Path() / country / "places.csv", newline = "", encoding = "utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            main[country][row["key"]] = {
                "cases": int(row["cases"]),
                "population": int(row["population"].replace(",", ""))
            }

unit["taiwan"] = 1000000
with urllib.request.urlopen("https://od.cdc.gov.tw/eic/Weekly_Age_County_Gender_19CoV.json") as response:
    data = json.loads(response.read())
    for row in data:
        main["taiwan"][row["縣市"]]["cases"] += int(row["確定病例數"])
'''
unit["uk"] = 100000
with urllib.request.urlopen("https://www.arcgis.com/sharing/rest/content/items/b684319181f94875a6879bbc833ca3a6/data") as response:
    reader = csv.DictReader(io.TextIOWrapper(response, encoding = 'utf-8'), delimiter=',')
    for row in reader:
        if row["GSS_CD"] in main["uk"]:
            main["uk"][row["GSS_CD"]]["cases"] = int(row["TotalCases"])
'''
unit["japan"] = 1000000
with urllib.request.urlopen("https://dl.dropboxusercontent.com/s/6mztoeb6xf78g5w/COVID-19.csv") as response:
    reader = csv.DictReader(io.TextIOWrapper(response, encoding = 'utf-8'), delimiter=',')
    for row in reader:
        if row["Hospital Pref"] != "Unknown":
            if row["Hospital Pref"] in ["Nigata", "Niigata "]:
                row["Hospital Pref"] = "Niigata"
            main["japan"][row["Hospital Pref"]]["cases"] += 1

unit["us"] = 1000000
with urllib.request.urlopen("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv") as response:
    reader = csv.reader(io.TextIOWrapper(response, encoding = 'utf-8'), delimiter=',')
    for row in reader:
        if row[0] == "Province/State" or row[1] != "US":
            continue
        elif row[0] in main["us"]:
            main["us"][row[0]]["cases"] = int(row[-1])

for country in main:
    values = []
    for place in main[country]:
        main[country][place]["pcapita"] = round(main[country][place]["cases"] / main[country][place]["population"] * unit[country], 2)
        values.append(main[country][place]["pcapita"])

    step = math.sqrt(max(values)) / 6

    thresholds = [0, 0, 0, 0, 0, 0]
    for i in range(6):
        thresholds[i] = round(math.pow(step * i, 2), 2)

    with open(pathlib.Path() / country / "template.svg", "r", newline = "", encoding = "utf-8") as file_in:
        with open(pathlib.Path() / country / "per-capita.svg", "w", newline = "", encoding = "utf-8") as file_out:
            for row in file_in:
                written = False
                for place in main[country]:
                    if row.find('id="{}"'.format(place)) > -1:
                        i = 0
                        while i < 5:
                            if main[country][place]["pcapita"] >= thresholds[i + 1]:
                                i += 1
                            else:
                                break
                        main[country][place]["threshold met"] = thresholds[i]
                        main[country][place]["fill"] = colours[i]
                        file_out.write(row.replace('id="{}"'.format(place), 'style="fill:{}"'.format(main[country][place]["fill"])))
                        written = True
                        break
                if written == False:
                    file_out.write(row)

    cases = []
    for place in main[country]:
        cases.append(main[country][place]["cases"])
    print("{}: {} cases total in {} areas".format(country.upper(), sum(cases), len(cases)))
    print("Thresholds: {} Max: {}".format(thresholds, max(values)))
