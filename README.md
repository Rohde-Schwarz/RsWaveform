# RsWaveform

[![Documentation Status](https://readthedocs.org/projects/rswaveform/badge/?version=latest)](https://rswaveform.readthedocs.io/en/latest/?badge=latest) [![Build Status](https://github.com/Rohde-Schwarz/RsWaveform/actions/workflows/tests.yml/badge.svg)](https://github.com/Rohde-Schwarz/RsWaveform/actions/) [![PyPI Versions](https://img.shields.io/pypi/pyversions/RsWaveform.svg)](https://pypi.python.org/pypi/RsWaveform) ![PyPI - Downloads](https://img.shields.io/pypi/dm/RsWaveform)  [![PyPI Status](https://img.shields.io/pypi/status/RsWaveform.svg)](https://pypi.python.org/pypi/RsWaveform) [![PyPI License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> Load, manipulate and save R&S waveform files

The RsWaveform package provides a convenient and easy-to-use software solution for creating and modifying waveform files that can be used with Rohde & Schwarz instruments, but it does not provide access to encrypted waveform files that require a license.

## Purpose

### What it does

The RsWaveform package is a software tool developed by Rohde & Schwarz that allows you to create waveform files that can be used with Rohde & Schwarz instruments. This tool can help you to easily create waveform files that match your specific needs, or to load existing waveform files in various formats such as wv, iqtar, and iqw, modify them, and store them again for future use.

### What it not does

The RsWaveform package does not have the capability to load encrypted waveform files that require a license. These waveform files can only be used with a licensed Rohde & Schwarz product, and cannot be modified or analyzed without the appropriate license.

## Installation

Install from pypi.org:

```sh
$ pip install RsWaveform
```

You need at least Python 3.8.

## Setup environment

To set up your environment, just run

```py 
pip install -r requirements-dev.txt
```

## Usage

```py
import RsWaveform
```

### Load waveform files

```py
import RsWaveform

filename = "tests/data/dummy.wv"
wv = RsWaveform.RsWaveform(file=filename)
# default loader + saver will be used which is currently a ".wv" type
# This is the same as wv = RsWaveform.RsWaveform(load=RsWaveform.wv.Load, save=RsWaveform.wv.Save, file=filename)
wv.data[0]
>> array([0.2 + 0.4j, 0.6 + 0.8j])
wv.meta[0]
>> {
    'type': 'SMU-WV',
    'copyright': 'Rohde & Schwarz',
    'comment': 'Test waveform file',
    'clock': 100000000.0,
    'marker': {'marker list 1': [[0, 1], [32, 0], [63, 0]],},
    'control_length': None,
    'control_list': {},
    'level offs': (2.220459, 0.0),
    'date': datetime.datetime(2023, 1, 5, 10, 3, 52),
    'control length': 2,
    'encryption_flag': False,
    'center_frequency': 1000000000.0,
    'scalingfactor': 1
}
```

### Save waveform files

```py
import RsWaveform
import numpy as np
import datetime

wv = RsWaveform.RsWaveform()  # default loader + saver will be used which is currently a ".wv" type
# This is the same as wv = RsWaveform.RsWaveform(load=RsWaveform.wv.Load, save=RsWaveform.wv.Save)
wv.data[0] = np.ones((2,)) + 1j * np.zeros((1,))
# Set values as dict
wv.meta[0].update({
    'type': 'SMU-WV',
    'copyright': 'Rohde & Schwarz',
    'level offs': (2.220459, 0.0),
    'date': datetime.datetime.now(),
    'clock': 100000000.0,
    'control length': 2,

})
# or use the meta data properties
wv.meta[0].comment = 'Test waveform file'
wv.meta[0].marker.update({'marker list 1': [[0, 1], [32, 0], [63, 0]]})
# save to file
wv.save(r"someFileName.wv")
```

### Load iqw files

```py
import RsWaveform

filename = "tests/data/dummy.iqw"
iqw = RsWaveform.Iqw(
    file=filename)  # default loader + saver will be used which is
# currently a ".iqw" type
# This is the same as iqw = RsWaveform.Iqw(load=RsWaveform.iqw.Load,
# save=RsWaveform.iqw.Save, file=filename)
iqw.data[0]
>> array([0.2 + 0.4j, 0.6 + 0.8j])
```

### Save iqw files

```py
import RsWaveform
import numpy as np

iqw = RsWaveform.Iqw()  # default loader + saver will be used which is
# currently a ".iqw" type
# This is the same as iqw = RsWaveform.Iqw(load=RsWaveform.iqw.Load,
# save=RsWaveform.iqw.Save)
iqw.data[0] = np.ones((2,)) + 1j * np.zeros((1,))
iqw.save(r"someFileName.iqw")  # save to file
```

### Load iqtar files

```py
import RsWaveform
import datetime

filename = "tests/data/dummy.iq.tar"
iqtar = RsWaveform.IqTar(file=filename)
# default loader + saver will be used which is
# currently a ".iqw" type
# This is the same as iqtar = RsWaveform.IqTar(load=RsWaveform.iqtar.Load,
# save=RsWaveform.iqtar.Save, file=filename)
iqtar.data[0]
>> array([0.2 + 0.4j, 0.6 + 0.8j])
iqtar.meta[0]
>> {
    'clock': 10000.0,
    'scalingfactor': 1.0,
    'datatype': 'float32',
    'format': 'complex',
    'name': 'Python iq.tar Writer (iqdata.py)',
    'comment': 'RS WaveForm, TheAE-RA',
    "datetime": datetime.datetime(2023, 3, 1, 10, 19, 37, 43312),
}

```

### Save iqtar files

```py
import RsWaveform
import datetime

iqtar = RsWaveform.IqTar()
# default loader + saver will be used which is
# currently a ".iqw" type
# This is the same as iqtar = RsWaveform.IqTar(load=RsWaveform.iqtar.Load,
# save=RsWaveform.iqtar.Save, file=filename)
iqtar.data[0] = np.ones((2,)) + 1j * np.zeros((1,))
# Set values as dict
iqtar.meta[0] = {
    'clock': 10000.0,
    'scalingfactor': 1.0,
    'datatype': 'float32',
    'format': 'complex',
    'name': 'Python iq.tar Writer (iqdata.py)',
    "datetime": datetime.datetime.now(),
}
# or use the meta data properties
iqtar.meta[0].comment = 'RS WaveForm, TheAE-RA'
# save to file
iqtar.save("somefilename.iq.tar")
```

### Digital signal processing utilites

The RsWaveform package provides also these convenience functions for digital
signal processing

- normalize
- calculate_peak - output as dB
- calculate_rms - output as dB
- calculate_par - output as dB
- convert_to_db - amplitude based

You can use them as following

```py
import RsWaveform
import numpy as np

data = RsWaveform.normalize(np.ones((2,)) + 1j * np.zeros((1,)))

RsWaveform.calculate_peak(data)
>> 0.0
RsWaveform.calculate_rms(data)
>> 0.0
RsWaveform.calculate_par(data)
>> 0.0
```

### Running the tests

To run the tests, run the following command:

```sh
$ pip install tox
$ tox -e test
```

This will run all the tests for the package and report any issues or failures. Make sure that you have installed the necessary dependencies before running the tests.

## Contributing

- Author: Carsten Sauerbrey (<carsten.sauerbrey@rohde-schwarz.com>)
- Author: Daniela Rossetto (<daniela.rossetto@rohde-schwarz.com>)

We welcome any contributions, enhancements, and bug-fixes. Open an [issue](https://github.com/Rohde-Schwarz/RsWaveform/issues) on [Github](https://github.com) and [submit a pull request](https://github.com/Rohde-Schwarz/RsWaveform/pulls).

### Code approval/review guidelines

In case you finished the work on your branch, create a pull request, describe (optionally) your changes in the pull request and set at least *one* of the authors mentioned above as code
reviewer. The closed branch should be deleted after merge.

Before approving a pull request, check for and discuss:

- Repetitive (copy & paste) code -> Could this be refactored/moved to a function?
- Stale / commented out functional code -> Could these artifacts be deleted?
- Duplication of existing functionality -> Could existing code already solve the adressed problem?
- Unused imports -> Could these imports be cleaned up?`
- File locations don't mirror their logical connection to a feature -> Could they be grouped within a logical unit (e.g. folder)?
- Outdated / needlessly complex python functionality -> Could this be solved by more modern python language features (e.g. itertools)?
- Is there a test for your functionality? -> add new test or modify an existing test.
