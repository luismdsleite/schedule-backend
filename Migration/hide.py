import csv

def convert_boolean(value):
    if value.strip().lower() == "false":
        return "0"
    elif value.strip().lower() == "true":
        return "1"
    else:
        return value

input_file = "Blocos.csv"
output_file = "Blocks.csv"

with open(input_file, "r") as csvfile, open(output_file, "w") as outfile:
    csvreader = csv.reader(csvfile)
    csvwriter = csv.writer(outfile)
    for row in csvreader:
        updated_row = row[:-1] + [convert_boolean(row[-1])]
        csvwriter.writerow(updated_row)