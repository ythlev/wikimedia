import argparse, json, csv, math, statistics

parser = argparse.ArgumentParser()
parser.add_argument("year")
args = vars(parser.parse_args())

with open("data-verified.json", newline = "", encoding = "utf-8") as file:
    data = json.loads(file.read())[args["year"]]
    meta = data["meta"]
    towns = data["towns"]

colours = {
    "dpp": ['#e5f5e0','#a1d99b','#31a354'],
    "kmt": ['#deebf7','#9ecae1','#3182bd'],
    "ind": ['#f0f0f0','#bdbdbd','#636363']
}

colours[meta["runner-up party"]].reverse()
colour = colours[meta["runner-up party"]] + colours[meta["winner party"]]

def tmp():
    if int(args["year"]) < 2004:
        return "template (1996–2000).svg"
    else:
        return "template.svg"

with open(tmp(), newline = "", encoding = "utf-8") as file_in:
    with open(args["year"] + ".svg", "w", newline = "", encoding = "utf-8") as file_out:
        for row in file_in:
            if row.find('id="_') > -1:
                written = False
                for key, value in towns.items():
                    if row.find(key) > -1:
                        i = 0
                        while i < 5:
                            if value["diff"] >= meta["thresholds"][i + 1]:
                                i += 1
                            else:
                                break
                        file_out.write(row.replace('id="_{}"'.format(key), 'fill="{}"'.format(colour[i])))
                        written = True
                        break
                if written == False:
                    file_out.write(row)
            else:
                file_out.write(row)
