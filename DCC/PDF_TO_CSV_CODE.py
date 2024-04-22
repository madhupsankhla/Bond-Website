import fitz
import csv

def pdf_to_csv(input_file, output_file):
    writer = csv.writer(open(output_file, 'w', newline=''))
    doc = fitz.open(input_file)
    i= 0
    for page in doc:
        tabs = page.find_tables()
        if tabs.tables:
            writer.writerows(tabs[0].extract())
            print("Page ", i, " done")
            i += 1


