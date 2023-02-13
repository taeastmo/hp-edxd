

Ultrasound measurement
----------------------

A GUI porgram sonicPy is used for the ultrasound measurement. SonicPy allows to automatically record ultrasound ultrasound waveforms from the oscilloscope with varying exitation wave frequencies.

Before beginning, create a folder named **US** in your data folder where the ultrasound data will be saved to. 

1. Open sonicPy by running the **ultrasound measurement** shortcut of the desktop. 

   .. figure:: /images/us_measurement/start_screen.png
      :alt: ultrasound_measurement_start_screen
      :width: 720px
      :align: center

   .. important:: Check that the Scope-Instrument is DPO5104 and AFG-Instrument is AFG3251. If something else is displayed it means that the program could not communicate with the hardware. Check that the oscilloscope and the function generator are both powered on.

2. Check and update if needed the following settings values:
   
   .. csv-table:: Scope settings
      :header: "Settings", "Value"
      :widths: 50, 100
      :file: tables/table2_scope_settings.csv

   .. csv-table:: AFG settings
      :header: "Settings", "Value"
      :widths: 50, 100
      :file: tables/table4_afg_settings.csv

   .. csv-table:: Scan settings
      :header: "Settings", "Value"
      :widths: 50, 100
      :file: tables/table3_us_scan_settings.csv

   .. csv-table:: Save data settings
      :header: "Settings", "Value"
      :widths: 50, 100
      :file: tables/table5_us_save_data_settings.csv

3. To check the ultrasound signal level, clear the scope and acquire a new ultrasound waveform by clicking :guilabel:`Erase + ON` above the waveform plot.

   .. figure:: /images/us_measurement/waveform_acquired.png
      :alt: waveform_acquired
      :width: 720px
      :align: center   


   .. note:: Scope Vertical scale may need to be adjusted depending on the signal level to avoid saturation and to optimize the oscilloscope's dynamic range relative to the signal level.


4. Set the 'Next file #' zero, if needed; and click :guilabel:`Go` in the Scan panel. The the frequency sweep will start and conclude on its own. To interrupt the scan mid-way click :guilabel:`Go` again. 

   .. important:: Remember to reset Next file # back to 0 before each scan.

