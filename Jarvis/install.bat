@echo off
echo Installing Jarvis dependencies...

REM Core packages (pre-built wheels)
pip install --only-binary :all: numpy
pip install openai>=1.3.0
pip install requests>=2.31.0

REM Optional packages
pip install python-dotenv
pip install pytest
pip install speechrecognition pyttsx3

echo Installation complete!
