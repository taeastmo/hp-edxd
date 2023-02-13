.. _edxd_mode:

EDXD measurement
----------------
On the PEC user interface,

1.	Move camera OUT 
2.	Click :guilabel:`Slits for EDXD` to narrow slits and to remove filter.
3.	Move Tip X to IN position 

.. important:: Tip X must be moved to OUT position when putting in and removing PE cell to avoid accidentally bumping the collimator.

EDXD data collation and viewing is done using the :ref:`hpMCA <hpMCA>` software:

1. Open 'hpMCA' from shortcut on desktop

.. figure:: /images/hpmca/hpmca_main_screen.png
   :alt: hpmca_main_screen
   :width: 720px
   :align: center

2. \ :menuselection:`File --> foreground --> open detector`.
3. Click :guilabel:`&OK`, keeping the default PV name.

.. note:: The EDXD detector PV name should be ``16bmb:aim_adc1``.

4. Find sample :ref:`Y, Z, <yz_position>` and :ref:`X, <x_position>` positions before starting EDXD data collection.

5. Start EDXD data acquisition (Refer to :ref:`hpMCA <hpMCA>` section for EDXD data acquisition and viewing).