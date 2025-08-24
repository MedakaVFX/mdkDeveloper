echo "MDK | load > mdk_developer_settings..."

:: common settings
SET MDK_VERSION_EXIFTOOL=13.34
SET MDK_VERSION_LIBRAW=0.21.4
SET MDK_VERSION_PYTHON=3.11.9



:: Path
SET MDK_PATH=%~dp0

SET MDK_LIBRAW_PATH=%MDK_PATH%tools\libraw\libraw-%MDK_VERSION_LIBRAW%-win\bin
SET MDK_EXIFTOOL=%MDK_PATH%tools\exiftool\exiftool-%MDK_VERSION_EXIFTOOL%-win
SET PATH=%MDK_PATH%python\python-%MDK_VERSION_PYTHON%-embed-amd64;%MDK_LIBRAW_PATH%;%MDK_EXIFTOOL%


EXIT /b