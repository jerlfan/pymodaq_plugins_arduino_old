# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 13:07:44 2023

@author: manip-lumi
"""
"""
Wrapper for grating movement using Arduino
"""

import os
import platform
import sys
from ctypes import c_ulong, c_double, c_ushort
from ctypes import cdll, byref
from telemetrix import telemetrix
import time

is_64bits = sys.maxsize > 2 ** 32


class IK220:
    """
    Wrapper to the Heidenhain dll
    """
    units = 'cm'

    def __init__(self, dllpath="C:\\Program Files (x86)\\HEIDENHAIN\\DLL64"):
        """Initialize device"""
        self.dll = None
        self.axis = []
        self.pStatus = c_ushort()
        self.pAlarm = c_ushort()
        if not dllpath:
            dllpath = 'C:\\Program Files (x86)\\HEIDENHAIN'
            if is_64bits:
                if platform.machine() == "AMD64":
                    dllpath = os.path.join(dllpath, 'DLL64')
                else:
                    dllpath = os.path.join(dllpath, 'DLL')
        try:
            # Check operating system and load library
            if platform.system() == "Windows":
                if is_64bits:
                    dllname = os.path.join(dllpath, "IK220Dll64")
                    # print(dllname)
                    self.dll = cdll.LoadLibrary(dllname)
                else:
                    dllname = os.path.join(dllpath, "IK220Dll")
                    self.dll = cdll.LoadLibrary(dllname)
            else:
                print("Cannot detect operating system, will now stop")
                raise Exception("Cannot detect operating system, will now stop")
        except Exception as e:
            raise Exception("error while initialising hein libraries. " + str(e))

        self.get_present_axis()
        self.config_endat()

    def config_endat(self):
        p_status = c_ushort()  # pointer
        p_type = c_ushort()  # pointer
        p_period = c_ulong()  # pointer
        p_step = c_ulong()  # pointer
        p_turns = c_ushort()  # pointer
        p_ref_dist = c_ushort()  # pointer
        p_cnt_dir = c_ushort()
        for axis in self.axis:
            self.dll.IK220ConfigEn(axis, byref(p_status), byref(p_type), byref(p_period), byref(p_step), byref(p_turns),
                                   byref(p_ref_dist), byref(p_cnt_dir))

    def get_present_axis(self):
        """
        :return:
            position of the axis i with respect to the
        Input:
            None
        Output:
            pointer 16 entries
        """
        serial = (c_ulong * 16)()
        self.dll.IK220Find(byref(serial))
        self.axis = []
        for i in range(0, 16, 1):  # There is 16 axis numbered from 0 t 15
            if serial[i] > 0:
                self.axis.append(i)
            else:
                pass
        return f'Axis {self.axis} are present'

    def get_axis_position(self, axis):
        """
        :return: the absolute position deduced from one period.
        To obtain the real value in cm^{-1} this result has to be multiplied by a factor 2.
        Finally, as our goal is t reach a resolution of 0.1 cm^{-1} (i.e. 1µm),
        the obtained result is rounded

        Input:
            None
        Output:

        """
        p_data = c_double()
        self.dll.IK220ReadEn(axis, byref(self.pStatus), byref(p_data), byref(self.pAlarm))
        return round(p_data.value * 2, 3)

class Stepper:
    def open_communication(self, port):
       """
       fake instrument opening communication.
       Returns
       -------
       bool: True is instrument is opened else False
       """
       self.device=telemetrix.Telemetrix(com_port=port)

       self.motor = self.device.set_pin_mode_stepper(interface=2, pin1=3, pin2=4)

       return True

    def current_position_callback(self, data):
       print(f'pos {data[2]}\n')
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
       return print(f'Motor disconnected:')