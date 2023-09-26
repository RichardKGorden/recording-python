import pyautogui
import cv2
import numpy as np

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

html_file_path = "E:\\recording_initial\\recording\\hello.html"

chrome_driver_path = "D:\chrome-win64\chrome.exe"

driver = webdriver.Chrome()
driver.get("file://" + html_file_path)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "html")))


# Specify resolution
resolution = (1920, 1080)
 
# Specify video codec
codec = cv2.VideoWriter_fourcc(*"XVID")
 
# Specify name of Output file
filename = "Recording.avi"
 
# Specify frames rate. We can choose any
# value and experiment with it
fps = 60.0
 
 
# Creating a VideoWriter object
out = cv2.VideoWriter(filename, codec, fps, resolution)
 
# Create an Empty window
cv2.namedWindow("Live", cv2.WINDOW_NORMAL)
 
# Resize this window
cv2.resizeWindow("Live", 480, 270)
 
while True:
    try:
        # Take screenshot using PyAutoGUI
        img = pyautogui.screenshot()
    
        # Convert the screenshot to a numpy array
        frame = np.array(img)
    
        # Convert it from BGR(Blue, Green, Red) to
        # RGB(Red, Green, Blue)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
        # Write it to the output file
        out.write(frame)
        
        web_content = driver.find_element(By.TAG_NAME, "html").screenshot_as_png
        web_frame = np.array(bytearray(web_content), dtype=np.uint8)
        web_frame = cv2.imdecode(web_frame, -1)
        web_frame = cv2.resize(web_frame, resolution)
                
        # Optional: Display the recording screen
        cv2.imshow('Live', frame)
        
        # Stop recording when we press 'q'
        if cv2.waitKey(1) == ord('q'):
            break
    except WebDriverException as e:
        print("WebDriverException:", e)
        break
 
# Release the Video writer
out.release()

driver.quit()
 
# Destroy all windows
cv2.destroyAllWindows()