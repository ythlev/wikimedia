import argparse, csv, json
from datetime import datetime, date

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--type")
parser.add_argument("-d", "--date")
parser.add_argument("-f", "--file")
parser.add_argument("-c", "--commit", action = "store_const", const = True)
args = vars(parser.parse_args())
main = {}

if args["commit"] == True:
    import os
    os.replace("el-preview.json", "el.json")
    quit()

with open("el.json", newline = "", encoding = "utf-8") as file:
    el = json.loads(file.read())

el["lastUpdatedAt"] = datetime.now().isoformat()

if args["type"] != None and args["date"] != None:
    for election in el["elections"][args["type"]]:
        if "date" in election and election["date"] == args["date"]:
            el["elections"][args["type"]].remove(election)
            break

    def init(l, d, nm = None):
        for i in range(len(l)):
            if i > 0:
                l[i] = l[i - 1] + l[i]
            if l[i] not in d:
                if i == len(l) - 1:
                    d[l[i]] = {"nm": nm}
                else:
                    d[l[i]] = {}
            d = d[l[i]]

    areas = {}
    if args["file"] == "base":
        with open("elbase.csv", newline = "", encoding = "utf-8") as file:
            for row in csv.reader(file):
                row = [s.lstrip("'") for s in row]
                if row[0] != "00" and row[0] + row[1] != "10000":
                    if row[2] == "00" or row[3] == "000":
                        init([row[0] + row[1]], areas, row[5])
                        if row[4] == "0000":
                            init([row[0] + row[1], row[3]], areas, row[5])
                        else:
                            init([row[0] + row[1], row[3], row[4]], areas, row[5])

    d = {
        "date": args["date"],
        "areas": areas
    }
    el["elections"][args["type"]].append(d)
    el["elections"][args["type"]].sort(reverse = True, key = lambda d : d["date"])

with open("el-preview.json", "w", newline = "", encoding = "utf-8") as file:
    file.write(json.dumps(el, indent = 2, ensure_ascii = False))
