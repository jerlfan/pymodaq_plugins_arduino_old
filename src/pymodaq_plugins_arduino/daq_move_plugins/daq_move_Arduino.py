from pymodaq.daq_move.utility_classes import DAQ_Move_base  # base class
from pymodaq.daq_move.utility_classes import comon_parameters  # common set of parameters for all actuators
from pymodaq.daq_utils.daq_utils import ThreadCommand, getLineInfo  # object used to send info back to the main thread
from easydict import EasyDict as edict  # type of dict
from pymodaq_plugins_arduino.hardware.arduino_wrapper import ActuatorWrapper


from serial.tools import list_ports
ports = [str(port.name) for port in list_ports.comports()]
port = 'COM5' #if 'cu.usbmodem401301' in ports else ports[0] if len(ports)>0 else ''
class DAQ_Move_Arduino(DAQ_Move_base):
    """
        Wrapper object to access the Mock fonctionnalities, similar wrapper for all controllers.

        =============== ==============
        **Attributes**    **Type**
        *params*          dictionnary
        =============== ==============
    """
    _controller_units = ActuatorWrapper.units
    axes_names = ['grating']  # TODO for your plugin: complete the list
    _epsilon = 1  # TODO replace this by a value that is correct depending on your controller


    is_multiaxes = False  # set to True if this plugin is controlled for a multiaxis controller (with a unique communication link)
    stage_names = ['Motor 1']  # "list of strings of the multiaxes

    params = [   ## TODO for your custom plugin
                 # elements to be added here as dicts in order to control your custom stage
                 ############
                 {'title': 'Com port:', 'name': 'comport', 'type': 'str', 'limits':ports, 'value': port,
                  'tip': 'The serial COM port'},
                 #{'title': 'Laser wavelength:', 'name': 'wavelength', 'type': 'float', 'limits': ports, 'value': port,
                  #'tip': 'The wavelength of the laser'},
                 {'title': 'Acceleration:', 'name': 'accel', 'type': 'int', 'value': 200,
                  'tip': 'Set the stepper motor acceleration'},
                 {'title': 'Max speed:', 'name': 'maxspeed', 'type': 'int', 'value': 1000,
                  'tip': 'Set the stepper motor max speed'},
                 {'title': 'MultiAxes:', 'name': 'multiaxes', 'type': 'group', 'visible': is_multiaxes, 'children': [
                     {'title': 'is Multiaxes:', 'name': 'ismultiaxes', 'type': 'bool', 'value': is_multiaxes,
                      'default': False},
                     {'title': 'Status:', 'name': 'multi_status', 'type': 'list', 'value': 'Master',
                      'values': ['Master', 'Slave']},
                     {'title': 'Axis:', 'name': 'axis', 'type': 'list', 'values': stage_names},

                 ]}] + comon_parameters

    def __init__(self, parent=None, params_state=None):
        """
            Initialize the the class

            ============== ================================================ ==========================================================================================
            **Parameters**  **Type**                                         **Description**

            *parent*        Caller object of this plugin                    see DAQ_Move_main.DAQ_Move_stage
            *params_state*  list of dicts                                   saved state of the plugins parameters list
            ============== ================================================ ==========================================================================================

        """

        super().__init__(parent, params_state)


    def check_position(self):
        """Get the current position from the hardware with scaling conversion.

        Returns
        -------
        float: The position obtained after scaling conversion.
        """
        ## TODO for your custom plugin
        pos = self.controller.get_value()

        ##

        pos = self.get_position_with_scaling(pos)
        self.emit_status(ThreadCommand('check_position',[pos]))
        return pos


    def close(self):
        """
        Terminate the communication protocol
        """
        ## TODO for your custom plugin
        self.controller.close_communication()        ##

    def commit_settings(self, param):
        """
            | Activate any parameter changes on the PI_GCS2 hardware.
            |
            | Called after a param_tree_changed signal from DAQ_Move_main.

        """

        ## TODO for your custom plugin
        if param.name() == self.settings.child(('accel')):
           self.controller.accel_set(self.settings.child(('accel')).value())
        elif param.name() == self.settings.child(('maxspeed')):
           self.controller.max_speed_set(self.settings.child(('maxspeed')).value())
        #elif param.name() == self.settings.child(('wavelength')):
        #    self.controller.max_speed_set(self.settings.child(('wavelength')).value())
        elif param.name() == 'epsilon':
            self.controller.epsilon = param.value()

    def ini_stage(self, controller=None):
        """Actuator communication initialization

        Parameters
        ----------
        controller: (object) custom object of a PyMoDAQ plugin (Slave case). None if only one actuator by controller (Master case)

        Returns
        -------
        self.status (edict): with initialization status: three fields:
            * info (str)
            * controller (object) initialized controller
            *initialized: (bool): False if initialization failed otherwise True
        """

        self.ini_stage_init(old_controller=controller, new_controller=ActuatorWrapper())
        self.controller.open_communication(self.settings.child(('comport')).value())

        self.controller.accel_set(self.settings.child(('accel')).value())
        self.controller.max_speed_set(self.settings.child(('maxspeed')).value())

        info = "Connected"
        initialized = True  # self.controller.a_method_or_atttribute_to_check_if_init()  # todo
        return info, initialized

    def move_Abs(self, position):
        """ Move the actuator to the absolute target defined by position

        Parameters
        ----------
        position: (flaot) value of the absolute target positioning
        """

        position = self.check_bound(position)  #if user checked bounds, the defined bounds are applied here


        self.controller.move_at(position)
        self.emit_status(ThreadCommand('Update_Status',['Move done']))
        ##############################



        self.target_position = position
        self.current_position = position
        #self.poll_moving()  #start a loop to poll the current actuator value and compare it with target position
        #if abs(self.target_position - self.current_position)>self.controller.epsilon:
         #   self.controller.move_at(position)
        #self.move_done(position)

    def move_Rel(self, position):
        """ Move the actuator to the relative target actuator value defined by position

        Parameters
        ----------
        position: (flaot) value of the relative target positioning
        """
        position = self.check_bound(self.current_position+position)

        self.controller.move_at(position)
        self.emit_status(ThreadCommand('Update_Status',['Some info you want to log']))

        self.target_position = position
        self.move_done(position)
        ##############################

        #self.poll_moving()

    def move_Home(self):
        """
          Send the update status thread command.
            See Also
            --------
            daq_utils.ThreadCommand
        """

        ## TODO for your custom plugin
        self.controller.your_method_to_get_to_a_known_reference()
        self.emit_status(ThreadCommand('Update_Status',['Some info you want to log']))
        ##############################


    def stop_motion(self):
      """
        Call the specific move_done function (depending on the hardware).

        See Also
        --------
        move_done
      """

      ## TODO for your custom plugin
     # self.
      self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))
      self.move_done() #to let the interface know the actuator stopped
      ##############################


