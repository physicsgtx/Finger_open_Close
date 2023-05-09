# importing pakages
from cvzone.HandTrackingModule import HandDetector
import cv2
from math import atan2, pi
import math

# change the value 0 to 1 if you want to use external camera
cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)

detector = HandDetector(detectionCon=0.5, maxHands=2)

# Function that detects the angle between three points ( between two vectors)
# angle returned is between 0 to 180.

def angle(A, B, C):
    Ax, Ay = A[0]-B[0], A[1]-B[1]
    Cx, Cy = C[0]-B[0], C[1]-B[1]
    a = atan2(Ay, Ax)
    c = atan2(Cy, Cx)
    if a < 0: a += pi*2
    if c < 0: c += pi*2
    result = (pi*2 + c - a) if a > c else (c - a)
    result *= (180/math.pi)
    if result > 180:
        result = 360 - result
    return result


while True:
    # Get image frame
    success, img = cap.read()
    # Find the hand and its landmarks
    hands, img = detector.findHands(img)  # with draw
    # hands = detector.findHands(img, draw=False)  # without draw
    try:
        if hands:
            # Hand 1
           hand1 = hands[0]
           lmList1 = hand1["lmList"]  # List of 21 Landmark points
           bbox1 = hand1["bbox"]  # Bounding box info x,y,w,h
           centerPoint1 = hand1['center']  # center of the hand cx,cy
           handType1 = hand1["type"]  # Handtype Left or Right
           # cv2.circle(img,lmList1[8][:2],15, (0,0,255), -1)

# -------------------------------------------------------------
#
           result = dict({'thumb':angle(lmList1[4][:2] ,lmList1[3][:2],lmList1[1][:2]),'index':angle(lmList1[8][:2] , lmList1[6][:2],lmList1[5][:2]),
                                    'middle':angle(lmList1[12][:2] , lmList1[10][:2],lmList1[9][:2]),
                                    'ring':angle(lmList1[16][:2] , lmList1[14][:2],lmList1[13][:2]),
                                    'pinky':angle(lmList1[20][:2] , lmList1[18][:2],lmList1[17][:2]),
                                    'thumb2':angle(lmList1[3][:2] , lmList1[2][:2],lmList1[1][:2])})

           mylist = []
           for key, value in result.items():
                 # thumb angle
                if key == 'thumb' :
                    if (value <= 180  and 110 < value) and (angle(lmList1[4][:2] ,lmList1[2][:2],lmList1[1][:2]) >110 and angle(lmList1[4][:2] ,lmList1[2][:2],lmList1[1][:2]) <=180):
                           mylist.append(0)
                    else:
                        mylist.append(1)

                # index finger angle
                if key == 'index':
                    if value <= 180  and 90 < value:
                            mylist.append(0)
                    if value <= 90  and 0 <= value:
                           mylist.append(1)

                # middle finger angle
                if key == 'middle':
                    if value <= 180  and 90 < value:
                           mylist.append(0)
                    if value <= 90  and 0 <= value:
                           mylist.append(1)

                # ring finger angle
                if key == 'ring':
                    if value <= 180  and 90 < value:
                                mylist.append(0)

                    if value <= 90  and 0 <= value:
                                mylist.append(1)

                # pinkey finger angle
                if key == 'pinky':
                    if value <= 180  and 90 < value:
                            mylist.append(0)

                    if value <= 90  and 0 <= value:
                           mylist.append(1)
                # thumb inward and outward movement
                if key == 'thumb2':
                    if value <= 180  and 145 < value:
                            mylist.append(0)

                    if value <= 145  and 0 <= value:
                           mylist.append(1)



        # appending all results in a string ang then printing it.
        listToStr = ''.join([str(elem) for elem in mylist])
        listToStr='$'+listToStr
        print(listToStr)

        # we can detect right and left hand and  then below code will create boundary box
        if len(hands) == 2:
            # Hand 2
            hand2 = hands[1]
            lmList2 = hand2["lmList"]  # List of 21 Landmark points
            bbox2 = hand2["bbox"]  # Bounding box info x,y,w,h
            centerPoint2 = hand2['center']  # center of the hand cx,cy
            handType2 = hand2["type"]  # Hand Type "Left" or "Right"

            fingers2 = detector.fingersUp(hand2)

            # Find Distance between two Landmarks. Could be same hand or different hands
            length, info, img = detector.findDistance(lmList1[8], lmList2[8], img)  # with draw
            # length, info = detector.findDistance(lmList1[8], lmList2[8])  # with draw
    except:
        continue
    # Display
    cv2.imshow("Image", img)
    if cv2.waitKey(1)  & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
