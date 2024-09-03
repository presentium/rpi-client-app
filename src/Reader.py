import pirc522

class Reader:
    def read_id(self):
        self.running = True
        try:
            reader = pirc522.RFID()
            while self.running:
                uid = reader.read_id(True)
                if uid is not None:
                    return str(uid)
                
            return None

        except KeyboardInterrupt:
            return None

        finally:
            reader.cleanup()

    def stop(self):
        self.running = False
