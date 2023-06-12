from pymodaq.pid.utils import PIDModelGeneric, OutputToActuator, InputFromDetector, main


class PIDModelGrating(PIDModelGeneric):


    limits = dict(max=dict(state=False, value=10),
                  min=dict(state=False, value=0), )
    konstants = dict(kp=1, ki=0, kd=0.0000)


    Nsetpoints = 1
    setpoint_ini = [15980.00]
    setpoint_name = ['Wavenumber']
    actuators_name = ["Stepper"]
    detectors_name = ['Ruler']

    def __init__(self, pid_controller):
        super().__init__(pid_controller)

    def update_settings(self, param):
        """
        Get a parameter instance whose value has been modified by a user on the UI
        Parameters
        ----------
        param: (Parameter) instance of Parameter object
        """
        if param.name() == '':
            pass

    def ini_model(self):
        super().ini_model()


    def convert_input(self, measurements):
        """
        Convert the measurements in the units to be fed to the PID (same dimensionality as the setpoint)
        Parameters
        ----------
        measurements: (Ordereddict) Ordereded dict of object from which the model extract a value of the same units as the setpoint

        Returns
        -------
        float: the converted input

        """

        self.curr_input = measurements['Ruler']['data0D']['Ruler_Ruler_CH000']['data']

        return InputFromDetector([self.curr_input])

    def convert_output(self, outputs, dt, stab=True):
        """

        """
        self.curr_output = outputs
        return OutputToActuator(mode='rel', values=outputs)


if __name__ == '__main__':
   main("preset_pid_z40.xml")

