@echo off
REM Check if the user has provided an argument
if "%1"=="" (
    echo Usage: assemble.bat output_name
    exit /b 1
)

REM Set the output name from the first argument
set OUTPUT_NAME=%1

REM Assemble and link using the specified output name
C:\masm32\bin\ml /c /Zd /coff %OUTPUT_NAME%.asm
C:\masm32\bin\Link /SUBSYSTEM:CONSOLE %OUTPUT_NAME%.obj

REM Run the executable if linking was successful
if exist %OUTPUT_NAME%.exe (
    echo Running %OUTPUT_NAME%.exe...
    %OUTPUT_NAME%.exe
) else (
    echo Failed to create %OUTPUT_NAME%.exe
)
