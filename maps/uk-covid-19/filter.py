import json

list = []

with open("subdivisions.json", newline = "", encoding = "utf-8") as file:
    data = json.loads(file.read())
    for attrs in data:
        for attr, value in attrs.items():
            if attr == "ctyua19cd":
                list.append(value)

print(list)
with open("subdivisions-new.json", "w", newline = "", encoding = "utf-8") as file:
    file.write(json.dumps(list))
