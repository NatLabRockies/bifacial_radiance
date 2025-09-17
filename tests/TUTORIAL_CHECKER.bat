@echo off
setlocal

REM List of Python files to run
set python_files=..\docs\tutorials\*.py

REM Output file to save stdout
set output_file=tutorial_checker_output.txt

REM Clear the output file if it exists
if exist %output_file% del %output_file%

REM Loop through each Python file and run it
for %%f in (%python_files%) do (
    echo %time% >>  %output_file%
    echo Running %%f 
    echo Running %%f >> %output_file%
    python "%%f" >> %output_file% 2>&1
    echo. >> %output_file%
)

echo Output saved to %output_file%
endlocal