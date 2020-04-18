def draw(template, values, area, colour, data_type = "div", bands = 5, area_keyword = 'id="_', replaced = 'id="{}"'):
    import statistics, math
    mean = statistics.mean(values)
    if data_type == "seq":
        q = statistics.quantiles(values, n = 100, method = "inclusive")
        if bands < 7:
            step = math.sqrt(mean - q[0]) / 3
        else:
            step = math.sqrt(mean - q[0]) / 4
        threshold = []
        for i in range(bands):
            threshold.append(math.pow(i * step, 2) + q[0])
    else:
        threshold = [0, -mean, -mean / 4, 0, mean / 4, mean]
    print(["{:.0f}".format(i) for i in threshold])
    with open(template + ".svg", newline = "", encoding = "utf-8") as file_in:
        with open(template + "-result.svg", "w", newline = "", encoding = "utf-8") as file_out:
            for row in file_in:
                if row.find(area_keyword) > -1:
                    for k, v in area.items():
                        if row.find(k) > -1:
                            i = 0
                            while i < 5:
                                if v >= threshold[i + 1]:
                                    i += 1
                                else:
                                    break
                            file_out.write(row.replace(replaced.format(k), 'fill="{}"'.format(colour[i])))
                            break
                else:
                    file_out.write(row)
