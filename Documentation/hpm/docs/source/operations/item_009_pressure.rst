Pressure control
----------------
The PEC oil pressure is controlled by the Teledyne ISCO 30D dual syringe pump system. 
The maximum pressure allowed is 14,000 psi (9,000 psi for ultrasound or grooved cells).
Syringe pump is controlled through the MEDM interface

.. figure:: /images/operation/syringe_pump_interface.png
   :alt: syringe_pump_interface
   :width: 720px
   :align: center

Basic pump operation
Procedure for increasing, maintaining, and decreasing pressure. 

.. warning:: Due to a problem with the pump controller, sometimes communication with the pump 
   gets lost and the indicators colors will change to white. 
   If this happens, please wait around 1-2 minutes, the communication should get re-established on its own. 
   Afterwards, you may need to re-do the last command. 

Compression
^^^^^^^^^^^

   1. Make sure Mode is selected as “Compress”. 

   .. note:: Stop the Pressure Control before switching Mode. (Mode button is hidden while Pressure Control is in “Run” state). 

   2. Refill pumps A and B (click the button :guilabel:`Refill` for each pump). 

   .. note:: Wait until both pumps finish refilling.

   3. Set Max flow for both pumps to 5ml/min.
   #. Set the Oil pressure setpoint to 20 psi.
   #. Set Pressure control to Run. Pump will go through the initial equalization sequence; this will take around 30 seconds to one minute. 

   .. note:: Pressure may go up to ~80 psi and fluctuate somewhat during this process. 
      Wait until the Actual oil pressure stabilizes at 20 psi.

   6. Increase the Oil pressure setpoint to your required pressure (maximum allowed is 14,000psi). Pump will gradually reach the setpoint pressure and maintain the pressure continuously. 
   #. If you don't want the pump to maintain the pressure continuously after reaching the setpoint, set the Maximum oil flow-rates for pumps A and B to 0.0001 ml/min. 

   .. important:: DO NOT switch Pressure Control to Stop. 

   8. To reach the next oil pressure setpoint, re-enable pressure control by setting Max flow rates back to 5 ml/min.

Decompression
^^^^^^^^^^^^^

   1. Set Pressure Control to Stop.
   2. Set Mode to Decompress. 
   3. Set Pressure Control to Run.

   .. important:: Wait around 1 minute before doing anything else. 
      After around 30 seconds, one of the pumps (A or B) will start emptying out (there will be a valve opening/closing sound). 
      Wait until the level in that pump reaches around 7.5 ml.

   4. Set the setpoint pressure to 20 psi.
   #. After the actual oil pressure is at 20 psi, switch pressure control to Stop.
   #. Open the valves to vent the remaining oil pressure:

      1. Open valve control from the main PEC interface menu "Pump control menu"

      .. figure:: /images/sp/valve_control_2.png
         :alt: valve_control
         :width: 300px
         :align: center

      2. Toggle Valves 1-4 to Low. 

      .. note:: If the readback text for a valve is high (red), and pressed button is low: click the :guilabel:`high` button and then the :guilabel:`low` button.

      .. note:: If the valve 1-4 buttons are hidden check the following conditions are met: 
         
         * Pressure : <= 20psi
         * Pressure setpoint: 20psi
         * Pressure control: stopped

   .. figure:: /images/sp/valve_control_blocked.png
       :alt: valve_control_blocked
       :width: 300px
       :align: center


PE Press Live valve
^^^^^^^^^^^^^^^^^^^

The Live valve is and electronically actuated valve in-line between the Syringe pump and the PE press. 
The Line valve allows to keep the pressure in the PE press isolated from the Syringe pump when changing modes 
(Compression <-> Decompression), when heating, or when leaviing the PE press unattended for an extended perions of time.
This subseciton describes the operation of the Line valve.
