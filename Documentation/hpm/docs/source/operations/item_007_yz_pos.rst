.. _yz_position:

Sample Y and/or Z positions search
----------------------------------
There are 2 ways to search sample Y and/or Z positions:

(1)	Search by radiography image
(2)	Scan absorption profile
(3)   Scan by EDXD or flurescence profile (refer to :ref:`X position search <x_position>`)


By radiography image
^^^^^^^^^^^^^^^^^^^^

   - Switch to :ref:`radiography measurement mode <radiography_mode>`.
   - Narrow slit size to those of EDXD measurement.
   - Mark the narrow slit size and position by tape or something on monitor.
   - Open slit (click :guilabel:`for Camera`) for radiography measurement.
   - Move sample position to x-ray beam position shown by a mark on monitor.


By absorption scan
^^^^^^^^^^^^^^^^^^

   - Move to :ref:`EXDX measurement mode <edxd_mode>`.
   - Confirm 2TH is >10°.
   - Open 'Bluediamond' (:ref:`Bluediamond <bluediamond>` software).
   - Select 'IC2 or Diode' in Detector in Bluediamond, uncheck all others.
   - Open 'scan' on SAM Y (or Z)

   .. figure:: /images/operation/scan_launch.png
      :alt: scan_launch
      :width: 720px
      :align: center

   - Set scan parameters of 'Start', 'End' and '#Pts' (#Pts has to be odd number) (confirm 'Relative').

   .. figure:: /images/operation/scan_go.png
      :alt: scan_go
      :width: 300px
      :align: center

   - Click :guilabel:`Load&Go` to start scan.
   - Scan results will appear in the ':ref:`Bluediamond <bluediamond>`' window.