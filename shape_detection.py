import cv2
import imutils
import glob


class ShapeDetector():
    def __init__(self):
        pass
    def detect(self, c):  # c is the contour given to identify (2D shape)
        shape = "unidentified"
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04*perimeter, True)

        if len(approx) == 3:
            shape = ""
        elif len(approx) == 4:
            (x, y, w, h) = cv2.boundingRect(approx) # bounding box corners of the rectangle shape
            aspect_ratio = w/float(h)

            if aspect_ratio > 0.95 and aspect_ratio < 1.05:
                shape = "square"
            else:
                shape = "rectangle"
        elif len(approx) == 5:
            shape = ""
        else:
            shape = ""

        return shape
    



vid = cv2.VideoCapture(0)  # Use the webcam (change the parameter to the video file path if you want to use a video file)

while True:
    ret, frame = vid.read()
    frame = cv2.flip(frame,1)

    if not ret:
        break

    resized = imutils.resize(frame, width=300)
    ratio = frame.shape[0] / float(resized.shape[0])

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    sd = ShapeDetector()

    for c in cnts:
        M = cv2.moments(c)
        if M["m00"] != 0:
            # centre points of the contour
            cX = int((M["m10"] / M["m00"]) * ratio)
            cY = int((M["m01"] / M["m00"]) * ratio)
            shape = sd.detect(c)

            c = c.astype('float')
            c*=ratio
            c = c.astype('int')

            cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
            cv2.putText(frame, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 2)

    cv2.imshow("Video", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

vid.release()
cv2.destroyAllWindows()