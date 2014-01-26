=========================
Installation Instructions
=========================

Dependencies
============

The latest GTK is required, which is only being released on a PPA until Ubuntu 14.04 comes out.

::
    
    $ sudo add-apt-repository ppa:gnome3-team/gnome3 
    $ sudo apt-get update

::
    
    $ sudo apt-get install python-gi gir1.2-gtk-3.0 gir1.2-webkit-3.0 gir1.2-webkit2-3.0 python-gi-cairo
    
    
    
Development Environment
=======================
Primary development of the application is done on Mac OS X, using an Ubuntu VM running in VirtualBox.

Additional Deps:

::
    
    $ sudo apt-get install xorg fvwm python-pip
    $ sudo pip install ipython ipdb
    
For testing, we use an installation of X windows and FVWM for window management (the app is run full-screen, and can be used without a window manager, but it's useful for messing around).

pip is useful for installing python packages. 

ipython and ipdb are a special variant of the python interpreter and PDB, respectively. They are useful for exploring the GObject API during R&D, prototyping and routine debugging.

Everything is set up for you (the X init bits to use FVWM, a startx script) if you use the apt packages to install into the VM. 

Running code is simply a matter of logging into the VM console directly and running:

::
    
    $ startx
    
Then, from an SSH login, setting the :code:`$DISPLAY` environment variable and 
executing the code:

::
    
    $ export $DISPLAY=":0"
    $ python example.py
    


.. note::
   I get "user is not authorized to run X server" when trying to run startx from an SSH login. I think this can be corrected, and then the setup steps can be put into a single shell script.
   

