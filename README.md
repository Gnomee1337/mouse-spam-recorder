# Spam Mouse Bot

Program for recording mouse movements + clicks and their automatic playback

<img src="https://i.imgur.com/7e5DCqF.jpeg" width="700" height="300"/>

# How to use:
1. After starting the program use the button “Record Movements” which will open the utility “MouseInfo”.

The “MouseInfo” utility is designed to record the coordinates of the mouse cursor location in Windows.

In the “MouseInfo” utility uncheck the “3 Sec.Button Delay” checkbox and set the mouse cursor to the desired location by pressing the “Log XY (F6)” button.

After that the XY coordinates of the last cursor position will appear in the “MouseInfo” utility. 

Record the cursor coordinates the required number of times. 

2. When you are ready in the “MouseInfo” utility, click the “Save Log” button to export the recorded mouse coordinates. 

You can close the “MouseInfo” utility. 

3. Now click “Load Coordinates” button in the program to import the recorded coordinates. 

After importing the coordinates, a window will appear where you can automate mouse clicks (Right click on the desired coordinates) or change them. 

4. After that click the “Save and Close” button. 

5. Now in the main window specify the “Delay” before each mouse click in seconds, as well as the number of repetitions of the recorded algorithm.

6. When you are ready, click “Start Replay” button to start the automation.

To cancel, you can click the “Cancel Replay” button or use the “ESC” hotkey on the keyboard.


# Setup:
```
$ pip install -r requirements.txt
```

# Build executable:
```
$ pyinstaller --onefile --windowed --hidden-import=mouseinfo --icon=icon.ico .\spam_v2.py
```

# Usage:
```
$ python spam_v2.py
