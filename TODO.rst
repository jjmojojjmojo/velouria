====
TODO
====

This document holds outstanding issues - mostly used as a conveient way to
log technical debt and quirks while working on moving the development forward.

0.1
===

Test Edge Cases: X not running
------------------------------
If X isn't running, or the DISPLAY variable isn't set, the errors from GTK are counter-intuitive.

Tests need to be performed to see what happens during this use case, and add check code in the main application entry point to handle it.

Flash
-----
Macromedia flash is not available by default. This may be fixable with a system packge.

FIXED: run:

::
    
    $ sudo apt-get install flashplugin-nonfree
    
and restart velouria.

Notify User If velouria.conf Can't Be Found
-------------------------------------------
If the user doesn't have a velouria.conf file in any of the usual locations, the application should notify the user.

Default Configuration
---------------------
If no velouria.conf can be found, load a configuration that shows off/tests the features of the app.

Command-Line Options
--------------------
The user should be able to pass a few command-line options to configure the application at runtime. Specifically:

- specify a velouria.conf file
- where to write the log file
- set the log level

Logging
-------
All debugging and other useful input should be routed to use the built-in logging mechanism provided by python.

Packaging 
---------
Besides a python egg, the app should be distributable as a system package (target apt at minimum).

Binary Distribution
-------------------
Due to the many dependencies and the current requirement of a bleeding-edge PPA, a binary distribution that bundles all of the libraries would be ideal.

New Slide: Rotate Images Within A Directory
-------------------------------------------
Add a slide where you specify a directory, and it cycles through each image in the directory every time its displayed.
