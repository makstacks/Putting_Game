# Putting_Game
This game is still under development, with features needing to be added/refined.
Object tracking and object detection is applied to track golf puts in real time and display stats/games. Works best with the Perfect Practice putting mat
but settings can be adjusted to suit any mat.  

The game is started by running main.py. This calls mat_detect to identify general shape of the mat and 2 holes. Once these are defined we start tracking 
moving objects, the desired size/area of detected objects can be adjusted within the code. The tracker method takes the detected objects and as the name
suggests applies object tracking, allowing us to store out the path of an object.
If the object is moving towards the hole along the mat we register this object as a shot. If this shot enters either of the holes we record the shot as
a big hole or small hole, if neither of these are true we register it as a miss.

The basic code and method was identified thanks to Pysource: https://www.youtube.com/watch?v=O3b8lVF93jU&ab_channel=Pysource

Note: Sound files have not been added into this repository so references to sounds/music within code will need to be commented out.
