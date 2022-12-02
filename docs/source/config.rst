Configuration
=============

In the project root is the file `config.yml`. This file does most of the configuration.
The config file is also mirrored into a `config.mat` file.

After each run of calibrate or runner the file is freshly saved with the (new) values and also new indented.

The parameters are most of the time directly injected into the constructor of the relevant object.
Sometimes also in some special methods.

The file holds the configuration for all 3 pis at the same time, plus additional virtual hosts,
which can be usefull for debugging purposes, together with the `-h` flag.

In the following you can see the yaml file of one of the hosts.

.. code-block:: yaml

   rpi3: # the hostname this condig is used at
     ball: # the ball object conf
       hsv: # the hsv colors in between the ball form is searched
         lower: [110, 50, 50]
         upper: [130, 120, 120]
       max_radius: 20 # the maximal radius of the ball
       min_radius: 5 # the minimal radius of the ball
       morph_iterations: 1 # the amount of iterations the morphing is done (here closing)
     camera: # the camera object conf
       wb_gains: [1.30, 1.88] # the white balancing gains
       framerate: 60 # the framerate
       rotation: 0 # no rotation
       resolution_no: 1 # 320x240
     hoop: # the hoop object conf
       angle_offset: 0 # the offset which will be added on each angle
       center: [143, 80] # the center of the hoop
       center_dots: # the center of the marker to find the hoop
       - [181, 217]
       - [277, 136]
       - [0, 81]
       - [276, 32]
       hsv: # the lower and upper color of the markers to find the hoop
         lower: [150, 100, 50]
         upper: [180, 200, 200]
       min_radius_dots: 0 # the minimal radius of the marker
       morph_iterations: 0 # the amount of morphing itearations to do (here opening)
       radius: 142 # the radius of the found hoop
       radius_dots: [2, 4, 2, 2] # the radius of the found markers
     network: # the network object conf
       is_server: true # flag if this host is the server
       message_bytes: 2 # the amount of message bytes to send via ethernet and serial
       send_errors: true # flag if errors should be sent
       serial: # the serial object conf, can be omitted if this is not the server
         active: true # a flag if serial com should be used
         baud: 9600 # the baud rate
         com: /dev/serial0 # the file path the serial com is repesented by
         send_mode: 1 # which mode of sending should be used (not yet implemented)
       server_ip: '' # the ip of the server (best to be empty or localhost if this is the server)

This config can be several times in the same file, as long as the first line (the hostname) is different.
Some options are missing. For a full documentation (but the hoop) have a look at the object constructor signatures.
The hoop is config is also used in different class methods as well. Every function which uses `**kwargs` gets the
corresponding parts of the config array, fetched from yaml.

.. note::

   for better version control, it might be a good idea to split up the config file in one file per host in the future

For more advanced debugging have a look to the additional config params shown in :doc:`Advanced Debugging<debugging>`