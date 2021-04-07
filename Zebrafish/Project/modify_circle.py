import cv2
import Project.backend

drawing = False

def draw_circle(event, x, y, flags, param):
    global x1, y1, drawing, radius, num, img, img2, cimg
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        cimg = img.copy()
        img2 = cimg.copy()
        cv2.circle(cimg, (x, y), radius, (0, 0, 255), 6)
        cv2.circle(cimg, (x, y), 1, (255, 0, 0), 6)

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            a, b = x, y
            if a != x & b != y:
                cimg = img2.copy()
                cv2.circle(cimg, (x,y), radius, (0, 0, 255), 6)
                cv2.circle(cimg, (x, y), 1, (255, 0, 0), 6)

    elif event == 10:
        drawing == True
        cimg = img2.copy()
        if flags > 0:
            radius = radius + 5
            cv2.circle(cimg, (x, y), radius, (0, 0, 255), 6)
            cv2.circle(cimg, (x, y), 1, (255, 0, 0), 6)
        else:
            radius = radius - 5
            cv2.circle(cimg, (x, y), radius, (0, 0, 255), 6)
            cv2.circle(cimg, (x, y), 1, (255, 0, 0), 6)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.circle(cimg, (x,y), radius, (0, 0, 255), 6)
        cv2.circle(cimg, (x, y), 1, (255, 0, 0), 6)
        img2 = img.copy()


def give_name(par1, par2):
    global name, img, img2, cimg, radius
    data = Project.backend.select_radius(par1.split("/")[-1])
    for i in range(len(data)):
        (x, y, r, i_n) = data[i]
        radius = r
    name = par1
    windowName = name
    cimg = cv2.imread(par1)
    img = cv2.imread(par2)
    img2 = img.copy()
    cv2.namedWindow(windowName)
    cv2.setMouseCallback(windowName, draw_circle)
    while (True):
        cv2.imshow(windowName, cimg)
        k = cv2.waitKey(20)
        if k == 27:
            cv2.destroyAllWindows()
            break
        if k == 13:
            cv2.destroyAllWindows()
            cv2.imwrite(par1, cimg)
            Project.backend.updadte_circle(x, y, radius, par1.split("/")[-1])
            break
