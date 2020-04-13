import json

with open("routemap/Station-new.json", newline = "", encoding = "utf-8") as file:
    data = json.loads(file.read())["Stations"]


with open("map.svg", newline = "", encoding = "utf-8") as file_in:
    with open("map-new.svg", "w", newline = "", encoding = "utf-8") as file_out:
        for row in file_in:
            if row.find('circle') > -1:
                for station in data:
                    if row.find(station["StationName"]["Zh_tw"]) > -1 and station["StationClass"] in ["0", "1", "2"]:
                        file_out.write(row.replace('<title>{}</title>'.format(station["StationName"]["Zh_tw"]), '<title>{} {}</title>'.format(station["StationName"]["Zh_tw"], station["StationName"]["En"])))
                        break
            else:
                file_out.write(row)
