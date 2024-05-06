import cv2
import numpy as np
import glob
import yaml

checkered_board_size = (8,6) 
frame_size = (640,480)

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((checkered_board_size[0]*checkered_board_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:checkered_board_size[0], 0:checkered_board_size[1]].T.reshape(-1,2)


objpoints = []
imgpoints = []

images = glob.glob('*.jpg')
# images = glob.glob("checkered_board.jpg")

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, corners = cv2.findChessboardCorners(gray, checkered_board_size, None)

    if ret == True:
        objpoints.append(objp)
    
        corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)

        cv2.drawChessboardCorners(img, checkered_board_size, corners2, ret)
        cv2.imshow('img', img)
        key = cv2.waitKey(500)

cv2.destroyAllWindows()

# ############################################## CALIBRATION #######################################################

ret, cameraMatrix, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, frame_size, None, None)

print(f"ret: {ret}")
print(f"\ncam_mat: {cameraMatrix}")
print(f"\ndist_mat: {dist}")
print(f"\nrvecs: {rvecs}")
print(f"\ntvecs: {tvecs}")


############## UNDISTORTION #####################################################

img = cv2.imread('checkered_board1.jpg')
h,  w = img.shape[:2]
newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix, dist, (w,h), 1, (w,h))


# fixing distoring of camera images
dst = cv2.undistort(img, cameraMatrix, dist, None, newCameraMatrix)

# # cropping image based on roi matrix
x,y,w,h = roi
dst = dst[y:y+h, x:x+w] # cropped image(undistorted)
cv2.imwrite("result.jpg", dst)

# Reprojection Error
mean_error = 0

for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], cameraMatrix, dist)
    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
    mean_error += error

print( "total error: {}".format(mean_error/len(objpoints)) )

data = {
    'ret': str(ret),
    'cam_matrix': str(cameraMatrix),
    'distortion_coeffcient': str(dist),
    'rotation_vectors': str(rvecs),
    'translation_vectors': str(tvecs)
}

file_path = 'fisheye_cam_data.yaml'


with open(file_path, 'w') as file:
    yaml.dump(data, file, default_flow_style=False)

print("yaml file data has been written")


# vid_cap = cv2.VideoCapture(0)
vid_2 = cv2.VideoCapture(1)

while(True):

    # ret_val, image = vid_cap.read()
    ret_val2, image2 = vid_2.read()
    # image = cv2.flip(image, 1)
    image2 = cv2.flip(image2, 1)

    h, w = image2.shape[:2]
    newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix, dist, (w,h), 1, (w,h))

    dst = cv2.undistort(image2, cameraMatrix, dist, None, newCameraMatrix)

    # cropping image based on roi matrix
    x,y,w,h = roi
    dst = dst[y:y+h, x:x+w] # cropped image(undistorted)

    if ret_val2 != True:
        break
    
    # cv2.imshow('frame', image)
    cv2.imshow('frame2', dst)
    # print(f"y_pix: {image.shape[1]}, x_pix: {image.shape[0]}")
    
    
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        # cv2.imwrite("checkered_board22.jpg", dst)
        break

# vid_cap.release()
vid_2.release()
cv2.destroyAllWindows()