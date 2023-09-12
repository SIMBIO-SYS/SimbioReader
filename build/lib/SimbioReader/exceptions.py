class SizeError(Exception):
    def __init__(self, size, expected):
        self.size = size
        self.expected = expected
        super().__init__(self.size, self.expected)

    def __str__(self):
        return f"The file size is {self.size} but the expected size is {self.expected}"