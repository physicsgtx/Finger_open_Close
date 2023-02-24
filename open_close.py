import mediapipe as mp
import cv2
import math
import serial
import time
global ser

portNo ="COM4"
def sendData(string):

    try:
       ser.write(string.encode())
       print(string)
    except:
        pass

def connectToRobot(portNo):
    global ser
    try:
        ser = serial.Serial(portNo, 9600)
        print("Robot Connected ")
    except:
        print("Not Connected To Robot ")
        pass


connectToRobot(portNo)
def get_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
def get_angle(x1, y1, x2, y2, x3, y3):
    radians = math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2)
    angle = math.fabs(math.degrees(radians))
    if angle > 180:
        angle = 360 - angle
    return angle

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


# Initialize video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 30)  # Set FPS to 30


# Initialize MediaPipe Hands.
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7)


while cap.isOpened():
    # Read frame from camera.
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue

    # Flip the image horizontally for a later selfie-view display, and convert
    # the BGR image to RGB.
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        # Loop through hands.
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # Define landmarks.
            landmark_list = []
            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, c = image.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmark_list.append([id, cx, cy])
            # Calculate the hand width in pixels
            landmarks_array = mp_hands.HandLandmark
            x_min = min([hand_landmarks.landmark[i].x for i in range(len(landmarks_array))])
            x_max = max([hand_landmarks.landmark[i].x for i in range(len(landmarks_array))])
            hand_width_px = (x_max - x_min) * image.shape[1]
            thumb_tip = hand_landmarks.landmark[4].x * hand_width_px
            thumb_base = hand_landmarks.landmark[3].x * hand_width_px

            thumb_open = thumb_tip < thumb_base
            # Define fingers.
            thumb = landmark_list[1:5]
            index = landmark_list[5:9]
            middle = landmark_list[9:13]
            ring = landmark_list[13:17]
            pinky = landmark_list[17:21]

            # Define angles.
            angles = [""] * 5

            # Thumb
            hand_landmarks = results.multi_hand_landmarks[0]

            # Get the coordinates of the wrist, base of the thumb, and tip of the thumb
            wrist = (hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x,
                     hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y)
            thumb_base = (hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_CMC].x,
                          hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_CMC].y)
            thumb_tip = (hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x,
                         hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y)

            # Calculate the angle between the three points
            angle = math.degrees(math.atan2(thumb_tip[1] - thumb_base[1], thumb_tip[0] - thumb_base[0]) -
                                 math.atan2(wrist[1] - thumb_base[1], wrist[0] - thumb_base[0]))

            # Classify the angle
            if angle < -130:
                angles[0]="0"
            # elif angle > -10:
            #     angles[0]="0"
            else:
                angles[0]="1"

            # Index
            # 0 180 90
            index_angle = get_angle(index[0][1], index[0][2], index[1][1], index[1][2], index[2][1], index[2][2])
            if index_angle < 50:
                angles[1] = "1"
            # elif index_angle > 100:
            #     angles[1] = "180"
            else:
                angles[1] = "0"

            # Middle
            middle_angle = get_angle(middle[0][1], middle[0][2], middle[1][1], middle[1][2], middle[2][1], middle[2][2])
            if middle_angle < 50:
                angles[2] = "1"
            # elif middle_angle > 100:
            #     angles[2] = "180"
            else:
                angles[2] = "0"

            # Ring
            ring_angle = get_angle(ring[0][1], ring[0][2], ring[1][1], ring[1][2], ring[2][1], ring[2][2])
            if ring_angle < 50:
                angles[3] = "1"
            # elif ring_angle >100:
            #     angles[3]="180"
            else:
                angles[3]="0"

            # Pinky
            ring_angle = get_angle(pinky[0][1], pinky[0][2], pinky[1][1], pinky[1][2], pinky[2][1], pinky[2][2])
            if ring_angle < 50:
                angles[4] = "1"
            # elif ring_angle >100:
            #     angles[4]="180"
            else:
                angles[4]="0"

            # result="$"+''.join(str(int(i)) for i in angles)
            # time.sleep(.2)
            print("$"+''.join(str(int(i)) for i in angles))
            sendData("$"+''.join(str(int(i)) for i in angles))


            cv2.imshow('Hand Tracking', image)
    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# Release the VideoCapture object and close the window
cap.release()
cv2.destroyAllWindows()
