# pyRobotEyez
A simple python based command line video capture script

## usage

Command line Python webcam capture script, inspired by [RobotEyez](https://batchloaf.wordpress.com/2011/11/27/ultra-simple-machine-vision-in-c-with-roboteyes/)

```
usage: capture.py [-w WIDTH] [-h HEIGHT] [-f FILE] [--help] [--wait WAIT]
                  [--focus {0:5:255}]
                  [--no-flip NO_FLIP]

optional arguments:
  -w WIDTH, --width WIDTH
                        width of the image
  -h HEIGHT, --height HEIGHT
                        height of the image
  -f FILE, --file FILE  where to store the image (default capture.jpg)
  --help                show this help message and exit
  --wait WAIT           how many seconds to wait
  --focus {0:5:255,-1}
                        focus set point to set, -1 is autofocus
  --no-flip NO_FLIP     do not flip display image
  ```
