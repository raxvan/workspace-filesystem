
if "%~1"=="" (
    echo Error: No argument supplied for WORKSPACE.
    exit /b 1
)

set REPODIR=%~dp0../
set TEST_ENV_NAME=wfs-tests

docker build -t %TEST_ENV_NAME% -f %~dp0test-env.dockerfile %~dp0../
 
@set "WORKSPACE=%1"

docker run ^
	-it ^
	--rm ^
	-v %REPODIR%:/repo ^
	-v %WORKSPACE%:/wfs ^
	-e "TERM=xterm-256color" ^
	%TEST_ENV_NAME% ^
	/bin/bash
