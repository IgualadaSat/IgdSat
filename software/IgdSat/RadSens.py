import smbus
import time
# This is a Python translation from the original library: https://github.com/climateguard/RadSens


# RadSens I2C Register Addresses
RS_DEFAULT_I2C_ADDRESS: int = 0x66 #default adress
RS_DEVICE_ID_RG: int = 0x00
RS_FIRMWARE_VER_RG: int = 0x01
RS_RAD_INTENSY_DYNAMIC_RG: int = 0x03
RS_RAD_INTENSY_STATIC_RG: int = 0x06
RS_PULSE_COUNTER_RG: int = 0x09
RS_DEVICE_ADDRESS_RG: int = 0x10
RS_HV_GENERATOR_RG: int = 0x11
RS_SENSITIVITY_RG: int = 0x12
RS_LED_CONTROL_RG: int = 0x14
RS_LMP_MODE_RG: int = 0x0C



class CG_RadSens:
    def __init__(self, sensor_address: int):
        self._sensor_address: int = sensor_address
        self._bus: smbus.SMBus = smbus.SMBus(1)  # Use 1 for Raspberry Pi, check your system for the correct bus

        self._chip_id: int = 0
        self._firmware_ver: int = 0
        self._pulse_cnt: int = 0
        # HV interval patch!
        self.HV_interval = 60 # Reinitialize HV every 60 seconds
        self.HV_Last = time.time() - 60
        self.HV_state = False

    def _i2c_read(self, reg_addr: int, num: int):
        #HV check...
        if self.HV_state == True and (time.time() - self.HV_Last ) > 6:
            self.HV_state = False
            self.set_hv_generator_state(False)
            print("HV off")

        if (time.time() - self.HV_Last ) > self.HV_interval:
            #Reinitialize HV
            self.HV_state = True
            self.HV_Last = time.time()
            self.set_hv_generator_state(True)
            print("HV on")
        

        try:
            data: list = self._bus.read_i2c_block_data(self._sensor_address, reg_addr, num)
            return data
        except Exception as e:
            print(f"Error reading from I2C address {self._sensor_address}, register {reg_addr}: {e}")
            return None

    def _update_pulses(self):
        res: list = self._i2c_read(RS_PULSE_COUNTER_RG, 2)
        if res:
            self._pulse_cnt += (res[0] << 8) | res[1]

    def init(self) -> bool:
        try:
            # Safety check, make sure the sensor is connected
            self._bus.write_byte(self._sensor_address, 0x00)
        except Exception as e:
            print(f"Error initializing RadSens: {e}")
            return False

        self._update_pulses()

        res: list = self._i2c_read(RS_DEVICE_ID_RG, 2)
        if res:
            self._chip_id: int = res[0]
            self._firmware_ver: int = res[1]
            return True
        return False

    def get_chip_id(self) -> int:
        return self._chip_id

    def get_firmware_version(self) -> int:
        return self._firmware_ver

    def get_rad_intensy_dynamic(self) -> float:
        self._update_pulses()
        res: list = self._i2c_read(RS_RAD_INTENSY_DYNAMIC_RG, 3)
        if res:
            temp: float = ((res[0] << 16) | (res[1] << 8) | res[2]) / 10.0
            return temp
        else:
            return 0.0

    def get_rad_intensy_static(self) -> float:
        self._update_pulses()
        res: list = self._i2c_read(RS_RAD_INTENSY_STATIC_RG, 3)
        if res:
            return ((res[0] << 16) | (res[1] << 8) | res[2]) / 10.0
        else:
            return 0.0

    def get_number_of_pulses(self) -> int:
        self._update_pulses()
        return self._pulse_cnt

    def get_sensor_address(self) -> int:
        res: list = self._i2c_read(RS_DEVICE_ADDRESS_RG, 1)
        if res:
            self._sensor_address: int = res[0]
            return self._sensor_address
        return 0

    def get_hv_generator_state(self) -> bool:
        res: list = self._i2c_read(RS_HV_GENERATOR_RG, 1)
        if res:
            return res[0] == 1
        return False

    def get_led_state(self) -> bool:
        res: list = self._i2c_read(RS_LED_CONTROL_RG, 1)
        if res:
            return res[0] == 1
        return False

    def get_sensitivity(self) -> int:
        res: list = self._i2c_read(RS_SENSITIVITY_RG, 2)
        if res:
            return res[1] * 256 + res[0]
        return 0

    def set_hv_generator_state(self, state: bool) -> bool:
        try:
            self._bus.write_byte_data(self._sensor_address, RS_HV_GENERATOR_RG, 1 if state else 0)
            return True
        except Exception as e:
            print(f"Error setting HV generator state: {e}")
            return False

    def set_lp_mode(self, state: bool) -> bool:
        try:
            self._bus.write_byte_data(self._sensor_address, RS_LMP_MODE_RG, 1 if state else 0)
            return True
        except Exception as e:
            print(f"Error setting LP mode: {e}")
            return False

    def set_sensitivity(self, sens: int) -> bool:
        try:
            self._bus.write_i2c_block_data(self._sensor_address, RS_SENSITIVITY_RG, [sens & 0xFF, sens >> 8])
            time.sleep(0.015)
            self._bus.write_i2c_block_data(self._sensor_address, RS_SENSITIVITY_RG + 0x01, [sens >> 8])
            return True
        except Exception as e:
            print(f"Error setting sensitivity: {e}")
            return False

    def set_led_state(self, state: bool) -> bool:
        try:
            self._bus.write_byte_data(self._sensor_address, RS_LED_CONTROL_RG, 1 if state else 0)
            time.sleep(0.015)
            return True
        except Exception as e:
            print(f"Error setting LED state: {e}")
            return False
            
# Example usage:
# rad_sens = CG_RadSens(sensor_address=0x66)
# if rad_sens.init():
#     print(f"Chip ID: {rad_sens.get_chip_id()}")
#     print(f"Firmware Version: {rad_sens.get_firmware_version()}")
#     print(f"Dynamic Radiation Intensity: {rad_sens.get_rad_intensy_dynamic()} uR/h")
#     print(f"Static Radiation Intensity: {rad_sens.get_rad_intensy_static()} uR/h")
#     print(f"Number of Pulses: {rad_sens.get_number_of_pulses()}")
#     print(f"Sensor Address: {hex(rad_sens.get_sensor_address())}")
#     print(f"HV Generator State: {rad_sens.get_hv_generator_state()}")
#     print(f"LED State: {rad_sens.get_led_state()}")
#     print(f"Sensitivity: {rad_sens.get_sensitivity()} Imp/uR")
# else:
#     print("Failed to initialize RadSens.")
