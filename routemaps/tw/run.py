# catalog: https://commons.wikimedia.org/wiki/BSicon/Catalogue
import argparse, json, csv, io, urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("-w", "--write", action = "store_const", const = True)
args = vars(parser.parse_args())

main = [
    "==Routemap==",
    "{{routemap",
    "| inline      = ",
    "| title       = ",
    "| title color = ",
    "| title bg    = ",
    "| collapsible = ",
    "| collapse    = ",
    "| navbar      = ",
    "| navbar pos  = ",
    "| navbar mini = ",
    "| legend      = ",
    "| legend alt  = ",
    "| float       = ",
    "| bg          = ",
    "| style       = ",
    "| top         = ",
    "| footnote    = ",
    "| text-width  = ",
    "| map = ",
    "~~km~~Station"
]

with open("Station-new.json", encoding = "utf-8") as file:
    sta = json.loads(file.read())["Stations"]

'''
with open("Station-new.json", "w", encoding = "utf-8") as file:
    file.write(json.dumps(data, indent = 2, ensure_ascii = False))
    quit()
'''

# major stations
maj = []
for station in sta:
    if station["StationClass"] in ["0", "1", "2"]:
        maj.append(station["StationID"])

with open("StationOfLine-new.json", encoding = "utf-8") as file:
    sol = json.loads(file.read())["StationOfLines"]

for line in sol:
    if line["LineID"] in ["SL"]:
        print(len(line["Stations"]))
        for station in line["Stations"]:
            seq = station["Sequence"]
            row = []
            dist = "{:.1f}".format(station["CumulativeDistance"])
            name = station["StationName"]["En"]
            if station["StationID"] in maj:
                row.append("BHF")
            else:
                row.append("HST")
            row.extend(["~~", dist, "~~", "{{stl|Taiwan Railways|", name, "}}"])
            main.append("".join(row))
        main.append("hCONTf")
main.append("}}")

if args["write"]  == True:
    with open("results.txt", "w", newline = "", encoding = "utf-8") as file:
        file.write("\n".join(main))
