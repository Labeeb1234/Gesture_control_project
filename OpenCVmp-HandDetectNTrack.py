import tensorflow as tf
import cv2
import mediapipe as mp
import time

# using palm detection and handlandmark CNN model for hand detection
hands = mp.solutions.hands.Hands( # type: ignore
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5   
) 

freq = 27.0 # Hz

vid_cap  = cv2.VideoCapture(0)
previous_time = time.time()

detection_centres = []
while(True):
    ret, frame = vid_cap.read()
    current_time = time.time()
    frame = cv2.flip(frame,1)

    if ret == False:
        break
    
    frame_centrex = int(frame.shape[1]/2)
    frame_centrey = int(frame.shape[0]/2)

    cv2.circle(frame, (frame_centrex, frame_centrey), 10, (255,255,255), -1)
    
    start_time = time.perf_counter()
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    end_time = time.perf_counter()

    if results.multi_hand_landmarks:
        #if(current_time-previous_time > 1/freq):
        for hand_landmarks in results.multi_hand_landmarks:
            x_min = min([lm.x for lm in hand_landmarks.landmark])
            y_min = min([lm.y for lm in hand_landmarks.landmark])
            x_max = max([lm.x for lm in hand_landmarks.landmark])
            y_max = max([lm.y for lm in hand_landmarks.landmark])

            x_min = int(x_min*frame.shape[1])
            y_min = int(y_min*frame.shape[0])
            x_max = int(x_max*frame.shape[1])
            y_max = int(y_max*frame.shape[0])
            detection_centres.append(((x_max+x_min)/2, (y_max+y_min)/2))
            for bbox_centre in detection_centres:
                print(f"{bbox_centre}")

            cv2.circle(frame, (x_min,y_min), 5, (255, 100, 200), -1)
            cv2.circle(frame, (x_max,y_max), 5, (255, 100, 200), -1)
            if detection_centres:
                cv2.circle(frame, (int(detection_centres[-1][0]), int(detection_centres[-1][1])), 5, (0, 255, 0), -1)

            # creating a bounding box
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0,255,0), 2)

        # previous_time = current_time 

        cv2.putText(frame, f"FPS: {int(1/(end_time-start_time))}", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,0,255), 1)
    cv2.imshow('frame', frame)
    
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break
   
vid_cap.release()
cv2.destroyAllWindows()
    



