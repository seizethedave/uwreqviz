from distutils.core import setup
from pip.req import parse_requirements

requirements = parse_requirements("requirements.txt")

setup(
 name='uwreqviz',
 version='0.9',
 py_modules=['uwreqviz'],
 install_requires=[str(r.req) for r in requirements]
)

