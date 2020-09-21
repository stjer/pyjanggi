import constant

class Grid:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

        if self.row < constant.MIN_ROW or self.row > constant.MAX_ROW:
            raise Exception(f"Grid row is out of range: {self.row}")

        if self.col < constant.MIN_COL or self.col > constant.MAX_COL:
            raise Exception(f"Grid column is out of range: {self.col}")

