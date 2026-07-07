media.ccc.de recordings
==========================

.. image:: https://raw.githubusercontent.com/pretalx/pretalx-media-ccc-de/python-coverage-comment-action-data/badge.svg
   :target: https://htmlpreview.github.io/?https://github.com/pretalx/pretalx-media-ccc-de/blob/python-coverage-comment-action-data/htmlcov/index.html
   :alt: Coverage

This is a plugin for `pretalx`_ that provides an integration with media.ccc.de, allowing you to embed recordings on talk pages.

.. image:: https://github.com/pretalx/pretalx-media-ccc-de/blob/main/assets/screenshot.png?raw=true

Development setup
-----------------

1. Make sure that you have a working `pretalx development setup`_.

2. Clone this repository, eg to ``local/pretalx-media-ccc-de``.

3. Activate the virtual environment you use for pretalx development.

4. Run ``pip install -e .`` within this directory to register this application with pretalx's plugin registry.

5. Restart your local pretalx server. This plugin should show up in the plugin list shown on startup in the console.
   You can now use the plugin from this repository for your events by enabling it in the 'plugins' tab in the settings.

Development commands
~~~~~~~~~~~~~~~~~~~~

This plugin uses `just`_ as a task runner and `uv`_ for dependency management.
Run ``just`` with no arguments to list every available command. The most useful ones
are:

``just fmt``
    Auto-format and lint the code.

``just test``
    Run the full test suite with pytest.

Installing pretalx
~~~~~~~~~~~~~~~~~~~~

The tests need pretalx installed in the environment. ``just test`` handles this for
you: if pretalx cannot be imported, it installs the latest version from git before
running the test suite.

If you already have a development version of pretalx around (for example if you want
to test your changes against a specific commit or branch of pretalx), you can also
install pretalx up front yourself:

``just install-pretalx-local /path/to/pretalx``
    Install pretalx from a local checkout as an editable install.

``just install-pretalx``
    Install the latest pretalx from git (runs before tests if no pretalx is installed).


License
-------

Copyright 2018 Tobias Kunze

Released under the terms of the Apache License 2.0


.. _pretalx: https://github.com/pretalx/pretalx
.. _pretalx development setup: https://docs.pretalx.org/en/latest/developer/setup.html
.. _just: https://just.systems/
.. _uv: https://docs.astral.sh/uv/
