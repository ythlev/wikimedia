# 張嘉桓 製
import urllib.request, json, io, math

places = [
    "新北市", "台北市", "桃園市", "台中市", "台南市", "高雄市", "宜蘭縣", "新竹縣", "苗栗縣", "彰化縣", "南投縣",
    "雲林縣", "嘉義縣", "屏東縣", "台東縣", "花蓮縣", "澎湖縣", "基隆市", "新竹市", "嘉義市", "金門縣", "連江縣"
]

main = {}
for place in places:
    main[place] = {"cases": 0}

with urllib.request.urlopen("https://od.cdc.gov.tw/eic/Weekly_Age_County_Gender_19CoV.json") as response:
    data = json.loads(response.read())
    for row in data:
        for place in main:
            if row["縣市"] == place:
                main[place]["cases"] += int(row["確定病例數"])
                break

list = []
for attrs in main.values():
    list.append(attrs["cases"])

min = min(list)
max = max(list)

thresholds = []
for i in range(8):
    thresholds.append(min)

if min == 0:
    step = math.log(max) / 5
    for i in range(7):
        thresholds[i + 1] = round(math.exp(step * i))
    thresholds = thresholds[0:7]
else:
    step = math.log(max / min) / 6
    for i in range(8):
        thresholds[i + 1] = round(min * math.exp(step * i))
    thresholds = thresholds[1:8]

colours = ["#fee5d9","#fcbba1","#fc9272","#fb6a4a","#de2d26","#a50f15"]

with open("template.svg", "r", newline = "", encoding = "utf-8") as file_in:
    with open("output.svg", "w", newline = "", encoding = "utf-8") as file_out:
        for row in file_in:
            written = False
            for place, attrs in main.items():
                if row.find(place) > 0:
                    if attrs["cases"] == max:
                        main[place]["threshold met"] = thresholds[5]
                        main[place]["colour"] = colours[5]
                    else:
                        i = 0
                        while attrs["cases"] >= thresholds[i]:
                            i += 1
                        i -= 1
                        main[place]["threshold met"] = thresholds[i]
                        main[place]["colour"] = colours[i]
                    file_out.write(row.replace('id="%s"' % place, 'style="fill:%s"' % attrs["colour"]))
                    written = True
                    break
            if written == False:
                file_out.write(row)

for place, attrs in main.items():
    print(place, attrs)

print("Total cases: ", sum(list))
print("Colours: ", colours)
print("Thresholds (rightmost not used): ", thresholds)
