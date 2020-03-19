import csv, math

colours = ['#fef0d9','#fdd49e','#fdbb84','#fc8d59','#ef6548','#d7301f','#990000']

main = {}
values = []

with open("data.csv", newline = "", encoding = "utf-8-sig") as file:
    reader = csv.DictReader(file)
    for row in reader:
        main[row["村里代碼"]] = {"dens": float(row["人口密度"])}
        values.append(float(row["人口密度"]))

values.sort()

step = math.sqrt(values[-777]) / 7

thresholds = [0, 0, 0, 0, 0, 0, 0]
for i in range(7):
    thresholds[i] = round(math.pow(step * i, 2))

with open("template.svg", "r", newline = "", encoding = "utf-8") as file_in:
    with open("density.svg", "w", newline = "", encoding = "utf-8") as file_out:
        for row in file_in:
            written = False
            for place in main:
                if row.find('id="{}"'.format(place)) > -1:
                    i = 0
                    while i < 6:
                        if main[place]["dens"] >= thresholds[i + 1]:
                            i += 1
                        else:
                            break
                    main[place]["threshold met"] = thresholds[i]
                    main[place]["fill"] = colours[i]
                    file_out.write(row.replace('id="{}"'.format(place), 'style="fill:{}"'.format(main[place]["fill"])))
                    written = True
                    break
            if written == False:
                file_out.write(row)

print("Processed {} areas".format(len(values)))
print("Thresholds: {} Max: {}".format(thresholds, max(values)))
