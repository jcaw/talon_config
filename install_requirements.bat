rem Kill Talon if running. Need to restart to load the new pip env anyway.
wmic process where name='talon.exe' delete
rem Install all requirements - useful in Talon beta
%~dp0/../.venv/Scripts/pip install -r %~dp0/requirements.txt --no-warn-script-location
