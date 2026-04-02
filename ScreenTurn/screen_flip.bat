@echo off
echo ===== DEBUG BATCH STARTED ===== > debug_output.txt
echo Current directory: %cd% >> debug_output.txt
echo User argument: %1 >> debug_output.txt
echo. >> debug_output.txt

echo Testing Python path: >> debug_output.txt
dir D:\TWITCH\Redeems\.venv\Scripts\python.exe >> debug_output.txt 2>&1

echo. >> debug_output.txt
echo Testing script file: >> debug_output.txt
dir D:\TWITCH\Redeems\ScreenTurn\screen_flip.py >> debug_output.txt 2>&1

echo. >> debug_output.txt
echo Attempting to run Python: >> debug_output.txt
D:\TWITCH\Redeems\.venv\Scripts\python.exe D:\TWITCH\Redeems\.py %1 >> debug_output.txt 2>&1

echo ===== DEBUG BATCH ENDED ===== >> debug_output.txt