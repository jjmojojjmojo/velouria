====
TODO
====

This document holds outstanding issues - mostly used as a convenient way to
log technical debt and quirks while working on moving the development forward.

0.1
===

Test Edge Cases: X not running
------------------------------
If X isn't running, or the DISPLAY variable isn't set, the errors from GTK are counter-intuitive.

Tests need to be performed to see what happens during this use case, and add check code in the main application entry point to handle it.

**FIXED:** added catch for RuntimeError that is thrown when X isn't available.

Flash
-----
Macromedia flash is not available by default. This may be fixable with a system package.

**FIXED:** run:

::
    
    $ sudo apt-get install flashplugin-nonfree
    
and restart velouria.

Notify User If velouria.conf Can't Be Found
-------------------------------------------
If the user doesn't have a velouria.conf file in any of the usual locations, the application should notify the user.

**FIXED:** added check for no parsed files to ConfigParser.read().

Default Configuration
---------------------
If no velouria.conf can be found, load a configuration that shows off/tests the features of the app.

**WONT FIX:** better to alert the user than do weird stuff.

Version Storage For Display
---------------------------
Find a good way to store, in a single place, the VERISON constant of the application.

See this TriZPUG thread for ideas: https://mail.python.org/pipermail/trizpug/2014-January/002320.html

**FIXED:** using Chris Calloway's suggestion, added :code:`VERSION=pkg_resources.get_distribution("velouria").version` to the main package.

Command-Line Options
--------------------
The user should be able to pass a few command-line options to configure the application at runtime. Specifically:

- specify a velouria.conf file
- where to write the log file
- set the log level

**DONE.** See :code:`velouria -h` for details.

Logging
-------
All debugging and other useful input should be routed to use the built-in logging mechanism provided by python.

**DONE.**

Packaging 
---------
Besides a python egg, the app should be distributable as a system package (target apt at minimum).

Binary Distribution
-------------------
Due to the many dependencies and the current requirement of a bleeding-edge PPA, a binary distribution that bundles all of the libraries would be ideal.

Signal Control
--------------
Figure out how to receive signals from the operating system (eg SIGHUP) and map to each of the available actions, plus reloading the config file.

**COMPLETE.** Implemented in a slightly different manner (used a unix domain socket instead of signals to provide flexibility.

Also, a SIGINT (ctrl-C) handler is implemented to shutdown the app.

Signal Control Script
---------------------
A command-line convenience application that sends signals to the main app. 

**COMPLETE.** Implemented in a slightly different manner (used a unix domain socket instead of signals to provide flexibility.)

New Slide: Rotate Images Within A Directory
-------------------------------------------
Add a slide where you specify a directory, and it cycles through each image in the directory every time its displayed.
