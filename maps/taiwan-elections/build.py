# 張嘉桓 製
import argparse, pathlib, csv, math, json

# parse arguments
parser = argparse.ArgumentParser(description = "This script generates an svg map for elections in Taiwan")
parser.add_argument("year", help = "Year of election", type = int)
parser.add_argument("type", help = "Type of election", nargs = "?", default = "presidential")
args = vars(parser.parse_args())

# sources directory
source = pathlib.Path() / "sources" / "中央選舉委員會_2020-01-21"

# get path for election and name of colours scheme
with open("elections.json", newline='', encoding="utf-8") as f:
    elections = json.loads(f.read())
    for v in elections[args["type"]][str(args["year"])]["path"]:
        source = source / v
    global colours
    colours = elections[args["type"]][str(args["year"])]["colours"]

# get colours scheme
fill = {}
fill["DPP-KMT"] = ["#08519c", "#3182bd", "#6baed6", "#bdd7e7", "#eff3ff", "white", "#edf8e9", "#bae4b3", "#74c476", "#31a354", "#006d2c"]
fill["KMT-DPP"] = fill["DPP-KMT"].copy()
fill["KMT-DPP"].reverse()
fill["DPP-IND"] = ["#252525", "#636363", "#969696", "#cccccc", "#f7f7f7"] + fill["DPP-KMT"][5:11]

# handle files with extra suffix
def alt_file(f):
    for v in ["_corrected", "20160523", "", "_P1"]:
        if (source / (f + v + ".csv")).exists():
            return source / (f + v + ".csv")
            break

# main dictionary
main = {}

# for converting value to colour key
def val(n):
    if n > 0:
        return math.floor(math.log10(n)) + 1
    elif n == 0:
        return 0
    elif n < 0:
        return - math.floor(math.log10(-n)) - 1

# get conversion table for old subdivision codes
if args["year"] < 2016:
    with open("subdivisions.json", newline='', encoding="utf-8") as f:
        subdivisions = json.loads(f.read())

# make function for old subdivision codes
def town(code):
    if args["year"] < 2016:
        for k, v in subdivisions.items():
            if str(args["year"]) in v["codes"].keys() and code == v["codes"][str(args["year"])]:
                return k
                break
    else:
        return code

# colour areas
elctks, national = {}, []
with open(alt_file("elctks"), newline='', encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        row = [v.replace("'", "") for v in row]
        if row[4] == "0000":
            elctks[row[0] + row[1] + row[3] + row[6][0]] = int(row[7])

# get winner and runner-up
for k, v in elctks.items():
    if k[0:2] == "00":
        national.append([k, v])
        national.sort(key = lambda col : col[1], reverse = True)
winner, runner_up = national[0][0][-1], national[1][0][-1]

for k, v in elctks.items():
    if k[0:2] != "00" and k[5:8] != "000" and (k[-1] == winner or k[-1] == runner_up):
        code = k[0:8]
        if not town(code) in main:
            main[town(code)] = {}
        main[town(code)][k[-1]] = int(v)
        if len(main[town(code)]) == 2:
            main[town(code)]["lead"] = main[town(code)][winner] - main[town(code)][runner_up]
            main[town(code)]["val"] = val(main[town(code)]["lead"])
            main[town(code)]["fill"] = fill[colours][main[town(code)]["val"] + 5]

# template map
def map():
    if args["year"] < 2004:
        return "presidential (1990–2003).svg"
    else:
        return "presidential.svg"

# colour template map and output map for election
with open(pathlib.Path() / "templates" / map(), "r", newline='', encoding="utf-8") as f_in:
    with open(pathlib.Path() / "output" / args["type"] / (str(args["year"]) + ".svg"), "w", newline='', encoding="utf-8") as f_out:
        a, b = 0, 0
        for row in f_in:
            written = False
            for code in main:
                try:
                    if code != None and row.find(code) > 0:
                        f_out.write(row.replace('id="%s"' % code, 'style="fill:%s"' % main[code]["fill"]))
                        a += 1
                        written = True
                        break
                except:
                    quit()
            if written == False:
                f_out.write(row)
        print("Coloured %d areas" % a)
