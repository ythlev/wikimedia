import argparse, pathlib, csv, math, hashlib

# parse arguments
parser = argparse.ArgumentParser(description = "This script generates an svg map for elections in Taiwan")
parser.add_argument("year", help = "Year of election", type = int)
parser.add_argument("type", help = "Type of election", nargs = "?", default = "presidential")
args = vars(parser.parse_args())

# sources directory
source = pathlib.Path.cwd() / "sources" / "中央選舉委員會_2020-01-21"

# get directory for election and name of colouring scheme
with open("elections.csv", newline='', encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        if str(args["year"]) == row[0] and args["type"] == row[1]:
            source = source / row[2] / row[3]
            global colouring
            colouring = row[4]

# get colouring scheme
fill = {}
with open("colouring/%s.csv" % colouring, newline='', encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        fill[row[0]] = row[1]

# handle files with extra suffix
def alt_file(f):
    for x in ["20160523", "_P1", ""]:
        if (source / (f + x + ".csv")).exists():
            return source / (f + x + ".csv")
            break

# main dictionary
town_data = {}

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
    conv, old_codes = {}, {}
    with open(alt_file("elbase"), newline='', encoding="utf-8") as f:
        counties, towns = {}, {}
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

    with open("subdivisions.csv", newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            for i in range(1, len(row)):
                if row[i] in old_codes:
                    conv[old_codes.get(row[i])] = row[0]

# make function for old subdivision codes
def town(code):
    if args["year"] < 2016:
        try:
            return conv[code]
        except KeyError:
            print(code + " not found")
    else:
        return code

# colour areas
elctks, national = {}, []
with open(alt_file("elctks"), newline='', encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        row = [v.replace("'", "") for v in row]
        if row[4] == "0000":
            elctks[row[0] + row[1] + row[3] + row[6]] = int(row[7])

# get winner and runner-up
for k, v in elctks.items():
    if k[0:2] == "00":
        national.append([k, v])
        national.sort(key = lambda col : col[1], reverse = True)
winner, runner_up = national[0][0][-1], national[1][0][-1]

for k, v in elctks.items():
    if k[0:2] != "00" and k[5:8] != "000" and (k[-1] == winner or k[-1] == runner_up):
        code = k[0:8]
        if not town(code) in town_data:
            town_data[town(code)] = {}
        town_data[town(code)][k[-1]] = int(v)
        if len(town_data[town(code)]) == 2:
            town_data[town(code)]["lead"] = town_data[town(code)][winner] - town_data[town(code)][runner_up]
            town_data[town(code)]["val"] = val(town_data[town(code)]["lead"])
            town_data[town(code)]["fill"] = fill[str(town_data[town(code)]["val"])]

# colour template map and output map for election
with open(pathlib.Path.cwd() / "templates" / (args["type"] + ".svg"), "r", newline='', encoding="utf-8") as f_in:
    with open(pathlib.Path.cwd() / "output" / args["type"] / (str(args["year"]) + ".svg"), "w", newline='', encoding="utf-8") as f_out:
        a, b = 0, 0
        for row in f_in:
            written = False
            for code in town_data:
                if row.find(code) > 0:
                    f_out.write(row.replace('id="%s"' % code, 'style="fill:%s"' % town_data[code]["fill"]))
                    a += 1
                    b += 1
                    written = True
                    break
            if written == False:
                f_out.write(row)
                b += 1
        print("Processed %d lines" % b)
        print("Coloured %d areas" % a)
