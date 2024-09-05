# Presentium - Client

This is the client application for Presentium, running on the Raspberry Pi devices.

## Stack
- [Python 3.11](https://www.python.org/)

## Hardware setup

The app is designed to run on a Raspberry Pi 5. Due to a GPIO chip change for the Pi 5, it might not work on older models.

### Wiring
#### Display
The display used in the development of this app is a [LCD1602 with I2C interface](https://de.aliexpress.com/item/1005006018109299.html?gatewayAdapt=glo2deu).

##### Connecting

| Display pin name | Physical RPi pin | RPi pin name |
|------------------|------------------|--------------|
| VCC              | 2, 4             | 5V           |
| GND              | 6, 9, 20, 25     | Ground       |
| SDA              | 3                | GPIO2, SDA   |
| SCL              | 5                | GPIO3, SCL   |

#### RFID Reader
Any RC522 RFID reader should work. The one used in the development of this app is the [Joy IT RFID-RC522](https://joy-it.net/en/products/SBC-RFID-RC522).

##### Connecting
Connecting RC522 module to SPI is pretty easy. You can use [this neat website](http://pi.gadgetoid.com/pinout) for reference.

| Board pin name | Physical RPi pin | RPi pin name |
|----------------|------------------|--------------|
| SDA / NSS      | 24               | GPIO8, CE0   |
| SCK            | 23               | GPIO11, SCKL |
| MOSI           | 19               | GPIO10, MOSI |
| MISO           | 21               | GPIO9, MISO  |
| IRQ            | 18               | GPIO24       |
| GND            | 6, 9, 20, 25     | Ground       |
| RST            | 22               | GPIO25       |
| 3.3V           | 1,17             | 3V3          |

## Development

### Local Development
Local development can't really be done on a computer, as the application is designed to run on a Raspberry Pi. However, you can run the app and test it on the Raspberry Pi.

For this, the easiest method is to have the Raspberry Pi set up with the [Presentium OS](https://github.com/presentium/os).

Once the Raspberry Pi is set up, you can SSH into it and clone this repository. Then, you can run the following commands to start the app:

```bash
cd rpi-client-app
python3 -m venv presentium-venv
source presentium-venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

Don't forget to copy the default config file and edit it to your needs:

```bash
cp config/config.ini.default config.ini
```

## Continuous Delivery

This app is automatically packaged on every tag push. A release is created with the tag name and the package is attached to it.

The CI then triggers a workflow on the [deb package repository](https://github.com/presentium/deb), which will download the package and store it in the repository.

The raspberry pi devices are then configured to automatically update the app when a new release is available using APT Unattended Upgrades.

## Contributing

Please refer to the [Contributing Guide][contributing] before making a pull request.

[contributing]: https://github.com/presentium/meta/blob/main/CONTRIBUTING.md
