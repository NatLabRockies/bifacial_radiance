.. _installation:

Installation
============

Compatibility
~~~~~~~~~~~~~

bifacial_radiance is coded and tested in Windows, but can also work on Linux and Mac OSX, particularly after improvements in :ref:`whatsnew_0302` which solved some of the binary issues for gencumsky. However, the functionalities in Linux are still being improved, for example the GUI requires special QT installation described in (:issue:`130`:).


Video Instructions
~~~~~~~~~~~~~~~~~~

`https://youtu.be/4A9GocfHKyM <https://youtu.be/4A9GocfHKyM>`_  This video shows how to install the bifacial_radiance software and all associated softwares needed for Windows, but it may be slightly out of date. Instructions for Windows and Linux-based OS are shown below and are more current.


STEP 0: PREREQUISITES (Step 0)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
RADIANCE
--------

Windows:

* This software requires the previous installation of ``RADIANCE`` from https://github.com/LBNL-ETA/Radiance/releases.
 
* It's recommended to download and install the current stable release (5.3) from the Windows executable.

* Make sure you add Radiance to the system PATH so Python can interact with the Radiance program.


Linux/Mac OSX:

* For Linux/Mac OSX, you will need to install QT for the GUI to work properly. Installation and details described in (:issue:`131`:):

1. Install ``qt5-default`` from Ubuntu using ``apt``.
2. Get the official Radiance 5.3 source tarball with auxiliary libraries ``rad5R3all.tar.gz`` from  `RADIANCE <https://www.radiance-online.org/download-install/radiance-source-code/latest-release>`_ online  - do _not_clone the GitHub repo as it doesn't have the auxiliary libraries which you may also need. Finally extract the tarball.
3. You may also need to install ``csh`` and ``cmake`` 
4. Make directories where you want to install radiance, for example ``~/.local/opt/radiance``. Some users have reported that the installer for MacOS isn't descriptive about where it installs, and they have an easier time just choosing a location by pressing the "Change Install Location..." button in the "Installation Type" stage of the install. Then they source it in the bash/zsh_profile like so::

        export PATH=$HOME/bin/radiance/bin:$PATH
        export RAYPATH=.:$HOME/bin/radiance/lib
        export MANPATH=$HOME/bin/radiance/man
        export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/bin/radiance/lib
        export MDIR=$HOME/bin/radiance/lib
   
5. Read the README and run ``./makeall install clean`` and choose where you want ``bin`` and ``lib``

You can test it by rendering the daffodil.


Mac OSX:

1. Brew install xquartz (https://www.xquartz.org/)
2. Get radiance source from https://www.radiance-online.org/download-install/radiance-source-code/latest-release,
3. $ ./makeall install clean


Macbook Pro Notes:

Users have reported using bifacial_radiance on my MacBook pro, with installation instructions nearly the same as for Linux, except you must use conda and create a `~/.matplotlib/matplotlibrc` file with "backend : TkAgg" no quotes as the only command (https://matplotlib.org/users/customizing.html#the-matplotlibrc-file) or else you will get the Mac "python not a framework" error or a segmentation fault - both are known issues for matplotlib on Mac.

Things learned from RADIANCE on installation:

0. RADIANCE can use either x11 or Qt by using the `-o <device>` option if it's compiled with those devices

1. If you use `makeall` to build RADIANCE then Qt is not required but Xorg X11 is required, so

(a) in Linux::

    $ sudo apt install xorg

(b) on Mac install XQuartz (https://www.xquartz.org/)::

    $ brew install xquartz

2. You cannot use `makeall` to build RADIANCE with the Qt device, instead you must use `cmake` - I did not test this, but the Linux binaries on GitHub expect your system to have Qt-5.10 libraries in the usual place - if you try to use `makeall` to build with `-DHAS_QT` then you will get an error and `rvu`, `rpict`, etc won't compile :(

3. If you use `makeall` x11 is the default device so you don't need to explicitly call `-o x11` if you don't want to, but it doesn't hurt


Alternative Installation: Windows Subsystem for Linux:

1. You need the `Windows Subsystem for Linux (WSL) <https://docs.microsoft.com/en-us/windows/wsl/install-win10>`_
2. Activate  WSL and then install an x11 server like `VcXsrv <https://sourceforge.net/projects/vcxsrv/>`_, then make sure to add to ~/.profile::
 
        # set DISPLAY to output to Xserver
        export DISPLAY=:0.0
        export LIBGL_ALWAYS_INDIRECT=1
 
   Make sure you start the x11 server if needed by clicking XLaunch on the desktop. Click ok, ok, ok, finish should see it in the systray 
3. Install qt5-default in your linux::
   
   $ sudo apt install qt5-default

4. Download and extract the official RADIANCE tarball including the auxiliary library files called `rad5R3all.tar.gz <https://www.radiance-online.org/download-install/radiance-source-code/latest-release>`_, do NOT use the github repo, it does not have the auxiliary files 
   * There's an older version of radiance bundled with ubuntu, but we do not suggest using it since it's not as updated.
5. Read the readme for radiance, enter the extracted folder, decide where you want radiance to be installed (i.e. ``~/.local/opt/radiance/bin`` and ``~/.local/opt/radiance/lib``) and run::

        path/to/extracted/radiance $ ./makeall install clean


  Note: there’s no need for the Jaloxa binaries, because building from the official RADIANCE source on WSL builds all of the binaries such as falsecolor, genBSDF, genklemsamp, genskyvec, objpict, objview, ltview, and ltpict

6. Test radiance by rendering the daffodil in the extracted folder::

        path/to/extracted/radiance $ cd ray/obj/misc
        path/to/extracted/radiance/ray/obj/misc $ PATH=path/to/radiance/bin:$PATH rad -o x11 daf.rif
        rvu -vu 0 1 0 -vp 50 60 40 -vd 0 -1 -1 -vh 20 -vv 20 -dp 128 -ar 19 -ds 0 -dt .2 -dc .25 -dr 0 -ss 0 -st .5 -aa .3 -ad 256 -as 0 -av 0.5 0.5 0.5 -lr 6 -lw .003 -ps 8 -pt .16 -R daf.rif -o x11 -pe 1 daf.oct
   
   Note: Ignore the fatal IO error, radiance doesn’t handle closing the window gracefully
 
  
**Note: bifacial_radiance is not endorsed by or officially connected with the Radiance software package or its development team.**
  

PYTHON
-------
You will need python installed to run bifacial_radiance. We suggest using the latest release of `Anaconda with Python 3.11 <https://www.anaconda.com/download/>`_ . Anaconda will install ``Spyder`` to work with the python scripts, and also it will install ``Jupyter``, which is the tool we use for our `tutorial trainings <https://github.com/NREL/bifacial_radiance/tree/master/docs/tutorials>`_


Alternative Installation: Windows Subsystem for Linux:

1. Make sure your linux has python-3 and virtualenv::
 
        $ sudo apt install python3 virtualenv
 
2. Enter the clone and create a virtual environment, and target your desired python ::
 
        path/to/bifacial_radiance [master] $ virtualenv -p python3 venv
 

STEP 1
~~~~~~

The simplest option is to open a command prompt and run::

        pip install bifacial_radiance
        
       
An alternative which is shown in the Video Instructions, if you want to install bifacial_radiance in a local folder of your choosing and/or be able to modify the internal code to suit your needs, you can do the following:

* clone the bifacial_radiance repo to your local directory or download and unzip the .zip file
* navigate to the \bifacial_radiance directory using anaconda command line
* run:: 

        pip install -e .

The period ``.`` is required, the ``-e`` flag is optional and installs in development mode where changes to the `bifacial_radiance.py` files are immediately incorporated into the module if you re-start the python kernel)

For best compatibility, deploy in a new Anaconda environment, and run::

        pip install -r requirements.txt


Alternative Installation: Windows Subsystem for Linux:

1. Activate the virtualenv and install the requirements::
 
        path/to/bifacial_radiance [master] $ . venv/bin/activate  # the dot operator is the same as the source command
        (venv) path/to/bifacial_radiance [master] $ pip install -r requirements.txt
 


STEP 2
~~~~~~
Windows:

* Copy gencumulativesky.exe from the repo's ``/bifacial_radiance/data/`` directory and copy into your Radiance install directory.
  This is typically found in ``/program files/radiance/bin/``.  
 
Linux/Mac OSX:

* Copy the gencumulativesky executable (the one that does NOT end on .exe since that one is for Windows) from the repo's ``/bifacial_radiance/data/`` directory and copy into your Radiance install directory.
  This is typically found in ``/usr/local/radiance/bin/``. 


.. note::
        GenCumulativeSky is detailed in the publication "Robinson, D., Stone, A., Irradiation modeling made simple: the cumulative sky approach and its applications, Proc. PLEA 2004, Eindhoven 2004."   

        The gencumsky source is included in the repo's ``/bifacial_radiance/data/gencumsky`` directory along with a make_gencumskyexe.py script which builds the multi-platform gencumulativesky executables. More details on the use of this script in readme.txt or on thread (:issue:`182`).

We suggest you recompile the executable to make sure it works with your version of Linux, otherwise issues like (:issue:`182`) or (:issue:`268`) can happen. To recompile, navigate to bifacial_radiance\data\gencumsky folder, and type

        python make_gencumuskyexe.py

This will generate an updated gencumulativesky in this same folder. Place this executable on your Radiance/bin directory as instructed above.


STEP 3
~~~~~~
Create a local directory for storing your simulations and runs results. 
If run in the default directory, simulation results will be saved in the TEMP folder, but will also be overwritten with every run. We recommend to keep the simulation files (scene geometry, skies, results, etc) separate from the bifacial_radiance directory by creating a local directory somewhere to be used for storing those files.


STEP 4
~~~~~~
Reboot the computer
This makes sure the ``PATH`` is updated
