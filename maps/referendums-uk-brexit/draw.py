import csv, math, statistics, json

main, values = {}, [-18499]

with open("EU-referendum-result-data.csv", newline = "", encoding = "utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        main[row["Area_Code"]] = int(row["Leave"]) - int(row["Remain"])
        values.append(abs(main[row["Area_Code"]]))

ni = {}
with open("ni.csv", newline = "", encoding = "utf-8") as file:
    reader = csv.reader(file)
    for row in reader:
        values.append(abs(int(row[1])))
        ni[row[0]] = int(row[1])

step = math.sqrt(statistics.mean(values)) / 2

threshold = [0, 0, 0]
for i in range(1, 3):
    threshold[i] = round(math.pow(i * step, 2))

threshold = [0, -threshold[2], -threshold[1]] + threshold

colour = ['#8c510a','#d8b365','#f6e8c3','#c7eae5','#5ab4ac','#01665e']

with open("ni.json", "w", newline = "", encoding = "utf-8") as file:
    for k in ni:
        i = 0
        while i < 5:
            if ni[k] >= threshold[i + 1]:
                i += 1
            else:
                break
        ni[k] = colour[i]
    file.write(json.dumps(ni, indent = 2))

with open("template.svg", newline = "", encoding = "utf-8") as file_in:
    with open("brexit.svg", "w", newline = "", encoding = "utf-8") as file_out:
        for row in file_in:
            if row.find('id="') > -1:
                written = False
                for k, v in main.items():
                    if row.find(k) > -1:
                        i = 0
                        while i < 5:
                            if v >= threshold[i + 1]:
                                i += 1
                            else:
                                break
                        file_out.write(row.replace('id="{}"'.format(k), 'fill="{}"'.format(colour[i])))
                        written = True
                        break
                if written == False:
                    file_out.write(row)
            elif row.find("Level") > -1:
                if row.find("Level 0") > -1:
                    file_out.write(row.replace("Level 0", "&lt; " + "{:_.0f}".format(threshold[1]).replace("_", "&#8201;")))
                else:
                    for i in range(1, 6):
                        if row.find("Level " + format(i)) > -1:
                            file_out.write(row.replace("Level " + format(i), "≥ " + "{:_.0f}".format(threshold[i]).replace("_", "&#8201;")))
                            break
            else:
                file_out.write(row)

print(threshold)
