from RPLCD.i2c import CharLCD
import time

class Screen:
    __cols = 16

    def __init__(self) -> None:
        self.lcd = CharLCD('PCF8574', 0x27)

        self.lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
                    cols=16, rows=2, dotsize=8,
                    charmap='A02',
                    auto_linebreaks=True,
                    backlight_enabled=True)

    def __write_framebuffer(self, framebuffer, num_cols):
        self.lcd.home()
        for row in framebuffer:
            self.lcd.write_string(row.ljust(num_cols)[:num_cols])
            self.lcd.write_string('\r\n')

    def clear(self) -> None:
        self.lcd.clear()

    def write(self, message) -> None:
        self.lcd.write_string(message)
    def clear_and_write(self, message) -> None:
        self.clear()
        self.write(message)

    def write_lines(self, lines) -> None:
        self.clear()
        self.__write_framebuffer(lines, self.__cols)
    def clear_and_write_lines(self, lines) -> None:
        self.clear()
        self.write_lines(lines)

    def rolling_text(self, message, line=0, delay=0.5) -> None:
        self.clear()
        framebuffer = [''] * 2
        for i in range(len(message) - 16 + 1):
            framebuffer[line] = message[i:i+16]
            self.__write_framebuffer(framebuffer, 16)
            time.sleep(delay)
    