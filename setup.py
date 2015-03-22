import setuptools
from pyrapt.version import Version

setuptools.setup(name='pyrapt',
	version=Version('0.0.1').number,
	description='PyRapt - Python implementation of RAPT (Robust Algorithm for Pitch Tracking)',
	long_description=open('README.md').read().strip(),
	author='Daniel Gaspari',
	author_email='daniel.gaspari@gmail.com',
	url='https://github.com/dgaspari/pyrapt',
	py_modules=['pyrapt'],
	install_requires=[],
	license='MIT License',
	zip_safe=False,
	keywords=['pitch','audio','dsp'],
	classifiers=[]
)
