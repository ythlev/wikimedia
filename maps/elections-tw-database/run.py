import argparse, csv, json

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file")
parser.add_argument("-v", "--verify", action = "store_const", const = True)
args = vars(parser.parse_args())
main = {}

with open("el.json", "w+", newline = "", encoding = "utf-8") as file:
    el = json.loads(file.read())
    el["description"] = "Database for elections in Taiwan"
    file.write(json.dumps(el, indent = 2))
