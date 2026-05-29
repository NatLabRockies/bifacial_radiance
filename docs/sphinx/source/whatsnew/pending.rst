.. _whatsnew_060:

v0.6.0 (XXX XX, 2026)
------------------------
Major release

API Changes
~~~~~~~~~~~~~
* RadianceObj.set1axis() has new input `use_mtx` to trigger the gendaymtx cumulative workflow
* RadianceObj.genCumSky() has new input `use_mtx` to trigger the gendaymtx cumulative workflow
* RadianceObj.genCumSky1axis() has new input `use_mtx` to trigger the gendaymtx cumulative workflow


Enhancements
~~~~~~~~~~~~
* MetObj now has a new parameter MetObj.frequency, set at initialization to track time-series frequency.
* new function MetObj.makeWEA to create a .wea file for gendaymtx simulations.
* new function MetObj._makeTrackerMTX to create .WEA files for tracked simulations.
* new function RadianceObj._cal_to_rad to call a .cal sky definition from a .rad file for cumulative simulation.

Bug fixes
~~~~~~~~~


Documentation
~~~~~~~~~~~~~~

Contributors
~~~~~~~~~~~~
* Chris Deline (:ghuser:`cdeline`)