@echo off
if exist "D:\msys64\ucrt64\bin\python.exe" (
    "D:\msys64\ucrt64\bin\python.exe" "%~dp0kiemtra.py" %*
) else (
    python "%~dp0kiemtra.py" %*
)
