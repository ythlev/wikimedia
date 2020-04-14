import csv, math, statistics

colour = ['#fef0d9','#fdcc8a','#fc8d59','#e34a33','#b30000']

main = {}
values = []

code = {}
with open("code.csv", newline = "", encoding = "utf-8-sig") as file:
    reader = csv.reader(file)
    for row in reader:
        code[row[1]] = row[0]

with open("town.csv", newline = "", encoding = "utf-8-sig") as file:
    reader = csv.DictReader(file)
    for row in reader:
        try:
            main[code[row["site_id"]]] = {"dens": float(row["population_density"])}
        except:
            print(row["site_id"], code[row["site_id"]], row["population_density"])
            quit()
        values.append(float(row["population_density"]))

step = math.sqrt(statistics.mean(values)) / 3

thresholds = [0, 0, 0, 0, 0]
for i in range(5):
    thresholds[i] = math.pow(step * i, 2)

with open("template.svg", "r", newline = "", encoding = "utf-8") as file_in:
    with open("density.svg", "w", newline = "", encoding = "utf-8") as file_out:
        for row in file_in:
            if row.find('id="_') > -1:
                for place in main:
                    if row.find(place) > -1:
                        i = 0
                        while i < 4:
                            if main[place]["dens"] >= thresholds[i + 1]:
                                i += 1
                            else:
                                break
                        file_out.write(row.replace('id="_{}"'.format(place), 'style="fill:{}"'.format(colour[i])))
                        break
            elif row.find('Level 0') > -1:
                file_out.write(row.replace('Level 0', '&lt; ' + "{:.0f}".format(thresholds[1])))
            elif row.find('Level') > -1:
                for i in range(1, 5):
                    if row.find('Level ' + format(i)) > -1:
                        file_out.write(row.replace('Level ' + format(i), '≥ ' + "{:.0f}".format(thresholds[i])))
                        break
            else:
                file_out.write(row)

print("Processed {} areas".format(len(values)))
print("Thresholds: {} Max: {}".format(thresholds, max(values)))
