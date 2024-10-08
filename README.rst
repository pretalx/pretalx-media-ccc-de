media.ccc.de recordings
==========================

This is a plugin for `pretalx`_ that provides an integration with media.ccc.de, allowing you to embed recordings on talk pages.

.. image:: https://github.com/pretalx/pretalx-media-ccc-de/blob/main/assets/screenshot.png?raw=true

Development setup
-----------------

1. Make sure that you have a working `pretalx development setup`_.

2. Clone this repository, eg to ``local/pretalx-media-ccc-de``.

3. Activate the virtual environment you use for pretalx development.

4. Execute ``python setup.py develop`` within this directory to register this application with pretalx's plugin registry.

5. Execute ``make`` within this directory to compile translations.

6. Restart your local pretalx server. You can now use the plugin from this repository for your events by enabling it in
   the 'plugins' tab in the settings.


License
-------

Copyright 2018 Tobias Kunze

Released under the terms of the Apache License 2.0


.. _pretalx: https://github.com/pretalx/pretalx
.. _pretalx development setup: https://docs.pretalx.org/en/latest/developer/setup.html
