from setuptools import Extension, setup
from Cython.Build import cythonize

ext_modules = [
    Extension("proxy_native",
              sources=["proxy.pyx",],
              # libraries=["lib\*"],
              include_dirs = ["include"]
              )
]

setup(name="ProxyNative",
      ext_modules=cythonize(ext_modules))