@for /F %%i in ('..\..\pespy.py -V') do set VERSION=%%i
@..\..\py2cc.py --all -S -oPeSPY.exe PeSPY_EXE.py
@upx PeSPY.exe
@zip -0 PeSPY-%VERSION%.zip PeSPY.exe LICENSE.txt PeSPY.txt
