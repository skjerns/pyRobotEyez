from setuptools import setup

setup(name='pyRobotEyez',
      version='1.0',
      description='A simple webcam capture script',
      url='http://github.com/skjerns/pyRobotEyez',
      author='skjerns',
      author_email='nomail',
      license='GNU 2.0',
      install_requires=['monitorcontrol', 'opencv-python'],
      packages=['pyroboteyez'],
      zip_safe=False)
