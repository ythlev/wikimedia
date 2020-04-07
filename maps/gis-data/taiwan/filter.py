import pathlib

rows = []

with open((pathlib.Path() / "new-taipei").with_suffix(".svg"), "r", newline = "", encoding = "utf-8") as file_in:
    for row in file_in:
        rows.append(row)

with open((pathlib.Path() / "new-taipei-new").with_suffix(".svg"), "w", newline = "", encoding = "utf-8") as file_out:
    for i in range(len(rows)):
        if rows[i].find('id="_65') > -1:
            file_out.write(rows[i])
            file_out.write(rows[i + 1])
            file_out.write(rows[i + 2])
            file_out.write(rows[i + 3])
            file_out.write(rows[i + 4])
        else:
            written = False
            for keyword in ['id="_', 'title', '/path', 'Township', 'City', 'District']:
                if rows[i].find(keyword) > -1:
                    written = True
                    break
            if written == False:
                file_out.write(rows[i])
