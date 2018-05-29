# CppMicroServices Conan Build Script

This repository holds the [conan](https://www.conan.io/) build script for the [CppMicroServices](https://github.com/CppMicroServices/CppMicroServices) framework.

Currently the script is configured to download the `beta-release-3.3.0` branch of the CppMicroServices framework.

## Warning

This packaging is work in progress. For instance, only tested on Windows OS with Visual Studio 14 compiler at the moment.

## Usage

Declare the dependency

If you are using `conanfile.txt`:
```
[requires]
CppMicroServices/3.3.0@pollen/snapshot
```

If you are using `conanfile.py`:

```python
from conans import *

class MyProjectConan(ConanFile):
    # Either:
    requires = 'CppMicroServices/3.3.0@pollen/snapshot'
    # Or:
    def requirements(self):
        self.requires('CppMicroServices/3.3.0@pollen/snapshot')

    # ...
```

## Options

A full list of options and defaults can be found in [`conanfile.py`](conanfile.py)

```bash
# Example
conan install --build=missing \
              -o CppMicroServices:US_BUILD_SHARED_LIBS=ON \
              -o CppMicroServices:US_ENABLE_THREADING_SUPPORT=ON
```
