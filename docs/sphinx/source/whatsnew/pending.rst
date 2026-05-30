.. _whatsnew_060:

v0.6.0 (XXX XX, 2026)
------------------------
Major release

API Changes
~~~~~~~~~~~~~
* RadianceObj.set1axis() has new input `use_mtx` to trigger the gendaymtx cumulative workflow (:pull:`598`)
* RadianceObj.genCumSky() has new input `use_mtx` to trigger the gendaymtx cumulative workflow (:pull:`598`)
* RadianceObj.genCumSky1axis() has new input `use_mtx` to trigger the gendaymtx cumulative workflow (:pull:`598`)


Bug fixes
~~~~~~~~~
* Switch to accuracy='high' for some pytests to reduce variability (:pull:`594`)
* Modelchain .ini files can now include "accuracy: high" to specify high analysis accuracy level under the heading [analysisParamsDict] (:pull:`594`)
* Github pytests use an updated `RADIANCE distribution <https://github.com/LBNL-ETA/Radiance/releases/tag/rad6R0P2>`_ (:pull:`594`)

Enhancements
~~~~~~~~~~~~
* MetObj now has a new parameter MetObj.frequency, set at initialization to track time-series frequency. (:pull:`598`)
* new function MetObj.makeWEA to create a .wea file for gendaymtx simulations. (:pull:`598`)
* new function MetObj._makeTrackerMTX to create .WEA files for tracked simulations. (:pull:`598`)
* new function RadianceObj._cal_to_rad to call a .cal sky definition from a .rad file for cumulative simulation. (:pull:`598`)

Bug fixes
~~~~~~~~~


Documentation
~~~~~~~~~~~~~~

Contributors
~~~~~~~~~~~~
* Chris Deline (:ghuser:`cdeline`)