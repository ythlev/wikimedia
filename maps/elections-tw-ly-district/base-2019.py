import csv, json

village = {}
with open("village 2019.csv", newline = "", encoding = "utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        village[row["TOWNCODE"] + row["VILLCODE"][8:11]] = row["VILLCODE"]

elbase = []
with open("elbase-2020.csv", newline = "", encoding = "utf-8") as file:
    reader = csv.reader(file)
    for row in reader:
        if row[0] != "00" and row[2] != "00":
            if row[3] == "000":
                elbase.append({
                    "id": row[0] + row[1] + row[2],
                    "name": row[5]
                })
            elif row[4] != "0000":
                if row[4][0] != "A" and row[0] + row[1] + row[3] + row[4][1:4] in village:
                    elbase.append({
                        "VILLCODE": village[row[0] + row[1] + row[3] + row[4][1:4]],
                        "id": row[0] + row[1] + row[2]
                    })
                else:
                    print(row[0] + row[1] + row[3] + row[4][1:4], "not found")

with open("elbase-2020.json", "w", newline = "", encoding = "utf-8") as file:
    file.write(json.dumps(elbase, indent = 2))
