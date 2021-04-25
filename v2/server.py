import base64
import cv2
import zmq
from control import ControlState

context = zmq.Context()
footage_socket = context.socket(zmq.PAIR)
footage_socket.bind('tcp://*:5555')

camera = cv2.VideoCapture(0)  # init the camera

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
            if c.a.value:
                print("A pressed")
            if c.b.value:
                print("B pressed")
            if c.select.value:
                print("Select pressed")
            print("Vertical:", c.vertical.value)
            print("Horizontal:", c.horizontal.value)

    except KeyboardInterrupt:
        break


footage_socket.close()
camera.release()