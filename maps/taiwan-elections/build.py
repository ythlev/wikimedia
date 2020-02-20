import sys, math, csv

path = "./sources/中央選舉委員會_2020-01-21/"
el_type = "presidential"
el_year = "2020"

if len(sys.argv) == 5:
    with open("elections.csv", newline='', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if el_year == row[0] and el_type == row[1]:
                path = path + row[2] + "/" + row[3] + "/"
    winner, runner_up = sys.argv[3], sys.argv[4]
else:
    path = path + "2020總統立委/總統/"
    winner, runner_up = "3", "2"

# value for colouring
def val(num):
    if num > 0:
        return math.floor(math.log10(num)) + 1
    elif num == 0:
        return 0
    elif num < 0:
        return - math.floor(math.log10(-num)) - 1

fill = {}
with open("colouring/dpp-kmt.csv", newline='', encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        fill[row[0]] = row[1]

towns = {}
with open(path + "elctks.csv", newline='', encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        town_code = row[0] + row[1] + row[3]
        if row[4] == "0000" and row[0] != "00" and row[2] != "00":
            if row[6] == winner or row[6] == runner_up:
                if not town_code in towns:
                    towns[town_code] = {}
                towns[town_code][row[6]] = int(row[7])
                if len(towns[town_code]) == 2:
                    towns[town_code]["lead"] = towns[town_code][winner] - towns[town_code][runner_up]
                    towns[town_code]["val"] = val(towns[town_code]["lead"])
                    towns[town_code]["fill"] = fill[str(towns[town_code]["val"])]

# print(town["10013100"]["val"])
for row in towns:
    print(towns[row]["fill"])