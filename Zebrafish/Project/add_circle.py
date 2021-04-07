import cv2
import math

import Project.backend

drawing = False
num = 0


def draw_circle(event, x, y, flags, param):
    global x1, y1, drawing, radius, num, img, img2, name
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        x1, y1 = x, y
        radius = int(math.hypot(x - x1, y - y1))
        cv2.circle(img, (x1,y1), radius, (0, 0, 255), 3)
        cv2.circle(img, (x1, y1), 1, (255, 0, 0), 3)

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            a, b = x, y
            if a != x & b != y:
                img = img2.copy()
                radius = int(math.hypot(a - x1, b - y1))
                cv2.circle(img, (x1,y1), radius, (0, 0, 255), 3)
                cv2.circle(img, (x1, y1), 1, (255, 0, 0), 3)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        radius = int(math.hypot(x - x1, y - y1))
        cv2.circle(img, (x1,y1), radius, (0, 0, 255), 3)
        cv2.circle(img, (x1, y1), 1, (255, 0, 0), 3)



def give_name(par):
    global name, img2, img
    name = par
    windowName = name
    img = cv2.imread(name)
    img2 = img.copy()
    cv2.namedWindow(windowName)
    cv2.setMouseCallback(windowName, draw_circle)
    while (True):
        cv2.imshow(windowName, img)
        k = cv2.waitKey(20)
        if k == 27:
            cv2.destroyAllWindows()
            break
        elif k == 13:
            cv2.destroyAllWindows()
            lastname = name.split("/")[-1].split(".")[0] + "_houghcircle" + ".JPG"
            fn = ""
            fullname = name.split("/")
            for i in fullname:
                if i != name.split("/")[-1]:
                    if fn == "":
                        fn = fn + i
                    else:
                        fn = fn + "/" + i
            fn = fn + "/Elofeldolgozott/" + lastname
            if(cv2.imwrite(fn, img)):
                Project.backend.insert_circle(x1, y1, radius, lastname)
            break
