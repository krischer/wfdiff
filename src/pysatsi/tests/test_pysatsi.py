#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pysatsi test suite.

Run with pysatsi.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2014
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/gpl.html)
"""
import inspect
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.testing.compare import compare_images as mpl_compare_images
import numpy as np
import os

from pysatsi import read_fault_plane_solutions


# Most generic way to get the data folder path.
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe()))), "data")

# Baseline images for the plotting test.
IMAGE_DIR = os.path.join(os.path.dirname(DATA_DIR), "baseline_images")


def reset_matplotlib():
    """
    Reset matplotlib to a common default.
    """
    # Set all default values.
    mpl.rcdefaults()
    # Force agg backend.
    plt.switch_backend('agg')
    # These settings must be hardcoded for running the comparision tests and
    # are not necessarily the default values.
    mpl.rcParams['font.family'] = 'Bitstream Vera Sans'
    mpl.rcParams['text.hinting'] = False
    # Not available for all matplotlib versions.
    try:
        mpl.rcParams['text.hinting_factor'] = 8
    except KeyError:
        pass
    import locale
    locale.setlocale(locale.LC_ALL, str('en_US.UTF-8'))


def images_are_identical(image_name, temp_dir, dpi=None):
    """
    Partially copied from ObsPy. Used to check images for equality.
    """
    image_name += os.path.extsep + "png"
    expected = os.path.join(IMAGE_DIR, image_name)
    actual = os.path.join(temp_dir, image_name)

    if dpi:
        plt.savefig(actual, dpi=dpi)
    else:
        plt.savefig(actual)
    plt.close()

    assert os.path.exists(expected)
    assert os.path.exists(actual)

    # Use a reasonably high tolerance to get around difference with different
    # freetype and possibly agg versions. matplotlib uses a tolerance of 13.
    result = mpl_compare_images(expected, actual, 5, in_decorator=True)
    if result is not None:
        print(result)
    assert result is None


def test_fault_plane_solutions_reading():
    """
    Tests the parsing of fault plane solution text files to pandas data
    frame objects.
    """
    # Define the expected data.
    test_files = [
        {"filename":  os.path.join(DATA_DIR, "example0D",
                                   "INPUT_example0D.txt"),
         "count": 150, "header": ["x", "y", "dip", "dip_angle", "rake"]},
        {"filename":  os.path.join(DATA_DIR, "example1D",
                                   "INPUT_example1D.txt"),
         "count": 1890, "header": ["x", "y", "dip", "dip_angle", "rake"]},
        {"filename":  os.path.join(DATA_DIR, "example2D",
                                   "INPUT_example2D.txt"),
         "count": 3256,
         "header": ["x", "y", "dip", "dip_angle", "rake"]},
        {"filename":  os.path.join(DATA_DIR, "example3D",
                                   "INPUT_example3D.txt"),
         "count": 7500,
         "header": ["x", "y", "z", "t", "dip", "dip_angle", "rake"]},
    ]

    for params in test_files:
        df = read_fault_plane_solutions(params["filename"])
        assert df.columns.tolist() == params["header"]
        assert len(df) == params["count"]
        assert df["x"].dtype.type is np.int32
        assert df["dip"].dtype.type is np.float64