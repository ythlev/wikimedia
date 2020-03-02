import io, urllib.request, csv, math

subdivisions = {}
with open("subdivisions.csv", newline = "", encoding = "utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        subdivisions[row["COUNTYNAME"]] = {"cases": 0}

with urllib.request.urlopen("https://od.cdc.gov.tw/eic/Weekly_Age_County_Gender_19CoV.csv") as response:
    reader = csv.DictReader(io.TextIOWrapper(response, encoding = 'utf-8'), delimiter=',')
    for row in reader:
        for k, v in subdivisions.items():
            if row["縣市"] == k:
                subdivisions[k]["cases"] += int(row["確定病例數"])
                break

list = []
for k, v in subdivisions.items():
    list.append(v["cases"])

min = min(list)
max = max(list)

thresholds = [0, 0, 0, 0, 0, 0, 0]

if min == 0:
    step = math.log10(max * 0.9) / 3
    for i in range(1, 6):
        thresholds[i] = round(10 ** ((i - 1) * step))
    thresholds = thresholds[0:6]
else:
    step = math.log10(max * 0.9 / min) / 4
    for i in range(7):
        thresholds[i] = round(10 ** ((i - 1) * step))
    thresholds = thresholds[1:7]

colours = ["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15"]

with open("template.svg", "r", newline = "", encoding = "utf-8") as f_in:
    with open("output.svg", "w", newline = "", encoding = "utf-8") as f_out:
        for row in f_in:
            written = False
            for k, v in subdivisions.items():
                if row.find(k) > 0:
                    i = 0
                    while v["cases"] >= thresholds[i]:
                        i += 1
                    subdivisions[k]["threshold met"] = thresholds[i - 1]
                    subdivisions[k]["colour"] = colours[i - 1]
                    f_out.write(row.replace('id="%s"' % k, 'style="fill:%s"' % subdivisions[k]["colour"]))
                    written = True
                    break
            if written == False:
                f_out.write(row)

for k, v in subdivisions.items():
    print(k, v)

print("Thresholds: ", thresholds[0:-1])
print("Colours by threshold: ", colours)
