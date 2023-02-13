.. _radiography_mode:

Radiography measurement
-----------------------
On the PEC user interface,

1.	Click :guilabel:`for Camera` to open slits and to put filter.
2.	Confirm and/or move '2TH' to > 11°.
3.	Move camera IN 

.. figure:: /images/operation/switch_to_radiography_interface.png
   :alt: switch_to_radiography_interface
   :width: 720px
   :align: center

Open 'Manta Camera' shortcut on desktop. This will opend a small launcher window with two buttons :guilabel:`Manta Viewer` 
and :guilabel:`Cam Control`:

.. figure:: /images/mantacamera/main_screen.png
   :alt: switch_to_radiography_interface
   :width: 200px
   :align: center

Click :guilabel:`Manta Viewer` in the launcher window to launch the viewer window.

.. figure:: /images/mantacamera/viewer.png
   :alt: switch_to_radiography_interface
   :width: 600px
   :align: center

Click :guilabel:`Start` to start camera. Adjust the 'exposure, s' if needed.

Click :guilabel:`Cam Control` in the launcher window to launch camera image file saving control.

.. figure:: /images/mantacamera/control.png
   :alt: switch_to_radiography_interface
   :width: 700px
   :align: center

* Enter the 'File path' and the 'File name'. 
* To save the image, click :guilabel:`Save`.

.. note:: The File path for saving the data should be ``/net/pantera/data/16bmb/PEC/Data/``, 
          followed by the run number, eg. ``2022-1``, followed by beamtime category (GUP, etc.) and PI name.
.. note:: Be careful when copy-pasting the file path from the Windows Explorer into the file saving control.
          The file saving control uses forward-slashes ' / ', while windows exlorer uses back-slashes ' \\ '.