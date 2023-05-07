Usage
=====

Calibration
-----------

To calibrate the application make sure you are in the project root folder in one of the pis and run

.. code-block:: sh

   python calibrate.py

To get (more) console output the `-v` flag is needed. Together with a hoop-search `-o`, a ball-search `-b` and
a white calibration `-w` the full command which you most of the time want to use is

.. code-block:: sh

   python calibrate.py -v -o -b -w

You can also specify the hsv color (only for the hoop so far) via the other flags. To see all of the available flags use:

.. code-block:: sh

   python calibrate.py --help

If the `-v` flag is set, there will be debug pictures dumped to `storage/calibration`

White-calibration
-----------------

Usually a white calibration is necessary everytime the lights change. This can also be introduced
through different sunlight intensity.

The white calibration is tries to messure the green and blue gains to finetune the color values.
Right now the white calibration takes a picture with arbitrary gains, takes a region of interest
in the middle of the image (cropping it) and averaging all red, blue and green values.

For best results the ROI of the picture should be very white, or at least grey. The white calibration
tries to adjust the gains that way, that it measures a gray image, instead of one with a one color overshoot.

For better convergence a p-controller is used to calculate the new gains to try.


Troubleshooting
---------------

Hoop or ball not found
**********************

If the hoop is not found have a look at the debug pictures `raw-rgb.png`, `raw-hsv.png`, `hoop-mask.png`
and the `hoop-colsplit` directories and make sure the masks are clean enough and the hsv values are set correctly.

See :py:meth:`src.ballandhoop.image.Image.color_split()` for more information.

.. note::

   The HSV values are taken as openCV interprets them (H: 0-180, S and V: 0-255 range), other applications might use
   different ranges to convert rgb to hsv e.g. gimp. Most common different one is H: 0-360, S and V: 0-1 or 0-100 range)

   If you messure the 'rgb' values inside `raw-hsv.png` you do not have to convert the color. It is the same way as
   opencv/python expects it.

There are markers in the mask, but the hoop is not found
   Have a look at the min_radius attributes in the config file and ajust them

I have too much noice in the hoop search / wrong hoop found
   Try to limiting your HSV range more, or increase the `morph_iteratrions` (opening operation) attribute in config file

The ball area mask is too split up
   Try to increase the `morph_iterations` (closing operation) in config file - it will try to connect the areas together

Camera out of memory error
**************************

Double check if the camera is connected to the rpis and the interface is activated in legacy mode.

Run application
---------------

To run the application make sure you are in the project root folder in one of the pis and run

.. code-block:: sh

   python runner.py

To get (more) console output the `-v` flag is needed.

You can also specify the ball color via the other flags. To see all of the available flags use:

.. code-block:: sh

   python runner.py --help

If the `-v` flag is set, there will be debug pictures dumped to `storage/debug/` from every 30th frame.

You can terminate the application through pressing Ctrl+C multiple times. After the application is closed result files
are written to `storage/result.mat` and `storage/result.yml` for easier plotting of the results (independent on `-v` flag).

Run application on all 3 pis
----------------------------

Do all the above steps for all 3 pis. Then first run the pi which has the serial connection and has the `is_server` flag.

Afterwards use the runner on the other 2 pis. If the clients disconnect at some point you can close the application
and restart it. They can reconnect.


