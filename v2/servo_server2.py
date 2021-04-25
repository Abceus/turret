import base64
import cv2
import zmq
from control import ControlState
from servo_control import ServoControll
import RPi.GPIO as GPIO

context = zmq.Context()
footage_socket = context.socket(zmq.PAIR)
footage_socket.bind('tcp://*:5555')

camera = cv2.VideoCapture(0)  # init the camera

GPIO.setmode(GPIO.BCM)
horizontal_servo = ServoControll(3.0, 11.7, 1, 27)
vertical_servo = ServoControll(3.0, 11.7, 1, 17)

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
            while True:
                msg = footage_socket.recv(flags=zmq.NOBLOCK)
        except zmq.ZMQError:
            pass
        if msg is not None:
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

            if c.horizontal.value != 0.0:
                horizontal_servo.rotate(c.horizontal.value)

            if c.vertical.value != 0.0:
                vertical_servo.rotate(c.vertical.value)

    except KeyboardInterrupt:
        break


footage_socket.close()
camera.release()