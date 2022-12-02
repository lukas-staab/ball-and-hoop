========================================
Local development and advanced debugging
========================================

Local development
=================

to be able to develope this codebase on a local (non-pi) machine you need to do some extra steps.

- make sure you have a Serial port, or a deactivated serial communication (see :doc:`config`)
- make sure you have mocked video material from a pi to make your calculations on (more on that later)

If you want better code completion it is advised also to install the `picamera` module.
Usually this is not possible, but there is a way to achieve it.

.. code-block:: shell

   export READTHEDOCS=True
   pip install picamera # should work now

Getting Mocked Video material
=============================

To record a 'video' there is the `debug.py` file, to take a video you can use the following command:

.. code-block:: sh

   python debug.py --vid dirname 300 60 1

Where
- dirname is the name of the directory in `storage/faker/`
- 300 is the amount of frames which will be collected, defaults to 10
- 60 is the framerate the frames will be collected, defaults to 60
- 1 is the resolution_no the pictures will be taken in, defaults to 1 (320x240)

To use this `videos` (only a lot of pictures which will be interpreted as a raw video stream) add the following config:

.. code-block:: yaml

   lyoga: # my pc hostname
     # some parts omitted
      camera:
         faker_path: fetch/rpi3.lan/faker/runtest # loads this video directory instead of the camera (for the ball search)
         # some parts omitted
      hoop:
         # some parts omitted
         faker_path: storage/cheat2.png # one picture which will be used for the configure routine (hoop+ball once)
      network:
         is_server: true
         serial:
            active: false # has to be false if you do not have a serial com

