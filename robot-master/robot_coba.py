# USAGE
# python real_time_object_detection.py

from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import imutils
import time
import cv2

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor", "tie", "book"]

COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe('MobileNetSSD_deploy.prototxt.txt', 'MobileNetSSD_deploy.caffemodel')

print("[INFO] starting video stream...")
vs = VideoStream(src=2).start()  # ganti ke 0 jika pakai webcam biasa
time.sleep(2.0)
fps = FPS().start()

last_command_time = 0
command_interval = 0.5

while True:
	frame = vs.read()
	frame = imutils.resize(frame, width=400)
	(h, w) = frame.shape[:2]
	frame_center = w // 2

	blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
		0.007843, (300, 300), 127.5)
	net.setInput(blob)
	detections = net.forward()

	person_detected = False
	current_time = time.time()

	for i in np.arange(0, detections.shape[2]):
		confidence = detections[0, 0, i, 2]
		if confidence > 0.2:
			idx = int(detections[0, 0, i, 1])
			label_name = CLASSES[idx]
			if label_name not in ["person", "cat"]:
				continue

			person_detected = True
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")

			center_x = (startX + endX) // 2

            # draw the prediction on the frame
			label = "{}: {:.2f}%".format(CLASSES[idx],
				confidence * 100)
			cv2.rectangle(frame, (startX, startY), (endX, endY),
				COLORS[idx], 2)
			y = startY - 15 if startY - 15 > 15 else startY + 15
			cv2.putText(frame, label, (startX, y),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

			if current_time - last_command_time >= command_interval:
				if abs(center_x - frame_center) < 40:
					print("🟢 Perintah: MAJU")
				elif center_x < frame_center:
					print("🟡 Perintah: BEL0K KIRI")
				else:
					print("🟡 Perintah: BELOK KANAN")
				last_command_time = current_time

	if not person_detected and current_time - last_command_time >= command_interval:
		print("🔴 Perintah: BERHENTI (tidak ada objek)")
		last_command_time = current_time

	# tampilkan hasil kamera tanpa delay
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break

	fps.update()

fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
cv2.destroyAllWindows()
vs.stop()
