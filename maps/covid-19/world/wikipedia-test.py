import argparse, csv, urllib.request, io, datetime, math, json

main = {}

def grabFromTemplate(): # credits: Dan Polansky
    import urllib.request, re
    url="https://en.wikipedia.org/wiki/Template:2019%E2%80%9320_coronavirus_pandemic_data"
    allLines = []
    for line in urllib.request.urlopen(url):
      allLines.append((line.decode()).rstrip())
    allLines = " ".join(allLines)
    allLines = re.sub("^.*jquery-tablesorter", "", allLines)
    allLines = re.sub("</table.*", "", allLines)
    allLines = re.sub("<(th|td)[^>]*>", r"<td>", allLines)
    allLines = re.sub("</?(span|img|a|sup)[^>]*>", "", allLines)
    allLines = re.sub("</(th|td|tr)[^>]*>", "", allLines)
    allLines = re.sub("&#91.*?&#93", "", allLines)
    allLines = re.sub(",", "", allLines)
    allLines = re.sub("<small>.*?</small>;?", "", allLines)
    allLines = re.sub("</?i>", "", allLines)

    outData = {}
    rows = allLines.split("<tr> ")
    for row in rows:
        try:
            cols = row.split("<td>")
            cols.pop(0)
            cols.pop(0)
            country = cols.pop(0)
            cols = cols[0:3]
            cols = [int(col) for col in cols]
        except:
            continue
        outData[(country.rstrip()).replace(";", "")] = cols
    #for key, value in outData.items():
    #  print key, value
    return outData

template = grabFromTemplate()

for place in template:
    print(place, template[place])
