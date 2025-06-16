@echo off

:: get parameter count
set argc=0
for %%x in (%*) do Set /A argc+=1

:: check parameters
if "%argc%"=="3" (
    goto check2
) else (
    echo wrong parameter count
    goto error
)

:check2
echo %1|findstr /v "[^0-9]" && (
    goto env
) || (
    echo port number must be digests
    goto error
)

:env
:: setup env
set _script_dir=%~d0%~p0
set _bin_sahara=%_script_dir%QSaharaServer.exe
set _bin_fh_loader=%_script_dir%fh_loader.exe
set _param_port=\\.\COM%1
set _param_prog=%2
set _param_search_dir=%3

:: find digests
if exist %_param_search_dir%\DigestsSignedZlpAwareHost.bin.mbn (
	set _signeddigests=DigestsSignedZlpAwareHost.bin.mbn
) else if exist %_param_search_dir%\DigestsSigned.bin.mbn (
	set _signeddigests=DigestsSigned.bin.mbn
) else if exist %_param_search_dir%\DigestsToSign.bin.mbn (
	set _signeddigests=DigestsToSign.bin.mbn
) else (
	echo signed digests not found!
	goto error
)

:: find chained table
if exist %_param_search_dir%\ChainedTableOfDigestsZlpAwareHost.bin (
	set _chainedtable=ChainedTableOfDigestsZlpAwareHost.bin
) else if exist %_param_search_dir%\ChainedTableOfDigests.bin (
	set _chainedtable=ChainedTableOfDigests.bin
) else (
	echo chained table not found!
	goto error
)

:: exec sahara
::bin\QSaharaServer.exe -p \\.\COM2 -s 13:prog_firehose_ddr.elf -b .\
set _cmd_sahara=%_bin_sahara% -p %_param_port% -s 13:%_param_prog% -b %_param_search_dir%
echo %_cmd_sahara%
%_cmd_sahara%

:: exec firehose
::bin\fh_loader.exe --port=\\.\COM2 --sendxml=rawprogram0.xml,rawprogram1.xml,rawprogram2.xml,rawprogram3.xml,rawprogram4.xml,rawprogram5.xml,patch0.xml,patch1.xml,patch2.xml,patch3.xml,patch4.xml,patch5.xml --search_path=.\ --showpercentagecomplete --memoryname=ufs --setactivepartition=1 --signeddigests=DigestsToSign.bin.mbn --chaineddigests=ChainedTableOfDigests.bin
set _cmd_fh_loader=%_bin_fh_loader% --port=%_param_port% --sendxml=rawprogram0.xml,rawprogram1.xml,rawprogram2.xml,rawprogram3.xml,rawprogram4.xml,rawprogram5.xml,patch0.xml,patch1.xml,patch2.xml,patch3.xml,patch4.xml,patch5.xml --search_path=%_param_search_dir% --showpercentagecomplete --memoryname=ufs --setactivepartition=1 --zlpawarehost=1 --signeddigests=%_signeddigests% --chaineddigests=%_chainedtable%
echo %_cmd_fh_loader%
%_cmd_fh_loader%
::exit

:error
echo vip_download.bat port_number prog_file search_dir
echo i.e.
echo    vip_download.bat 8 prog_firehose_ddr.elf images\
echo=
echo PS: search_dir must end with "\"
::exit