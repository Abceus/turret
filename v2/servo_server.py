import base64
import cv2
import zmq
from control import ControlState
# import RPi.GPIO as GPIO

context = zmq.Context()
footage_socket = context.socket(zmq.PAIR)
footage_socket.bind('tcp://*:5555')

camera = cv2.VideoCapture(0)  # init the camera

boards = (3.0, 11.7)
servoPIN = 17
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(servoPIN, GPIO.OUT)
#
# p = GPIO.PWM(servoPIN, 50)
# p.start(0.0)
current_vertical = 0.0
# p.ChangeDutyCycle(boards[0])

while True:
    try:
        grabbed, frame = camera.read()  # grab the current frame
        if frame is not None:
            frame = cv2.resize(frame, (640, 480))  # resize the frame
            encoded, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer)
            try:
                footage_socket.send(jpg_as_text, flags=zmq.NOBLOCK)
            except zmq.ZMQError:
                pass
        msg = None
        try:
            msg = footage_socket.recv(flags=zmq.NOBLOCK)
        except zmq.ZMQError:
            pass
        if msg:
            c = ControlState()
            c.from_bytes(msg)
            # if c.a.value:
            #     print("A pressed")
            # if c.b.value:
            #     print("B pressed")
            # if c.select.value:
            #     print("Select pressed")
            # print("Vertical:", c.vertical.value)
            # print("Horizontal:", c.horizontal.value)

            if c.vertical.value != 0.0:
                current_vertical = c.vertical.value + 1.0
                percent = current_vertical / 2.0
                pos = min(boards[0] + (boards[1] - boards[0]) * percent, boards[1])
                print(pos)
                # p.ChangeDutyCycle(pos)

    except KeyboardInterrupt:
        break


footage_socket.close()
camera.release()