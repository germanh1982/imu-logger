import smbus

class I2CDevice:
    def __init__(self, bus, devaddr):
        self._bus = smbus.SMBus(bus)
        self._devaddr = devaddr

    def write(self, regaddr, data):
        self.writemulti(regaddr, [data])

    def read(self, regaddr):
        return self.readmulti(regaddr, 1)[0]

    def writemulti(self, regaddr, data):
        self._bus.write_i2c_block_data(self._devaddr, regaddr, data)

    def readmulti(self, regaddr, size):
        return self._bus.read_i2c_block_data(self._devaddr, regaddr, size)

    def __enter__(self):
        return self

    def close(self):
        self._bus.close()

    def __exit__(self, exc_type, exc_value, tb):
        self.close()
