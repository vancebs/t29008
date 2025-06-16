# t29008

## Description
A multi-download tool to download Qualcomm device with 9008(EDL) based on **QShareServer** and **fh_loader**

## Supported OS
* Windows
* Linux (Tested on Ubuntu 24.04)

## Usage
```bash
parameters
    -vip|-v                          enable vip download
    -reboot-on-success|-r            reboot device when download success
    -trace-dir|-t <dir>              dir to save port_trace (default dir is "port_trace")
    -image-dir|-i <dir>              image dir
    -max-download-count|-n <count>   auto stop after n device is downloaded
    -prog|-p <filename>              prog file name (default is "prog_firehose_ddr.elf")
    -signeddigests|-sd <filename>    file name of signed digests (auto search if not set)
    -chaineddigests|-cd <filename>   file name of chained digests (auto search if not set)

i.e.
    python t29008.py -vip -reboot-on-success -trace-dir my_port_trace -image-dir vip_image
    python t29008.py -v -r -t my_port_trace -i vip_image
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

## Limitation
As a well known bug. fh_loader don't support sparse image with FILL type chunk.
