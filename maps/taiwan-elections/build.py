import pathlib, sys, math, csv

source = pathlib.Path.cwd() / "sources" / "中央選舉委員會_2020-01-21"
el_type = "presidential"
el_year = "2016"
colouring = "dpp-kmt-5"

if len(sys.argv) == 5:
    with open("elections.csv", newline='', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if el_year == row[0] and el_type == row[1]:
                source = source / row[2] / row[3]
                colouring = row[4]
    winner, runner_up = sys.argv[3], sys.argv[4]
else:
    source = source / "2016總統立委" / "總統"
    winner, runner_up = "2", "1"

# value for colouring
def val(num):
    if num > 0:
        return math.floor(math.log10(num)) + 1
    elif num == 0:
        return 0
    elif num < 0:
        return - math.floor(math.log10(-num)) - 1

fill = {}
with open("colouring/%s.csv" % colouring, newline='', encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        fill[row[0]] = row[1]

towns = {}

def alt_file(s):
    file_name = source / (s + ".csv")
    if file_name.exists():
        return file_name
    else:
        return source / (s + "_P1.csv")


with open(source / alt_file("elctks"), newline='', encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        town_code = str( row[0] + row[1] + row[3])
        if row[4] == "0000" and row[0] != "00" and row[2] != "00":
            if row[6] == winner or row[6] == runner_up:
                if not town_code in towns:
                    towns[town_code] = {}
                towns[town_code][row[6]] = int(row[7])
                if len(towns[town_code]) == 2:
                    towns[town_code]["lead"] = towns[town_code][winner] - towns[town_code][runner_up]
                    towns[town_code]["val"] = val(towns[town_code]["lead"])
                    towns[town_code]["fill"] = fill[str(towns[town_code]["val"])]

with open("templates/" + el_type + ".svg", "r", newline='', encoding="utf-8") as file_in:
    with open("output/" + el_type + "/" + el_year + ".svg", "w", newline='', encoding="utf-8") as file_out:
        count = 0
        count2 = 0
        for row in file_in:
            code, fill = "", ""
            for town_code in towns:
                if row.find(town_code) > 0:
                    count += 1
                    code = town_code
                    fill = towns[town_code]["fill"]
            file_out.write(row.replace('id="%s"' % code, 'style="fill:%s"' % fill))
            count2 += 1
        print("Processed %d lines" % count2)
        print("%d areas coloured" % count)