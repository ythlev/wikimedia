import csv

data = []
with open("data.csv", newline = "", encoding = "utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        data.append({
            "code": row["村里代碼"],
            "dens": float(row["人口密度"])
        })

threshold = [0, 307, 1227, 2762, 4910]
colour = ['#fef0d9','#fdcc8a','#fc8d59','#e34a33','#b30000']


with open("template.svg", newline = "", encoding = "utf-8") as file_in:
    with open("vill.svg", "w", newline = "", encoding = "utf-8") as file_out:
        for row in file_in:
            if row.find('id="_') > -1:
                written = False
                for vill in data:
                    if row.find(vill["code"]) > -1:
                        i = 0
                        while i < 4:
                            if vill["dens"] >= threshold[i + 1]:
                                i += 1
                            else:
                                break
                        file_out.write(row.replace('id="_{}"'.format(vill["code"]), 'style="fill:{}"'.format(colour[i])))
                        written = True
                        break
                if written == False:
                    file_out.write(row.replace('id="_', 'style="fill:#fef0d9" id="_'))
            else:
                file_out.write(row)
