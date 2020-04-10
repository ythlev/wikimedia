import argparse, json, csv, io, urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("-w", "--write", action = "store_const", const = True)
args = vars(parser.parse_args())

with open("station.json", encoding = "utf-8") as file:
    data = json.loads(file.read())["Stations"]

with open("station-od.json", encoding = "utf-8") as file:
    od = json.loads(file.read())

with open("station-o-line.json", encoding = "utf-8") as file:
    ol = json.loads(file.read())["StationOfLines"]

with open("traf-2019.json", encoding = "utf-8-sig") as file:
    traf = json.loads(file.read())

with open("traf-2018.csv", encoding = "utf-8-sig") as file:
    reader = csv.reader(file)
    traf18 = []
    for row in reader:
        traf18.append({
            "name": row[0],
            "value": row[1] + row[2]
        })

'''
with open("station-od.json", "w", encoding = "utf-8") as file:
    file.write(json.dumps(data, indent = 2, ensure_ascii = False))
    quit()
'''

main = []

sta = []
for line in ol:
    if line["LineID"] == "WL":
        left = ""
        for station in line["Stations"]:
            addr, borough, coord, cls, url = "", "", "", "", ""
            ps, psdelta = 0, 0
            sta.append({"name": station["StationName"]["En"]})
            for station2 in data:
                if station2["StationID"] == station["StationID"]:
                    url = "[" + station2["StationURL"] + " tip.railway.gov.tw]"
                    coord = format(station2["StationPosition"]["PositionLat"]) + "|" + format(station2["StationPosition"]["PositionLon"])
                    cls = station2["StationClass"]
                    break
            for station2 in od:
                if station2["stationCode"] == station["StationID"]:
                    if station2["stationAddrEn"] == "  ":
                        break
                    addr = station2["stationAddrEn"].replace(".", "")
                    addr = addr.replace(",", "")
                    addr = addr.replace("No ", "")
                    addr = addr.replace(" Dist", " District")
                    addr = addr.replace("(Station Building) ", "")
                    for word in [" Rd", " St", " Blvd"]:
                        if addr.find(word) > -1:
                            addr_list = addr.split(word)
                            addr_list[0] = addr_list[0] + word
                            addr = addr_list[0]
                            borough = addr_list[1].lstrip(" ")
                            break
                    for word in [" Township", " District", " City"]:
                        if borough.find(word) > -1:
                            borough_list = borough.split(word)
                            borough_list[0] += word
                            borough_list[1] = borough_list[1].lstrip(" ")
                            break
                    borough = "[[" + borough_list[0] + "]], [[" + borough_list[1] + "]]"
                    break
            for station2 in traf:
                if station["StationName"]["Zh_tw"] == station2["站別"]:
                    ps = (station2["上車人數"] + station2["下車人數"])
                    break
            for station2 in traf18:
                if station["StationName"]["Zh_tw"] == station2["name"]:
                    psdelta = 100 * ps / int(station2["value"]) - 100
                    break
            main.extend([
                "{{Infobox station",
                "| name = " + station["StationName"]["En"],
                "| native_name = " + station["StationName"]["Zh_tw"],
                "| native_name_lang = zh-Hant-TW",
                "| symbol_location = tw",
                "| symbol = tra",
                "| type = [[Taiwan Railways Administration|TRA]] railway station",
                "| caption = Station exterior",
                "| address = " + addr,
                "| borough = " + borough,
                "| country = Taiwan",
                "| coord = {{coord|" + coord + "|type:railwaystation|display=inline,title}}",
                "| distance = " + format(station["CumulativeDistance"]) + "&nbsp;km to {{stl|Taiwan Railways|Keelung}}",
                "| connections = {{Plainlist|",
                "* [[Public transport bus service|Local bus]]",
                "* [[Intercity bus service|Coach]]",
                "}}",
                "| structure = Ground level",
                "| code = " + station["StationID"],
                "| classification = " + cls,
                "| website = " + url,
                "| passengers = " + "{:,}".format(ps),
                "| pass_percent = " + "{:,.2f}".format(psdelta),
                "| pass_year = 2019",
                "| services = {{adjacent stations|Taiwan Railways|line=Western Trunk|left=" + left + "|right=}}"
                "| map_type = Taiwan",
                "}}"
            ])
            left = station["StationName"]["En"]

print(main)
quit()

with open("counter.json", encoding = "utf-8") as file:
    count = json.loads(file.read())[0]
    print(sta[count])
    count += 1
    with open("counter.json", "w", encoding = "utf-8") as file:
        file.write(json.dumps([count], indent = 2, ensure_ascii = False))
