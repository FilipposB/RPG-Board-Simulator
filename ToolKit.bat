@echo off
::if %1 is 0 its the move and rename function
::it expects %2 to be targer %3 to be destination %4 to be the new file name
::

:main
if %1==0 goto move_and_rename
if %1==1 goto rename
if %1==2 goto remove
exit /B 1

:move_and_rename
copy "%2" "%3\%4%~x2">nul
exit /B 0

:rename
ren %3\%2 %~n4%~x2>nul
exit /B 0

:remove
del %3\%2>nul
exit /B 0