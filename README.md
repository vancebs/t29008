# t29008

## Description
A multi-download tool to download Qualcomm device with 9008(EDL) based on **QShareServer** and **fh_loader**

## Requirements
* Supported OS
  * Windows
  * Linux (Ubuntu 18.04 +)
* Python
  * version >= 3.8

## Install
* **Windows**
  ```
  git clone https://github.com/vancebs/t29008.git
  cd t29008
  .\build.bat
  ```
  add **"\<t29008 dir>\dist_windows"** to system environment **PATH**
* **Linux**
  ```bash
  git clone https://github.com/vancebs/t29008.git
  cd t29008
  ./build.sh
  echo >> "export PATH=$PWD/dist_linux:$PATH" >> ~/.bashrc  # add to PATH
  ```
**NOTE: exe will not be delivered by release. Because there are dependence issues with PyInstaller generated exe.
Please follow the steps above to generate exe locally.** 

## Usage
### Scene 1 (easy to use)
1. ```t29008 -i <image dir> -t <trace dir> -r```
2. plug in devices with edl mode ...
3. ```ctrl + c``` to stop

### Scene 2 (easy to use)
1. cd to **\<image dir>**
2. cmd: ```t29008```
3. plug in devices with edl mode ...
4. ```ctrl + c``` to stop

### Scene 3 (easy to use without console)
1. Copy the binary (```dist_linux/t29008``` or ```dist_windows/t29008.exe```) to **\<image dir>**.
2. Double-click t29008.
3. plug in devices with edl mode ...
4. ```ctrl + c``` to stop

### Advanced
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

exit
    ctrl + c

i.e.
    t29008
    t29008 -vip -reboot-on-success -trace-dir my_port_trace -image-dir vip_image
    t29008 -v -r -t my_port_trace -i vip_image
    t29008 -v -r -t my_port_trace -i vip_image -p prog_firehose_ddr.elf -sd DigestsSigned.bin.mbn -cd ChainedTableOfDigests.bin
```
