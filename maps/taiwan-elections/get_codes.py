# This script fetches town codes for elections prior to 2016 and writes data to a file named "subdivsions.json"
import pathlib, csv, json

# sources directory
source = pathlib.Path() / "sources" / "中央選舉委員會_2020-01-21"

years = ["2012", "2008", "2004", "2000", "1996"]

# get directory for election and name of colouring scheme
folder = {}
with open("elections.csv", newline='', encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        for v in years:
            if v == row[0]:
                folder[v] = source / row[2] / row[3]
                break

# handle files with extra suffix
def alt_file(year):
    for v in ["_corrected", "20160523", "", "_P1"]:
        if (folder[year] / ("elbase" + v + ".csv")).exists():
            return folder[year] / ("elbase" + v + ".csv")
            break

main = {}
with open("alt names.csv", newline='', encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        main[str(row[0])] = {"names": [row[1]], "codes": {}}
        for i in range(2, 4):
            if not row[i] in main[str(row[0])]["names"] and row[i] != "":
                main[str(row[0])]["names"].append(row[i])

for year in years:
    counties, towns = {}, {}
    with open(alt_file(year), newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            row = [v.replace("'", "") for v in row]
            if row[4] == "0000" and row[0] != "00":
                if row[3] == "000":
                    counties[(row[0] + row[1])] = row[5]
                else:
                    towns[row[0] + row[1] + row[3]] = row[5]
    for k, v in towns.items():
        towns[k] = counties[k[0:5]] + v
    old_codes = dict([(v, k) for k, v in towns.items()])
    for k, v in main.items():
        for v2 in v["names"]:
            if v2 in old_codes:
                main[k]["codes"][year] = old_codes[v2]
                break

with open("subdivisions.json", "w", newline='', encoding="utf-8") as f:
        f.write(json.dumps(main, ensure_ascii = False, indent = 4))
