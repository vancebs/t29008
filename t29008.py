import os.path
import signal
import sys

from T2Edl import T2Edl
from T2EdlUi import T2EdlUi


def show_help():
    print('\n'.join((
        'parameters',
        '    -vip|-v                          enable vip download',
        '    -reboot-on-success|-r            reboot device when download success',
        '    -trace-dir|-t <dir>              dir to save port_trace (default dir is "port_trace")',
        '    -image-dir|-i <dir>              image dir',
        '    -max-download-count|-n <count>   auto stop after n device is downloaded',
        '    -prog|-p <filename>              prog file name (default is "prog_firehose_ddr.elf")',
        '    -signeddigests|-sd <filename>    file name of signed digests (auto search if not set)',
        '    -chaineddigests|-cd <filename>   file name of chained digests (auto search if not set)',
        '',
        'i.e.',
        '    python t29008.py -vip -reboot-on-success -trace-dir my_port_trace -image-dir vip_image',
        '    python t29008.py -v -r -t my_port_trace -i vip_image'
    )))


def show_error(msg: str):
    print(msg)
    print('')
    show_help()


def main() -> int:
    is_vip = False
    reboot_on_success = False
    trace_dir = 'port_trace'
    image_dir: str|None = None
    max_download_count: int = 0
    prog: str = 'prog_firehose_ddr.elf'
    signed_digests: str|None = None
    chained_digests: str|None = None

    # load parameter
    args = [arg for arg in sys.argv[1:]]
    while len(args) > 0:
        match args[0]:
            case '-vip' | '-v':
                is_vip = True
                args = args[1:]
            case '-reboot-on-success' | '-r':
                reboot_on_success = True
                args = args[1:]
            case '-trace-dir' | '-t':
                if len(args) < 2:
                    show_error('trace dir not provided!!')
                    return -1
                trace_dir = args[1]
                args = args[2:]
            case '-image-dir' | '-i':
                if len(args) < 2:
                    show_error('image dir not provided!!')
                    return -1
                image_dir = args[1]
                args = args[2:]
            case '-max-download-count' | '-n':
                if len(args) < 2:
                    show_error('download count not provided!!')
                    return -1
                if not args[1].isdigit():
                    show_error('download count should be in digit!!')
                    return -1
                max_download_count = int(args[1])
                args = args[2:]
            case '-prog' | '-p':
                if len(args) < 2:
                    show_error('prog file name not provided!!')
                    return -1
                prog = args[1]
                args = args[2:]
            case '-signeddigests' | '-sd':
                if len(args) < 2:
                    show_error('signeddigests file name not provided!!')
                    return -1
                signed_digests = args[1]
                args = args[2:]
            case '-chaineddigests' | '-cd':
                if len(args) < 2:
                    show_error('chaineddigests file name not provided!!')
                    return -1
                chained_digests = args[1]
                args = args[2:]
            case _:
                show_error(f'unknown parameter: "{args[0]}"')
                return -1

    if image_dir is None:
        show_error('image dir not provided')
        return -1

    # verify trace_dir
    if os.path.exists(trace_dir) and not os.path.isdir(trace_dir):
        show_error(f'cannot create trace dir: {trace_dir}')
        return -1
    os.makedirs(trace_dir, exist_ok=True)

    # create instance
    instance = T2Edl(image_dir=image_dir,
                     is_vip=is_vip,
                     reboot_on_success=reboot_on_success,
                     trace_dir=trace_dir,
                     max_download_count=max_download_count,
                     prog=prog,
                     signed_digests=signed_digests,
                     chained_digests=chained_digests)
    instance.watch(T2EdlUi())

    # install ctrl_c handler
    def ctrl_c_handler(signum, frame):
        nonlocal instance
        instance.stop()

    signal.signal(signal.SIGINT, ctrl_c_handler)

    # start
    instance.start()


if __name__ == '__main__':
    sys.exit(main())