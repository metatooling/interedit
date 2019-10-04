========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis|
        |
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/interedit/badge/?style=flat
    :target: https://readthedocs.org/projects/interedit
    :alt: Documentation Status


.. |travis| image:: https://travis-ci.org/interdoc-edit-bot/interedit.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/interdoc-edit-bot/interedit

.. |version| image:: https://img.shields.io/pypi/v/interedit.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/pypi/interedit

.. |commits-since| image:: https://img.shields.io/github/commits-since/interdoc-edit-bot/interedit/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/interdoc-edit-bot/interedit/compare/v0.1.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/interedit.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/pypi/interedit

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/interedit.svg
    :alt: Supported versions
    :target: https://pypi.org/pypi/interedit

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/interedit.svg
    :alt: Supported implementations
    :target: https://pypi.org/pypi/interedit


.. end-badges

An example package. Generated with cookiecutter-pylibrary.

* Free software: MIT License

Installation
============

::

    pip install interedit

Documentation
=============


https://interedit.readthedocs.io/


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
