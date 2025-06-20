import os.path
import signal
import sys
from typing import Union, Sequence

from Application import Application
from T2Edl import T2Edl
from T2EdlUi import T2EdlUi


def show_help():
    print('\n'.join((
        'parameters',
        '    -reboot-on-success|-r            reboot device when download success',
        '                                     <not set>: no reboot',
        '    -trace-dir|-t <dir>              dir to save port_trace',
        '                                     <not set>: "port_trace" under current working directory',
        '    -image-dir|-i <dir>              image dir',
        '                                     <not set>: current working directory',
        '    -max-download-count|-n <count>   auto stop after n device is downloaded',
        '                                     <not set>: no limit',
        '    -prog|-p <filename>              prog file name',
        '                                     <not set>: "prog_firehose_ddr.elf" as default',
        '    -vip|-v <on|off>                 on: enable vip download',
        '                                     off: disable vip download',
        '                                     <not set>: auto enabled if signeddigests and chaineddigests are detected',
        '    -signeddigests|-sd <filename>    file name of signed digests',
        '                                     <not set>: auto search if -vip not set or set to on',
        '    -chaineddigests|-cd <filename>   file name of chained digests',
        '                                     <not set>: auto search if -vip not set or set to on',
        '    -disable-zeroout|-dz             disable <zeroout> tag support',
        '                                     <not set>: enabled for non VIP downloading',
        '    -disable-erase|-de               disable auto erasing modemst1 and modemst2',
        '                                     <not set>: modemst1 & modemst2 are erased for non VIP downloading'
        '',
        'exit',
        '    ctrl + c',
        '',
        'i.e.',
        '    t29008',
        '    t29008 -vip -reboot-on-success -trace-dir my_port_trace -image-dir vip_image',
        '    t29008 -v -r -t my_port_trace -i vip_image',
        '    t29008 -v -r -t my_port_trace -i vip_image -p prog_firehose_ddr.elf -sd DigestsSigned.bin.mbn -cd ChainedTableOfDigests.bin'
    )))


def show_error(msg: str):
    print(msg)
    print('')
    show_help()


def verify_args_count(args: Sequence[str], size: int, err_msg: str) -> bool:
    if len(args) < size:
        show_error(err_msg)
        return False
    return True


def launch(
        reboot_on_success = False,
        trace_dir = 'port_trace',
        image_dir: str = Application.get().working_dir(),
        max_download_count: int = 0,
        prog: str = 'prog_firehose_ddr.elf',
        is_vip: Union[bool, None] = None,
        signed_digests: Union[str, None] = None,
        chained_digests: Union[str, None] = None,
        disable_zeroout: bool = False,
        disable_erase: bool = False):
    os.makedirs(trace_dir, exist_ok=True)

    # create instance
    instance = T2Edl(image_dir=image_dir,
                     reboot_on_success=reboot_on_success,
                     trace_dir=trace_dir,
                     max_download_count=max_download_count,
                     prog=prog,
                     is_vip=is_vip,
                     signed_digests=signed_digests,
                     chained_digests=chained_digests,
                     disable_zeroout=disable_zeroout,
                     disable_erase=disable_erase)
    instance.watch(T2EdlUi())

    # install ctrl_c handler
    def ctrl_c_handler(signum, frame):
        nonlocal instance
        instance.stop()

    signal.signal(signal.SIGINT, ctrl_c_handler)

    # start
    instance.start()


def main() -> int:
    reboot_on_success = False
    trace_dir = 'port_trace'
    image_dir: str = Application.get().working_dir()
    max_download_count: int = 0
    prog: str = 'prog_firehose_ddr.elf'
    is_vip: Union[bool, None] = None
    signed_digests: Union[str, None] = None
    chained_digests: Union[str, None] = None
    disable_zeroout: bool = False
    disable_erase: bool = False

    # load parameter
    args = [arg for arg in sys.argv[1:]]
    while len(args) > 0:
        param = args[0]
        if param in ('-reboot-on-success', '-r'):
            reboot_on_success = True
            args = args[1:]
        elif param in ('-trace-dir', '-t'):
            if not verify_args_count(args, 2, 'trace dir not provided!!'):
                return -1
            trace_dir = args[1]
            args = args[2:]
        elif param in ('-image-dir', '-i'):
            if not verify_args_count(args, 2, 'image dir not provided!!'):
                return -1
            image_dir = args[1]
            args = args[2:]
        elif param in ('-max-download-count', '-n'):
            if not verify_args_count(args, 2, 'download count not provided!!'):
                return -1
            if not args[1].isdigit():
                show_error('download count should be in digit!!')
                return -1
            max_download_count = int(args[1])
            args = args[2:]
        elif param in ('-prog', '-p'):
            if not verify_args_count(args, 2, 'prog file name not provided!!'):
                return -1
            prog = args[1]
            args = args[2:]
        elif param in ('-vip', '-v'):
            if not verify_args_count(args, 2, 'vip on/off not provided!!'):
                return -1
            is_vip = args[1] == 'on'
            args = args[2:]
        elif param in ('-signeddigests', '-sd'):
            if not verify_args_count(args, 2, 'signeddigests file name not provided!!'):
                return -1
            signed_digests = args[1]
            args = args[2:]
        elif param in ('-chaineddigests', '-cd'):
            if not verify_args_count(args, 2, 'chaineddigests file name not provided!!'):
                return -1
            chained_digests = args[1]
            args = args[2:]
        elif param in ('-disable-zeroout', '-dz'):
            disable_zeroout = True
        elif param in ('-disable-erase', '-de'):
            disable_erase = True
        else:
            show_error(f'unknown parameter: "{args[0]}"')
            return -1

    if image_dir is None:
        show_error('image dir not provided')
        return -1

    # verify trace_dir
    if os.path.exists(trace_dir) and not os.path.isdir(trace_dir):
        show_error(f'cannot create trace dir: {trace_dir}')
        return -1

    # launch
    launch(
        reboot_on_success=reboot_on_success,
        trace_dir=trace_dir,
        image_dir=image_dir,
        max_download_count=max_download_count,
        prog=prog,
        is_vip=is_vip,
        signed_digests=signed_digests,
        chained_digests=chained_digests,
        disable_zeroout=disable_zeroout,
        disable_erase=disable_erase)

    return 0


if __name__ == '__main__':
    sys.exit(main())