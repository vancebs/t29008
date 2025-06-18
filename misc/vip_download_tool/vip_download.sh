#! /bin/bash

function help(){
	echo "vip_download.bat port_number prog_file search_dir"
	echo "i.e."
	echo "   vip_download.sh 8 prog_firehose_ddr.elf images/"
	echo ""
	echo "PS: search_dir must end with \"/\""
}

# check parameters
if [ "$#" != "3" ]; then
	echo "wrong parameter count"
	help
	exit 1
fi

# check port number
if ! grep '^[[:digit:]]*$' <<< "$1" > /dev/null 2>&1; then
	echo "port number must be digests"
    help
	exit 1
fi

# setup env
_script_dir=$(cd "$(dirname $0)";pwd)
_bin_sahara="$_script_dir/QSaharaServer"
_bin_fh_loader="$_script_dir/fh_loader"
_param_port="/dev/ttyUSB$1"
_param_prog="$2"
_param_search_dir="$3"

# find digests
if [ -e "$_param_search_dir/DigestsToSign.bin.mbn" ]; then
	_signeddigests=DigestsToSign.bin.mbn
elif [ -e "$_param_search_dir/DigestsSigned.bin.mbn" ]; then
	_signeddigests=DigestsSigned.bin.mbn
else
	echo "signed digests not found!"
	help
	exit 1
fi

# find chained table
if [ -e "$_param_search_dir/ChainedTableOfDigests.bin" ]; then
	_chainedtable=ChainedTableOfDigests.bin
else
	echo "chained table not found!"
	help
	exit 1
fi

# exec sahara
_cmd_sahara="$_bin_sahara -p $_param_port -s 13:$_param_prog -b $_param_search_dir"
echo "$_cmd_sahara"
eval "$_cmd_sahara"

# exec firehose
_cmd_fh_loader="$_bin_fh_loader --port=$_param_port --sendxml=rawprogram0.xml,rawprogram1.xml,rawprogram2.xml,rawprogram3.xml,rawprogram4.xml,rawprogram5.xml,patch0.xml,patch1.xml,patch2.xml,patch3.xml,patch4.xml,patch5.xml --search_path=$_param_search_dir --showpercentagecomplete --memoryname=ufs --setactivepartition=1 --zlpawarehost=0 --signeddigests=$_signeddigests --chaineddigests=$_chainedtable"
echo "$_cmd_fh_loader"
eval "$_cmd_fh_loader"
