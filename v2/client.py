import pygame
import pygame_gui
import cv2
import numpy as np
import zmq
import base64
from control import ControlState

JOYSTICK_SELECT_BUTTON = 8
JOYSTICK_A_BUTTON = 1
JOYSTICK_B_BUTTON = 2

SCREEN_SIZE = [640, 530]

pygame.init()
pygame.display.set_caption("Turrel controller")
screen = pygame.display.set_mode(SCREEN_SIZE)
screen.fill([255, 255, 255])

manager = pygame_gui.UIManager(SCREEN_SIZE)

connect_text_line = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((0, 0), (640, 50)),
                                             manager=manager)

connect_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 25), (640, 25)),
                                             text='Connect',
                                             manager=manager)

pygame.joystick.init()

context = zmq.Context()
footage_socket = context.socket(zmq.PAIR)

clock = pygame.time.Clock()
run = True

control_send_timeout = 0.0

while run:
    frame = None
    try:
        while True:
            frame = footage_socket.recv_string(flags=zmq.NOBLOCK)
    except zmq.ZMQError:
        pass
    if frame is not None:
        img = base64.b64decode(frame)
        npimg = np.frombuffer(img, dtype=np.uint8)
        image = cv2.imdecode(npimg, 1)
        screen.fill([0, 0, 0])
        frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = pygame.surfarray.make_surface(frame)
        screen.blit(frame, (0, 50))
    time_delta = clock.tick(60) / 1000.0
    control_send_timeout = control_send_timeout + time_delta
    c = ControlState()
    state_changed = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == JOYSTICK_SELECT_BUTTON:
                c.select.value = True
                state_changed = True
            elif event.button == JOYSTICK_A_BUTTON:
                c.a.value = True
                state_changed = True
            elif event.button == JOYSTICK_B_BUTTON:
                c.b.value = True
                state_changed = True

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == connect_button:
                    try:
                        footage_socket.close()
                        footage_socket = context.socket(zmq.PAIR)
                        footage_socket.connect('tcp://' + connect_text_line.get_text() + ':5555')
                    except zmq.ZMQError:
                        pass

        manager.process_events(event)

    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.update()

    joystick_count = pygame.joystick.get_count()

    if joystick_count > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

        if joystick.get_numaxes() >= 2:
            axis0 = joystick.get_axis(0)
            if axis0 > 0.05 or axis0 < -0.05:
                c.horizontal.value = axis0
                state_changed = True

            axis1 = joystick.get_axis(1)
            if axis1 > 0.05 or axis1 < -0.05:
                c.vertical.value = axis1
                state_changed = True

    if state_changed:
        try:
            footage_socket.send(c.to_bytes(), flags=zmq.NOBLOCK)
            control_send_timeout = 0.0
        except zmq.ZMQError:
            pass

footage_socket.close()
pygame.quit()
cv2.destroyAllWindows()
