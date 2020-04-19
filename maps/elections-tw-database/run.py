import argparse, csv, json
from datetime import datetime, date

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--election")
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

if args["election"] != None:
    d = {
        "name": args["election"],
        "date": str(date.fromisoformat(args["date"]))
    }
    if d not in el["elections"]:
        el["elections"].append(d)
    el["elections"].sort(key = lambda d : d["date"])

if args["file"] != None:
    pass

with open("el-preview.json", "w", newline = "", encoding = "utf-8") as file:
    file.write(json.dumps(el, indent = 2, ensure_ascii = False))
