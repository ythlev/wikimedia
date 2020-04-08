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
    if line["LineID"] in ["WL"]:
        for station in line["Stations"]:
            seq = station["Sequence"]
            if seq == 13:
                continue
            row = []

            dist = "{:.1f}".format(station["CumulativeDistance"])
            name = station["StationName"]["En"]

            if seq >= 38 and seq <= 59:
                row.append("STR\\")
            if seq >= 9 and seq <= 15 or seq >= 103 and seq <= 112:
                row.append("t")
            elif seq >= 47 and seq <= 56 or name == "Pingtung":
                row.append("h")

            if name in ["Nangang"]:
                row.append("BHFag")
            elif name in ["Zuoying"]:
                row.append("HSTag")
            elif name in ["Banqiao", "Fengshan"]:
                row.append("BHFef")
            elif name in ["Fengyuan", "Pingtung"]:
                row.append("BHFa")
            elif name in ["Daqing"]:
                row.append("BHFe")
            elif seq == 1:
                row.append("KBHFa")
            elif station["StationID"] in maj:
                row.append("BHF")
            else:
                row.append("HST")
            row.extend(["~~", dist, "~~", "{{stl|Taiwan Railways|", name, "}}"])
            main.append("".join(row))
            if name in ["Sankeng", "Zhubei", "Jiabei"]:
                main.append("\\ABZg+l\\CONTfq~~{{routemapRoute|r=r|{{lnl|Taiwan Railways|}}}}")
            elif name in ["Ershui", "Zhongzhou"]:
                main.append("\\ABZgl\\CONTfq~~{{routemapRoute|r=r|{{lnl|Taiwan Railways|}}}}")
            elif name in ["Zhunan"]:
                main.append("bSHI2lr")
            elif name == "Chenggong":
                main.append("bvvWSLglr")
        main.append("hCONTf")
    if line["LineID"] in ["WL-C"]:
        for station in line["Stations"]:
            row = []
            dist = "{:.1f}".format(station["CumulativeDistance"])
            name = station["StationName"]["En"]
            row.extend(["{:.1f}".format(station["CumulativeDistance"] + 125.4), "{{stl|Taiwan Railways|", name, "}}", "~~", dist, "! !"])
            main.append("".join(row))
            if station in maj:
                print(name)

main.append("}}")

if args["write"]  == True:
    with open("results.txt", "w", newline = "", encoding = "utf-8") as file:
        file.write("\n".join(main))
