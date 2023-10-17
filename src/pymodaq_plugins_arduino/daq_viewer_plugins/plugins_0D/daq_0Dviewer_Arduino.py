import numpy as np
from pymodaq.daq_utils.daq_utils import ThreadCommand
from pymodaq.daq_utils.daq_utils import DataFromPlugins
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.daq_utils.parameter import Parameter
from pymodaq_plugins_arduino.hardware.ruler_wrapper import IK220




class DAQ_0DViewer_Arduino(DAQ_Viewer_base):
    """
    """
    params = comon_parameters+[{'title': 'Axis:', 'name': 'axis', 'type': 'int', 'value': 1.00},
        {'title': 'Laser Wavelength (nm):', 'name': 'las_wave', 'type': 'float', 'value': 457.00},
        {'title': 'correction:', 'name': 'correc', 'type': 'float', 'value': 5905.0}
        ## TODO for your custom plugin: elements to be added here as dicts in order to control your custom stage
        ]

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == 'las_wave':
            self.wavelength = 1e7 / param.value()
        elif param.name() == 'correc':
            self.correction = param.value()
        elif param.name() == 'axis':
            self.axis = param.value()

    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        #raise NotImplemented  # TODO when writing your own plugin remove this line and modify the one below
        self.controller=IK220()
        #self.ini_detector_init(old_controller=controller,new_controller=PythonWrapperOfYourInstrument())

        # TODO for your custom plugin (optional) initialize viewers panel with the future type of data
        #self.data_grabed_signal_temp.emit([DataFromPlugins(name='Ruler',data=[np.array([0])],dim='Data0D',labels=['Position', 'time'])])

        info = "Connected"
        initialized = True
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        #del self.controller # when writing your own plugin remove this line

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """

        # synchrone version (blocking function)

        data_tot = (self.controller.get_axis_position(self.settings.child('axis').value())
                    +self.settings.child('correc').value())-(1e7 /self.settings.child('las_wave').value())

        self.data_grabed_signal.emit([DataFromPlugins(name='Ruler', data=[np.array([data_tot])], dim='Data0D',labels=['dat0', 'data1'])])

    def callback(self):
        """optional asynchrone method called when the detector has finished its acquisition of data"""
        data_tot = self.controller.your_method_to_get_data_from_buffer()
        self.data_grabed_signal.emit([DataFromPlugins(name='Mock1', data=data_tot,
                                                      dim='Data0D', labels=['dat0', 'data1'])])

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        ## TODO for your custom plugin

        self.emit_status(ThreadCommand('Update_Status', ['Stop']))
        ##############################
        return ''


if __name__ == '__main__':
    main(__file__)