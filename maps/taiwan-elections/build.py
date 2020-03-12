# 張嘉桓 製
import argparse, pathlib, csv, math, json

# parse arguments
parser = argparse.ArgumentParser(description = "This script generates an svg map for elections in Taiwan")
parser.add_argument("year", help = "Year of election", type = int)
parser.add_argument(
    "-p", "--presidential",
    help = "Type of election is presidential",
    action = "store_const",
    const = "presidential",
    dest = "type",
    default = "presidential"
)
parser.add_argument("-l", "--legislative", help = "Type of election is legislative", action = "store_const", const = "legislative", dest = "type")
parser.add_argument("--print", help = "Print element")
args = vars(parser.parse_args())

# sources directory
source = pathlib.Path() / "sources" / "中央選舉委員會_2020-01-21"

# get colours and path for election
with open("data.json", newline='', encoding="utf-8") as file:
    data = json.loads(file.read())
    colour = data["party colours"]
    for party in colour:
        colour[party].insert(0, "white")
    for name in data["elections"][args["type"]][str(args["year"])]:
        source = source / name

# handle files with extra suffix
def get_file(file):
    for suffix in ["_corrected", "20160523", "", "_P1", "_T4"]:
        if (source / (file + suffix + ".csv")).exists():
            return source / (file + suffix + ".csv")
            break

# get conversion table for old subdivision codes
if args["year"] < 2016:
    with open("old_codes.json", newline='', encoding="utf-8") as file:
        old_codes = json.loads(file.read())

# make function for old subdivision codes
def get_town(code):
    if args["year"] < 2016 and code != "00000000":
        return old_codes[str(args["year"])][code]
    else:
        return code

# get party codes
party = {}
with open(get_file("elcand"), newline='', encoding="utf-8") as file:
    reader = csv.reader(file)
    for row in reader:
        row = [string.replace("'", "") for string in row]
        party[str(row[5].zfill(2))] = str(row[7])

# get vote figures
main = {}
with open(get_file("elctks"), newline='', encoding="utf-8") as file:
    reader = csv.reader(file)
    for row in reader:
        row = [string.replace("'", "") for string in row]
        if row[3] != "000" and row[4] == "0000":
            if args["type"] == "legislative" and row[0] != "00" or args["type"] == "presidential":
                town = get_town(row[0] + row[1] + row[3])
                if args["year"] == 1996:
                    cand = row[6][0].zfill(2)
                else:
                    cand = row[6].zfill(2)
                votes = int(row[7])
                if town not in main:
                    main[town] = {}
                main[town][party[cand]] = votes

# get winner and runner_up
if args["type"] == "presidential":
    votes_list = []
    for cand, votes in main["00000000"].items():
        votes_list.append(votes)
    votes_list.sort(reverse = True)
    for cand, votes in main["00000000"].items():
        if votes == votes_list[0]:
            winner = cand
        elif votes == votes_list[1]:
            runner_up = cand
    del main["00000000"]
    for cands in main.values():
        tbd = []
        for cand in cands:
            if cand != winner and cand != runner_up:
                tbd.append(cand)
        for cand in tbd:
            del cands[cand]
elif args["type"] == "legislative":
    for town, cands in main.items():
        total = 0
        for cand, votes in cands.items():
            total += votes
        for cand, votes in cands.items():
            main[town][cand] = votes / total * 100

# function to determine colour
def val(n):
    if args["type"] == "presidential":
        if n > 0:
            return math.floor(math.log10(n)) + 1
        else:
            return 0
    elif args["type"] == "legislative":
        if n > 0:
            return int(n // 20 + 1)
        else:
            return 0

# calculate colour values
for cands in main.values():
    votes_list = []
    for cand, votes in cands.items():
        votes_list.append(votes)
    votes_list.sort(reverse = True)
    for cand, votes in cands.items():
        if votes == votes_list[0]:
            first = cand
        elif votes == votes_list[1]:
            second = cand
    if args["type"] == "presidential":
        cands["fill"] = colour[first][val(cands[first] - cands[second])]
    elif args["type"] == "legislative":
        cands["fill"] = colour[first][val(cands[first])]

# template map
def map():
    if args["year"] < 2004:
        return "presidential (1996–2000).svg"
    else:
        return "presidential.svg"

# colour template map and output map for election
if args["print"] == None:
    with open(pathlib.Path() / "templates" / map(), "r", newline='', encoding="utf-8") as file_in:
        with open(pathlib.Path() / "output" / args["type"] / (str(args["year"]) + ".svg"), "w", newline='', encoding="utf-8") as file_out:
            a, b = 0, 0
            for row in file_in:
                written = False
                for town in main:
                    if town != None and row.find(town) > 0:
                        file_out.write(row.replace('id="%s"' % town, 'style="fill:%s"' % main[town]["fill"]))
                        a += 1
                        written = True
                        break
                if written == False:
                    file_out.write(row)
            print("Coloured %d areas" % a)

if args["print"] == "main":
    for k, v in main.items():
        print(k, v)
