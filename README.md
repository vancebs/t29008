# t29008

## Description
A multi-download tool to download Qualcomm device with 9008(EDL) based on **QShareServer** and **fh_loader**

## Requirements
* Supported OS
  * Windows
  * Linux (Tested on Ubuntu 24.04)
* Python
  * version >= 3.12



## Usage
* Simple 1
  * Add t29008 to PATH
  * cd to the image dir
  * cmd: ```t29008``` or ```python t29008.exe```

* Simple 2
  * Copy t29008 to image directory.
  * Double-click t29008.

* More
  ```
  parameters
      -reboot-on-success|-r            reboot device when download success
                                       not set: no reboot
      -trace-dir|-t <dir>              dir to save port_trace
                                       not set: "port_trace" under current working directory
      -image-dir|-i <dir>              image dir
                                       not set: current working directory
      -max-download-count|-n <count>   auto stop after n device is downloaded
                                       not set: no limit
      -prog|-p <filename>              prog file name
                                       not set: "prog_firehose_ddr.elf" as default
      -vip|-v <on|off>                 on: enable vip download
                                       off: disable vip download
                                       not set: auto enabled if signeddigests and chaineddigests are detected
      -signeddigests|-sd <filename>    file name of signed digests
                                       not set: auto search if -vip not set or set to on
      -chaineddigests|-cd <filename>   file name of chained digests
                                       not set: auto search if -vip not set or set to on
  
  i.e.
      t29008
      t29008 -vip -reboot-on-success -trace-dir my_port_trace -image-dir vip_image
      t29008 -v -r -t my_port_trace -i vip_image
      t29008 -v -r -t my_port_trace -i vip_image -p prog_firehose_ddr.elf -sd DigestsSigned.bin.mbn -cd ChainedTableOfDigests.bin
  ```

## Build Binary
### Windows
  ```bash
  .\build.bat
  ```
  binary path: **dist_windows\t29008.exe**
### Linux
  ```bash
  ./build.sh
  ```
  binary path: **dist_linux/t29008**
