@echo off
title DnD Board Simulator V0.1
color 0F

:: Final variables
set PYTHON_FILE=Battle.py
set CAMPAIGNS_FOLDER=Campaigns
set MONSTERS_FOLDER=Monster_Database
set OPTIONS_FILE=Options.txt

:init
if not exist %PYTHON_FILE% goto missing_file
if not exist %CAMPAIGNS_FOLDER% md %CAMPAIGNS_FOLDER%
if not exist %MONSTERS_FOLDER% md %MONSTERS_FOLDER%
:: Checks to see if there are options
if not exist %OPTIONS_FILE% goto new_options
call :load_options
goto main

:default_options
set letter_color=0
set background_color=F
set auto_open_site=true
goto :eof

:new_options
call :default_options
(
  echo %letter_color%
  echo %background_color%
  echo %auto_open_site%
) > %OPTIONS_FILE%
goto main

:load_options
< %OPTIONS_FILE% (
  set /p letter_color=
  set /p background_color=
  set /p auto_open_site=
)
goto :eof

:missing_file
echo %PYTHON_FILE% Seems to be missing
pause
exit

:main
color %letter_color%%background_color%
cls
echo Choose an option
echo -------------------------
echo 1) Run DnD Board Simulator
echo 2) Update Monster Database
echo 3) Manage Campaigns
echo 4) Options

set/p "option=>"

if %option% == 1 goto launch
if %option% == 2 goto update_monster_data
if %option% == 3 goto manage_campaigns
if %option% == 4 goto options
goto main

:options
call :load_options
goto main

:launch
set Test=
for /f "delims=" %%a in ('dir /b %CAMPAIGNS_FOLDER%') do set Test=%%a
if {%Test%} == {} goto no_campaigns
cls
echo Choose a campaign
echo ----------------
dir /a/o/b %CAMPAIGNS_FOLDER%
echo ----------------
set/p "campaign=>"
if not exist %CAMPAIGNS_FOLDER%/%campaign% goto campaign_missing
if exist %CAMPAIGNS_FOLDER%/%campaign%/Site.bat if %auto_open_site% == true call %CAMPAIGNS_FOLDER%/%campaign%/Site.bat else echo No Site Link was available
dir /a/o/b "%CAMPAIGNS_FOLDER%/%campaign%/Player_Icons"  > "%CAMPAIGNS_FOLDER%/%campaign%/Player_Names"
set monsters_found=0
for %%A in (%MONSTERS_FOLDER%/*) do set /a monsters_found+=1
set /p "grid_size=Grind Size>"
C:\Users\pogan\AppData\Local\Programs\Python\Python39\python.exe %PYTHON_FILE% %campaign% %monsters_found% %grid_size%
echo Campaign : %campaign% was closed.
pause
goto main

:no_campaigns
cls
echo There are no available Campaigns
echo Would you like to create one ? (y/n)
set/p "opt=>"
if /I %opt%==y goto new_campaign
goto main

:campaign_missing
cls
echo There is no campaign with the name "%campaign%"
echo -----------------------------------------------
echo Would you like to create %campaign% ? (y/n)
set/p "opt=>"
if /I %opt%==y goto new_campaign
goto main

:update_monster_data
dir /a/o/b %MONSTERS_FOLDER% > Monster_Info
echo Monster Database was updated !
echo Amount of Monsters found :
dir /a:-d /s /b %MONSTERS_FOLDER% | find /c ":\"
pause
goto main

:manage_campaigns
set Test=
for /f "delims=" %%a in ('dir /b %CAMPAIGNS_FOLDER%') do set Test=%%a
cls
echo Existing Campaigns
echo ------------------
if {%Test%}=={} (echo No existing campaigns) else dir /a/o/b %CAMPAIGNS_FOLDER%
echo ------------------
echo Options:
echo 1) Add a new Campaign
if not {%Test%}=={} echo 2) Edit a Campaign
echo 0) Back to Main Menu
set/p "cmp_opt=>"
if %cmp_opt% == 0 goto main
if %cmp_opt% == 1 goto new_campaign
if not {%Test%}=={} if %cmp_opt% == 2 goto choose_edit_campaign
goto manage_campaigns

:new_campaign
cls
set/p "campaign=Choose a campaign name : "
if exist %CAMPAIGNS_FOLDER%/%campaign% (
	echo This name already exists ! 
	pause
	goto new_campaign
)
md %CAMPAIGNS_FOLDER%/%campaign%
md %CAMPAIGNS_FOLDER%/%campaign%/Player_Icons
echo. 2>%CAMPAIGNS_FOLDER%/%campaign%/Player_Names
set back_address=next_step
:add_characters
echo Write a Character Name (if its "done" the process will stop)
set/p "ch_name=Name: "
if /I %ch_name%==done goto %back_address%
set/p "icon=Drag and drop character icon: "
call Toolkit.bat 0 %icon% %CAMPAIGNS_FOLDER%/%campaign%/Player_Icons %ch_name%
goto add_characters

:next_step
echo You can include a link to be opened when the campaign starts (if you don't wish to do that enter no)
set/p "link=Link: "
dir /a/o/b "%CAMPAIGNS_FOLDER%/%campaign%/Player_Icons" > "%CAMPAIGNS_FOLDER%/%campaign%/Player_Names"
if /I %link%==no goto main
echo.@echo off>%CAMPAIGNS_FOLDER%/%campaign%/Site.bat
echo.start %link%>>%CAMPAIGNS_FOLDER%/%campaign%/Site.bat
goto main

:choose_edit_campaign
cls
echo Choose a Campaign to edit
echo -------------------------
dir /a/o/b %CAMPAIGNS_FOLDER%
echo -------------------------
set/p "campaign=>"
goto edit_campaign

:edit_campaign
set edit_opt=9
if not exist %CAMPAIGNS_FOLDER%/%campaign% goto campaign_missing
dir /a/o/b "%CAMPAIGNS_FOLDER%/%campaign%/Player_Icons"  > "%CAMPAIGNS_FOLDER%/%campaign%/Player_Names"
::cls
echo --------------------------
echo Campaign : %campaign%
echo --------------------------
echo Player Characters:
dir	/a/o/b "%CAMPAIGNS_FOLDER%/%campaign%/Player_Icons"
echo --------------------------
echo Options:
echo 1) Add a new Player Character
echo 2) Rename Player Character
echo 3) Delete Player Character
echo 4) Rename Campaign
echo 5) Delete Campaign
echo 0) Back to Main Menu
set/p "edit_opt=>"
if %edit_opt% == 0 goto main
if %edit_opt% == 1 (
	set back_address=edit_campaign
	goto add_characters
)
if %edit_opt% == 2 goto rename_character
if %edit_opt%==3 (
	set/p "del_name= Character's Name: "
	goto delete_character
)

goto edit_campaign

:rename_character
set/p "old_name=Character's Name: "
set/p "new_name=Character's new Name: "
call Toolkit.bat 1 %old_name% %CAMPAIGNS_FOLDER%\%campaign%\Player_Icons %new_name%
goto edit_campaign

:delete_character
echo Write DELETE to delete %del_name%
set/p "check=>"
if %check%==DELETE call Toolkit.bat 2 %del_name% %CAMPAIGNS_FOLDER%\%campaign%\Player_Icons
goto edit_campaign

:eof