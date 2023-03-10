# import the necessary packages
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from imutils.video import VideoStream
import numpy as np
import imutils
import time
import cv2
import os
import serial
import threading
s = serial.Serial("/dev/tty.HC-05-SerialPort",9600,timeout=4)

#import ConnectServoMotor


def detect_and_predict_mask(frame, faceNet, maskNet):
	# grab the dimensions of the frame and then construct a blob
	# from it
	(h, w) = frame.shape[:2]
	blob = cv2.dnn.blobFromImage(frame, 1.0, (244, 244),
		(104.0, 177.0, 123.0))

	# pass the blob through the network and obtain the face detections
	faceNet.setInput(blob)
	detections = faceNet.forward()
	print(detections.shape)

	# initialize our list of faces, their corresponding locations,
	# and the list of predictions from our face mask network
	faces = []
	locs = []
	preds = []

	# loop over the detections
	for i in range(0, detections.shape[2]):
		# extract the confidence (i.e., probability) associated with
		# the detection
		confidence = detections[0, 0, i, 2]

		# filter out weak detections by ensuring the confidence is
		# greater than the minimum confidence
		if confidence > 0.5:
			# compute the (x, y)-coordinates of the bounding box for
			# the object
			try:
				box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
				(startX, startY, endX, endY) = box.astype("int")

				# ensure the bounding boxes fall within the dimensions of
				# the frame
				(startX, startY) = (max(0, startX), max(0, startY))
				(endX, endY) = (min(w - 1, endX), min(h - 1, endY))

				# extract the face ROI, convert it from BGR to RGB channel
				# ordering, resize it to 224x224, and preprocess it
				face = frame[startY:endY, startX:endX]


				face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
				face = cv2.resize(face, (224, 224))
				face = img_to_array(face)
				face = preprocess_input(face)

				# add the face and bounding boxes to their respective
				# lists
				faces.append(face)
				locs.append((startX, startY, endX, endY))
			except Exception as e:
				print(f'Exception {str(e)}')


	# only make a predictions if at least one face was detected
	if len(faces) > 0:
		# for faster inference we'll make batch predictions on *all*
		# faces at the same time rather than one-by-one predictions
		# in the above `for` loop
		faces = np.array(faces, dtype="float32")
		#cv2.imshow('Example - Show image in window', faces[0])
		preds = maskNet.predict(faces, batch_size=32)


	# return a 2-tuple of the face locations and their corresponding
	# locations
	return (locs, preds)

# load our serialized face detector model from disk
prototxtPath = r"/Users/Apple/DeepLearning/FMDetection/Face-Mask-Detection-master/face_detector/deploy.prototxt"
weightsPath = r"/Users/Apple/DeepLearning/FMDetection/Face-Mask-Detection-master/face_detector/res10_300x300_ssd_iter_140000.caffemodel"
faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)

# load the face mask detector model from disk
maskNet = load_model("mask_detector2.model")

# initialize the video stream
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
#vs=cv2.VideoCapture(0)
countOpen = 0
countClose = 0
flagCounter = 0


def warnafter(timeout):
	time.sleep(timeout)

	s.write(bytes("C", 'utf-8'))  # 67
	countClose = 0
	countOpen = 0
	flagCounter = 0
def countdown(time_sec):
	while time_sec:
		time.sleep(1)
		time_sec -= 1
		if time_sec <= 0:
			s.write(bytes("C", 'utf-8'))  # 67
			countClose = 0
			countOpen = 0
			flagCounter = 0

# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	frame = vs.read()
	frame = imutils.resize(frame, width=640)

	# detect faces in the frame and determine if they are wearing a
	# face mask or not
	(locs, preds) = detect_and_predict_mask(frame, faceNet, maskNet)
	print(preds)

	# loop over the detected face locations and their corresponding
	# locations
	try :
		for (box, pred) in zip(locs, preds):
			# unpack the bounding box and predictions
			(startX, startY, endX, endY) = box
			(mask, withoutMask) = pred
			showText = False
			if(mask > 0.8 ):
				showText = True
				if countOpen == 10 and flagCounter ==0:
					countOpen=0
					s.write(bytes("O", 'utf-8'))  # 79
					countClose=0
					flagCounter =1
					t = threading.Thread(target=warnafter, args=(12,))
					t.start()

				else :
					countOpen +=1

			#	ConnectServoMotor.open_gate(1)
			elif withoutMask > 0.8:
				showText = True
				if countClose==10 and flagCounter == 1:
					s.write(bytes("C", 'utf-8'))  # 67
					countClose=0
					countOpen=0
					flagCounter = 0
				else :
					countClose+=1

			else :
				showText = False

			#	ConnectServoMotor.open_gate(0)
			#else:
			#	ConnectServoMotor.open_gate(0)

			# determine the class label and color we'll use to draw
			# the bounding box and text
			label = "Mask" if mask > withoutMask else "No Mask"
			l =label
			color = (0, 255, 0) if label == "Mask" else (0, 0, 255)


			# include the probability in the label
			label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

			# display the label and bounding box rectangle on the output
			# frame
			if showText:
				cv2.putText(frame, label, (startX, startY - 10),
					cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
				cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)

			break
		# if l == 'Mask':
		# 	cv2.imwrite('Mask' + '.jpg', frame)
		# elif l == "No Mask":
		# 	cv2.imwrite('NoMask' + '.jpg', frame)
	except:
		pass
	# show the output frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

# do a bit of cleanup
#cv2.destroyAllWindows()
#vs.stop()



