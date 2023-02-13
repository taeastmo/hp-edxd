.. _x_position:

Sample X position scan
----------------------

Sample X position can be adjusted by using intensity of sample or diffraction pattern. However, it is difficult to scan sample X with diffraction intensity of amorphous material. We recommend scanning sample X by using diffraction intensity of MgO ring. Followings are procedures:

   #. Move Y -1.5 mm from sample Y center to see diffraction patterns of MgO.
   #. Add :ref:`ROIs. <rois>` for MgO peaks. 
   #. Then, move Y -1.3 mm position from sample Y center (+0.2 mm Y from -1.5 mm position or move back to the sample Y center and move -1.3 mm Y).
   #. In order to connect EPICS motor control and MCA software, please click :guilabel:`ON` in 'Scan1 MCA Trigger Toggle', and then input data acquisition time for each step in 'Preset Real Time' (typically, 2-5 second).
   #. Open 'Scan' in 'SAM X', and input parameters (typically, Start=-1, End=1, #Pts=21).
   #. Then, click :guilabel:`Load&Go` to start scan.
   #. Sample X center is the location where MgO diffraction intensity is the minimum.

   .. note:: After the scan, please do not forget to 'OFF' 'Scan1 MCA Trigger Toggle', and input 0 in 'Preset Real Time'.

.. figure:: /images/operation/mgo_scan.png
   :alt: mgo_scan
   :width: 350px
   :align: center

.. figure:: /images/operation/scan_trigger.png
   :alt: scan_trigger
   :width: 720px
   :align: center
