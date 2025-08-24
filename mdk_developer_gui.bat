@echo off
echo "MDK | ========================================"
echo "MDK | Launch Python"
echo "MDK | ========================================"

call mdk_developer_settings.bat

echo "MDK | MDK_PATH = %MDK_PATH%"

python %MDK_PATH%\src\mdk_developer_gui.py

pause