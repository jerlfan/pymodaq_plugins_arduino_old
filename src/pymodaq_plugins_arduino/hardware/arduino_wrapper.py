"""
Demo Wrapper to illustrate the plugin developpement. This Mock wrapper will emulate communication with an instrument
"""

from time import perf_counter, sleep
import time
import math

from serial.tools import list_ports
ports = [port.name for port in list_ports.comports()]

from pymodaq_plugins_arduino.hardware.ruler_wrapper import IK220
from telemetrix import telemetrix
class ActuatorWrapper:
    units = 'wavenumber (cm-1)'
    def __init__(self):
        self._com_port = ''
        self._current_value = 0
        self._target_value = None
        self.running = False
        self.status = 0




    def open_communication(self, port):
        """
        fake instrument opening communication.
        Returns
        -------
        bool: True is instrument is opened else False
        """
        self.device=telemetrix.Telemetrix(com_port=port,arduino_wait=4)

        self.motor = self.device.set_pin_mode_stepper(interface=2, pin1=3, pin2=4)

        return True

    def current_position_callback(self, data):
        #print(f'pos {data[2]}\n')
        self.status = data[2]

    def is_running_callback(self, data):
        self.running = data[1]
        print(f'is_running_callback returns {data[1]}\n')

    def the_callback(self, data):
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[2]))
        print(f'Motor {data[1]} absolute motion completed at: {date}.')

    def move_at(self, value):
        """
        Send a call to the actuator to move at the given value
        Parameters
        ----------
        value: (float) the target value
        """
        self._target_value = value
        self._init_value = self._current_value
        n_steps = round((self._target_value - self._init_value))

        self.device.stepper_move(self.motor, n_steps)
        self.device.stepper_run(self.motor, completion_callback=self.the_callback)
        self.device.stepper_is_running(self.motor, self.is_running_callback)
        time.sleep(0.01)
        while self.running == 1:
            time.sleep(0.01)
            self.device.stepper_is_running(self.motor, self.is_running_callback)
            time.sleep(0.01)
            self.get_value()
        # self._start_time = perf_counter()
        self._moving = True

    def max_speed_set(self,value):
        self.device.stepper_set_max_speed(self.motor, value)

    def accel_set(self,value):
        self.device.stepper_set_acceleration(self.motor, value)


    def get_value(self):
        """
        Get the current actuator value
        Returns
        -------
        float: The current value
        """

        self.device.stepper_get_current_position(self.motor, self.current_position_callback)
        self._current_value = self.status
        return self._current_value

    def close_communication(self):
        self.device.shutdown()
        return f'Motor disconnected:'






