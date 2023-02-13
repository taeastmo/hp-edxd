Start PEC EPICS/MEDM user interface
-----------------------------------

On the Windows desktop of the control computer, users will find a shortcut named ``16bmb MEDM PEC``.

.. note:: MobaXterm program should be started or runnning in the background before opening the MEDM interface, otherwise
          the interface will not start. 

.. note:: If running in isolation mode, the EPICS/MEDM interface should be launched from MobaXterm. 
          In the MobaXterm go to the tab ``duesenberg(s16bmbuser)``. 
          Click Macros (located in either the top Menu bar or left-side tabs) and select ``Start MEDM for 16bmb PEC users``.


Attached below is a screen shot of the PEC User Interface.

.. figure:: /images/operation/EPICS_user_interface.png
   :alt: EPICS_user_interface
   :width: 720px
   :align: center

It interfaces the control widgets with 16-BM-B station shutters, SR status, EPS status, most demanded
motors for user experiments, intensity monitors with ion chambers and diode, and heater power supply controller and pressure control syringe pump.

.. hint:: Please be aware that when entering a new value into a field in an MEDM interface, the mouse cursor must hover over the field. 
          Then the Enter key on the keyboard needs to be pressed to accept the edited value. If the mouse cursor leaves the 
          field before the Enter key is pressed the edited value will revert to the original value.