from time import sleep
from i2cdevice import I2CDevice
from struct import unpack

# SMPRT_DIV
SMPRT_DIV_REG = 25

# CONFIG
CONFIG_REG = 26
EXT_SYNC_SET = 3
DLPF_CFG = 0

# GYRO_CONFIG
GYRO_CONFIG_REG = 27
XG_ST = 7
YG_ST = 6
ZG_ST = 5
FS_SEL = 3

# ACCEL_CONFIG
ACCEL_CONFIG_REG = 28
XA_ST = 7
YA_ST = 6
ZA_ST = 5
AFS_SEL = 3

# FIFO_EN
FIFO_EN_REG = 35
TEMP_FIFO_EN = 7
XG_FIFO_EN = 6
YG_FIFO_EN = 5
ZG_FIFO_EN = 4
ACCEL_FIFO_EN = 3
SLV2_FIFO_EN = 2
SLV1_FIFO_EN = 1
SLV0_FIFO_EN = 0

# INT_PIN_CFG
INT_PIN_CFG_REG = 55
INT_LEVEL = 7
INT_OPEN = 6
LATCH_INT_EN = 5
INT_RD_CLEAR = 4
BYPASS_EN = 1

# INT_ENABLE
INT_ENABLE_REG = 56
FIFO_OFLOW_EN = 4
I2C_MST_INT_EN = 3
DATA_RDY_EN = 0

# INT_STATUS_REG
INT_STATUS_REG = 58
FIFO_OFLOW_INT = 4
I2C_MST_INT = 3
DATA_RDY_INT = 0

# (DATA Registers)
ACCEL_OUT_REG = 59  # This register is 3x 16 bits wide and has x,y,z components
TEMP_OUT_REG = 65       # This register is 16 bits wide
GYRO_OUT_REG = 67       # This register is 3x 16 bits wide and has x,y,z components

# USER_CTRL
USER_CTRL_REG = 106
FIFO_EN = 6
I2C_MST_EN = 5
I2C_IF_DIS = 4
FIFO_RESET = 2
I2C_MST_RESET = 1
SIG_COND_RESET = 0

# PWR_MGMT_1
PWR_MGMT_1_REG = 107
DEVICE_RESET = 7
SLEEP = 6
CYCLE = 5
TEMP_DIS = 3
CLKSEL = 0

# FIFO_COUNT
FIFO_COUNT_REG = 114

# FIFO_R_W
FIFO_R_W_REG = 116

# WHO_AM_I
WHO_AM_I_REG = 117

SENS_2G = 0
SENS_4G = 1
SENS_8G = 2
SENS_16G = 3

SENS_250DPS = 0
SENS_500DPS = 1
SENS_1000DPS = 2
SENS_2000DPS = 3

WHO_AM_I_VALUE = 0x98

class ICM20689:
    def __init__(self, devinfo):
        self._dev = I2CDevice(*devinfo)
        sig = self._dev.read(WHO_AM_I_REG)
        if sig != WHO_AM_I_VALUE:
            raise ValueError("Signature different than expected: Expected:{} Got:{}".format(WHO_AM_I_VALUE, sig))

        # Setup chip registers
        self._dev.write(PWR_MGMT_1_REG, 0 << SLEEP | 1 << TEMP_DIS | 1 << CLKSEL)
        sleep(0.1)

        self._dev.write(SMPRT_DIV_REG, 0)
        self._dev.write(CONFIG_REG, 0 << DLPF_CFG)
        self._dev.write(GYRO_CONFIG_REG, 1 << FS_SEL)
        self.accel_sensitivity = SENS_16G
        self.gyro_sensitivity = SENS_1000DPS

        sleep(0.1)

    def __enter__(self):
        return self

    @property
    def acceleration(self):
        regs = unpack('>3h', bytes(self._dev.readmulti(ACCEL_OUT_REG, 6)))
        return [self._accel_sf * x for x in regs]

    @property
    def acceleration_raw(self):
        return unpack('>3h', bytes(self._dev.readmulti(ACCEL_OUT_REG, 6)))

    @property
    def accel_sensitivity(self):
        return self._accel_sensitivity

    @accel_sensitivity.setter
    def accel_sensitivity(self, sens):
        if sens == SENS_2G:
            self._dev.write(ACCEL_CONFIG_REG, sens << AFS_SEL)
            self._accel_sf = 2 / 2**15
        elif sens == SENS_4G:
            self._dev.write(ACCEL_CONFIG_REG, sens << AFS_SEL)
            self._accel_sf = 4 / 2**15
        elif sens == SENS_8G:
            self._dev.write(ACCEL_CONFIG_REG, sens << AFS_SEL)
            self._accel_sf = 8 / 2**15
        elif sens == SENS_16G:
            self._dev.write(ACCEL_CONFIG_REG, sens << AFS_SEL)
            self._accel_sf = 16 / 2**15
        else:
            raise ValueError(sens)

        self._accel_sensitivity = sens

    @property
    def gyroscope(self):
        regs = unpack('>3h', bytes(self._dev.readmulti(GYRO_OUT_REG, 6)))
        return [self._gyro_sf * x for x in regs]

    @property
    def gyroscope_raw(self):
        return unpack('>3h', bytes(self._dev.readmulti(GYRO_OUT_REG, 6)))

    @property
    def gyro_sensitivity(self):
        return self._gyro_sensitivity

    @gyro_sensitivity.setter
    def gyro_sensitivity(self, sens):
        if sens == SENS_250DPS:
            self._dev.write(GYRO_CONFIG_REG, sens << FS_SEL)
            self._gyro_sf = 250 / 2**15
        elif sens == SENS_500DPS:
            self._dev.write(GYRO_CONFIG_REG, sens << FS_SEL)
            self._gyro_sf = 500 / 2**15
        elif sens == SENS_1000DPS:
            self._dev.write(GYRO_CONFIG_REG, sens << FS_SEL)
            self._gyro_sf = 1000 / 2**15
        elif sens == SENS_2000DPS:
            self._dev.write(GYRO_CONFIG_REG, sens << FS_SEL)
            self._gyro_sf = 2000 / 2**15
        else:
            raise ValueError(sens)

        self._gyro_sensitivity = sens

    def __exit__(self, e_type, e_val, tb):
        self._dev.close()
