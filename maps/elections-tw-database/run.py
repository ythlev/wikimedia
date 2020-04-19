import argparse, csv, json

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file")
parser.add_argument("-c", "--commit", action = "store_const", const = True)
args = vars(parser.parse_args())
main = {}

if args["commit"] == True:
    import os
    os.replace("el-preview.json", "el.json")
    quit()

with open("el.json", newline = "") as file:
    el = json.loads(file.read())

el["description"] = "Database for elections in Taiwan"

with open("el-preview.json", newline = "") as file:
    file.write(json.dumps(el, indent = 2))
