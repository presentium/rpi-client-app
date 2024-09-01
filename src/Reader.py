from mfrc522 import SimpleMFRC522

class Reader:
    def __init__(self):
        self.reader = SimpleMFRC522() 

    def read(self) -> tuple:
        return self.reader.read()

    def read_id(self) -> str:
        return str(self.read()[0])

    def read_text(self) -> str:
        return str(self.read()[1])