import cv2
import numpy as np
import mediapipe as mp


mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

vid_cap = cv2.VideoCapture(1) # fish eye cam

prev1_x5, prev1_y5 = 0, 0
prev2_x5, prev2_y5 = 0, 0


cameraMatrix = np.array([
    [447.67232197,   0.0,         334.65676781],
    [  0.0,         445.88002279, 232.82394761],
    [  0.0,           0.0,           1.0      ]
])

cameraMatrix = cameraMatrix.reshape(3,3)

dist = np.array([
    [[-0.32543405,  0.01195246, -0.00114533,  0.00129891,  0.0374563  ]]
])

dist = dist.reshape(1,5)

while(True):

    success, frame = vid_cap.read()

    frame = cv2.flip(frame, 1)

    h, w = frame.shape[:2]
    newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix, dist, (w,h), 1, (w,h))

    dst = cv2.undistort(frame, cameraMatrix, dist, None, newCameraMatrix)

    # cropping image based on roi matrix
    x,y,w,h = roi
    dst = dst[y:y+h, x:x+w] # cropped image(undistorted)

    if not success:
        print("Issues in opening cam")
        break
    
    result = hands.process(cv2.cvtColor(dst, cv2.COLOR_BGR2RGB))

    if result.multi_hand_landmarks:
        first_hand_landmark = result.multi_hand_landmarks[0].landmark
        if first_hand_landmark:
            # for landmark in first_hand_landmark:
                # x = int(landmark.x*frame.shape[1])
                # y = int(landmark.y*frame.shape[0])
                # dst = cv2.circle(dst, (x, y), 5, (255, 255, 0), -1)




            x5 = int(first_hand_landmark[8].x*dst.shape[1])
            y5 = int(first_hand_landmark[8].y*dst.shape[0])
             
            dst = cv2.circle(dst, (x5, y5), 5, (255, 255, 0), -1)

    


    cv2.imshow("cam_frame", dst)
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break 


vid_cap.release()
cv2.destroyAllWindows()

