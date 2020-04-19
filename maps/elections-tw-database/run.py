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

if args["type"] != None:
    if args["type"] == "general":
        for type in ["presidential", "ly district", "ly party"]:
            if args["date"] not in el["dates"][type]:
                el["dates"][type].append(args["date"])
                el["dates"][type].sort(reverse = True)
    elif args["date"] not in el["dates"][args["type"]]:
        el["dates"][args["type"]].append(args["date"])
        el["dates"][args["type"]].sort(reverse = True)

    

if args["file"] != None:
    pass

with open("el-preview.json", "w", newline = "", encoding = "utf-8") as file:
    file.write(json.dumps(el, indent = 2, ensure_ascii = False))
