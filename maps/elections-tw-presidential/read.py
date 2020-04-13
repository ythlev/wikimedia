import argparse, json, csv, math, statistics

parser = argparse.ArgumentParser()
parser.add_argument("-y", "--year")
parser.add_argument("-w", "--winner")
parser.add_argument("-r", "--runner_up")
parser.add_argument("-pw", "--party_winner")
parser.add_argument("-pr", "--party_runner_up")
parser.add_argument("-v", "--verify", action = "store_const", const = True)
args = vars(parser.parse_args())

if args["verify"] == True:
    with open("data-test.json", newline = "", encoding = "utf-8") as file_in:
        with open("data-verified.json", "w", newline = "", encoding = "utf-8") as file_out:
            file_out.write(json.dumps(json.loads(file_in.read()), indent = 2, ensure_ascii = False))
            quit()

if int(args["year"]) < 2016:
    with open("old-codes.json", newline = "", encoding = "utf-8") as file:
        oc = json.loads(file.read())[args["year"]]

with open("data-verified.json", newline = "", encoding = "utf-8") as file_in:
    with open("data-test.json", "w", newline = "", encoding = "utf-8") as file_out:
        data = json.loads(file_in.read())
        if args["year"] not in data:
            data[args["year"]] = {}
        if "meta" not in data[args["year"]]:
            data[args["year"]]["meta"] = {}
        meta = data[args["year"]]["meta"]
        if args["winner"] != None and args["runner_up"] != None:
            meta["winner"] = args["winner"]
            meta["runner-up"] = args["runner_up"]
        if args["party_winner"] != None and args["party_runner_up"] != None:
            meta["winner party"] = args["party_winner"]
            meta["runner-up party"] = args["party_runner_up"]
        if "towns" not in data[args["year"]]:
            data[args["year"]]["towns"] = {}
        towns = data[args["year"]]["towns"]

        with open("elctks-" + args["year"] + ".csv", newline = "", encoding = "utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                row = [s.lstrip("'") for s in row]
                row = [s.rstrip(" ") for s in row]
                if row[0] == "00" or row[3] == "000" or row[4] != "0000":
                    continue
                town = row[0] + row[1] + row[3]
                if int(args["year"]) < 2016:
                    town = oc[town]
                if town not in towns:
                    towns[town] = {}
                towns[town][row[6]] = int(row[7])

        values = []
        for town in towns:
            towns[town]["diff"] = towns[town][meta["winner"]] - towns[town][meta["runner-up"]]
            values.append(abs(towns[town]["diff"]))

        step = math.sqrt(statistics.mean(values)) / 2

        threshold = [0, 0, 0]
        for i in range(1, 3):
            threshold[i] = round(math.pow(i * step, 2))

        threshold = [0, -threshold[2], -threshold[1]] + threshold

        data[args["year"]]["meta"]["thresholds"] = threshold

        file_out.write(json.dumps(data, indent = 2, ensure_ascii = False))
