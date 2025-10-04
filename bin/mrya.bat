@echo off
setlocal

rem Get the root project folder (one level up from /bin)
for %%I in ("%~dp0..") do set "BASEDIR=%%~fI"

set "PYTHON=%BASEDIR%\python\python.exe"
set "PYTHONPATH=%BASEDIR%\src;%PYTHONPATH%"

call "%PYTHON%" "%BASEDIR%\src\mrya_main.py" %*

endlocal
