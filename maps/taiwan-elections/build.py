import argparse, pathlib, sys, math, csv

# parse arguments
parser = argparse.ArgumentParser(description = "This script generates an svg map for elections in Taiwan")
parser.add_argument("type", help = "Type of election", default = "presidential")
parser.add_argument("year", help = "Year of election")
parser.add_argument("winner", help = "Sequence number of the winner")
parser.add_argument("runner-up", help = "Sequence number of the runner-up")
args = vars(parser.parse_args())
parser.print_help()

# sources directory
source = pathlib.Path.cwd() / "sources" / "中央選舉委員會_2020-01-21"

# get directory for election and name of colouring scheme
with open("elections.csv", newline='', encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        if args["year"] == row[0] and args["type"] == row[1]:
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
def alt_file(s):
    file_name = source / (s + ".csv")
    if file_name.exists():
        return file_name
    else:
        return source / (s + "_P1.csv")

# main dictionary
towns = {}

# for converting value to colour key
def val(n):
    if n > 0:
        return math.floor(math.log10(n)) + 1
    elif n == 0:
        return 0
    elif n < 0:
        return - math.floor(math.log10(-n)) - 1

# colour areas
with open(source / alt_file("elctks"), newline='', encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        town_code = str( row[0] + row[1] + row[3])
        if row[4] == "0000" and row[0] != "00" and row[2] != "00":
            if row[6] == args["winner"] or row[6] == args["runner-up"]:
                if not town_code in towns:
                    towns[town_code] = {}
                towns[town_code][row[6]] = int(row[7])
                if len(towns[town_code]) == 2:
                    towns[town_code]["lead"] = towns[town_code][args["winner"]] - towns[town_code][args["runner-up"]]
                    towns[town_code]["val"] = val(towns[town_code]["lead"])
                    towns[town_code]["fill"] = fill[str(towns[town_code]["val"])]

# colour template map and output map for election
with open(pathlib.Path.cwd() / "templates" / (args["type"] + ".svg"), "r", newline='', encoding="utf-8") as f_in:
    with open(pathlib.Path.cwd() / "output" / args["type"] / (args["year"] + ".svg"), "w", newline='', encoding="utf-8") as f_out:
        a, b = 0, 0
        for row in f_in:
            code, fill = "", ""
            for town_code in towns:
                if row.find(town_code) > 0:
                    a += 1
                    code = town_code
                    fill = towns[town_code]["fill"]
            f_out.write(row.replace('id="%s"' % code, 'style="fill:%s"' % fill))
            b += 1
        print("Processed %d lines" % b)
        print("Coloured %d areas" % a)
