Liquid/amorphous structure measurement
--------------------------------------
A python program 'multiangle.py' is available for automatic data acquisition of EDXD pattern with varying 2θ angle.

- Open the python program by running 'multiangle.bat' from the desktop shortcut.

.. figure:: /images/operation/multiangle_setup.png
   :alt: multiangle_setup
   :width: 720px
   :align: center

You have the following 3 options:

   1.	Create a new setup automatically by clicking Setup in main window. In the pop-up window enter desired q-range and usable E range, and % overlap for the measurements. The built in algorithm will calculate optimal 2theta angles and populate the main window.

   .. figure:: /images/operation/multiangle_automatic.png
      :alt: multiangle_automatic
      :width: 320px
      :align: center

   2.	Load previously saved setup, click :guilabel:`Load` in main window
   3.	Add 2-theta angles manually by clicking :guilabel:`Add` in the main window for each angle.

Adjust the slit sizes and exposure times for each 2-theta 

   .. csv-table:: Input paramters description
      :header: "Setting", "Description"
      :widths: 50, 100
      :file: tables/table6_aedxd_settings.csv


If you want to repeat measurement, you can set 'Iterations' = 2 or higher.

.. important:: Confirm the following: 

   - 'Camera Vpos' = 110, 'Beamstop' = OUT, 'Tip X' = 0
   - 'Scan1 MCA Trigger Toggle' = OFF (nothing in line 2) Both 'Preset Real Time' and 'Preset Live Time' = 0
   - Slit and Filter setup is 'EDXD' condition ('Filter' = 0, slit size is small) 'position of sample is correct'.

Then, in :ref:`hpMCA`:

   #. Make sure file number is set to auto-increment
   #. Open \ :menuselection:`File --> Preferences`
   #. In preferences, please check 'yes' for 'autosave when acquisition stopped'. 
      (hpMCA will save file for each angle data with the name suffix of '_001', '_002'...).

Then, to start multiangle measurement, 

   - On Multiangle control window, click :guilabel:`Run` 

.. important:: After finishing the Multiangle collection, please do not forget to check 'no' for 'autosave when acquisition stopped'.

If you want to stop the Multiangle measurement, click :guilabel:`Stop`.