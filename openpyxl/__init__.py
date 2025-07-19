class Worksheet:
    def __init__(self):
        self.rows = []

    def append(self, row):
        self.rows.append(list(row))

class Workbook:
    def __init__(self):
        self.active = Worksheet()

    def save(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            for row in self.active.rows:
                f.write(','.join(str(x) for x in row) + '\n')
