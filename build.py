from Cython.Build import cythonize
from setuptools import setup
from setuptools.extension import Extension

setup(
  name='parser',
  version='0.1.0',
  description='A package for parsing and analyzing SQL injection payloads using machine learning techniques.',
  author='Dwi Mulia Mokoginta',
  package_dir={'parser': 'src/parser'},
  ext_modules=cythonize(
    [Extension('_core', ['src/parser/_core.pyx'])],
    compiler_directives={
      'language_level': 3,
      'boundscheck': False,
      'wraparound': False,
    },
  ),
)
