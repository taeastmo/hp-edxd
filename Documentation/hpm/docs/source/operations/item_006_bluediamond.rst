
.. _bluediamond:

Bluediamond
-----------
The Java-based HPCAT Bluediamond software is a real-time scan viewer program. The user 
shortcut can be found on the Windows desktop. If the software is started fresh, 
go to \ :menuselection:`Configuration --> open` to open the input configuration file named :file:`16BMB.txt` 
in the :file:`C:\\HPCAT Software` directory.  Note that this directory is local, but can 
be any directory in the network.  The software is straightforward to use and most 
of the menu items are self-instructing.

Various detectors can be displayed in the scan:

   - Beam intensity monitor by 'Ion Chamber 1' placed at the entrance of BMB hutch.
   - Beam intensity monitor by 'Ion Chamber 2' (used only in absorption density measurement).
   - Beam intensity monitor by 'IC2 or Diode' placed at the downstream of sample. This is mainly used for scanning sample Y and/or Z position by absorption contrast.
   - Intensity of ROI in MCA software. This is mainly used for scanning sample :ref:`X position <x_position>` in EDXD measurement. 

.. Note:: The labels for these detectors can change based on the names of the ROIs. Bluediamond only refreshes the names for the detectors when it is started. If you change the name of the ROI in hpMCA the names will not be updated in Bluediamond until it is restarted.

To use line cursors (two vertical and two horizontal), select menu \ :menuselection:`Util --> Markers --> Reset`. Left and right cursors can be dragged.
The cursor feature is useful for graphical determination of the FWHM and peak center position. You can move sample position by clicking :guilabel:`Move` button at the 'Center' in the left column.

.. figure:: /images/operation/bluediamond_interface.png
   :alt: bluediamond_interface
   :width: 640px
   :align: center 