import array
import csv

class CsvTable:

    def __init__(self, filename: str, skip_header: bool):

        # member initialization
        self.rows = []
        self.index = {}

        # read csv and store rows
        first_row: bool = True
        with open(filename, 'r') as csvfile:
            csvreader = csv.reader(csvfile) 
            for row in csvreader:

                # skip header row if requested
                if first_row:
                    first_row = False
                    if skip_header:
                        continue

                # Each row is a list of strings
                self.rows.append(row)

    def init_index(self):

        counter = 0
        for row in self.rows:
            self.index[row[0]] = counter
            counter += 1

    def find(self, val: str):

        if self.index:
            return self.index[val]
        return -1

    def insert_row(self, row: array):

        self.rows.insert(0, row)

    def size(self):

        return len(self.rows)
