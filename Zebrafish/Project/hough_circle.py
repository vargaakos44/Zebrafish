import cv2
import numpy as np

import Project.backend

minR = 640
maxR = 680


def hc_detect(fname, out_fname):
    global r
    im = cv2.imread(fname, cv2.IMREAD_COLOR)
    im_name = fname.split("/")[-1]
    lastname = im_name.split("/")[-1].split(".")[0] + "_houghcircle" + ".JPG"
    src = cv2.resize(im, None, fx=0.5, fy=0.5)
    hcMinR = int(0.5 + minR / 2)
    hcMaxR = int(0.5 + maxR / 2)

    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    rows = gray.shape[0]
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 16,
                               param1=210, param2=15,
                               minRadius=hcMinR, maxRadius=hcMaxR)
    if circles is None:
        src = cv2.resize(src, None, fx=2.0, fy=2.0)
        cv2.imwrite(out_fname, src)
        return [-1, -1, -1]

    circles_round = np.uint16(np.around(circles))
    for idx in range(0, 1):
        i = circles_round[0, idx]
        center = (i[0], i[1])
        # circle center
        cv2.circle(src, center, 1, (255, 0, 0), 3)
        # circle outline
        radius = i[2]
        cv2.circle(src, center, radius, (idx * 255, 0, 255), 3)

    fin = cv2.resize(src, None, fx=2.0, fy=2.0)
    cv2.imwrite(out_fname, fin)
    x = int(center[0])
    x = x*2
    y = int(center[1])
    y = y*2
    r = radius.item()
    r = r*2
    Project.backend.insert_circle(x, y, r, lastname)


'''def hc_avarage(list):
    r_list = []
    for image in list:


        im = cv2.imread(image, cv2.IMREAD_COLOR)
        src = cv2.resize(im, None, fx=0.5, fy=0.5)
        hcMinR = int(0.5 + minR / 2)
        hcMaxR = int(0.5 + maxR / 2)

        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        rows = gray.shape[0]
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 16, param1=210, param2=15, minRadius=hcMinR,
                                   maxRadius=hcMaxR)
        if circles is None:
            r_list.append(0)
            continue
        circles_round = np.uint16(np.around(circles))
        for idx in range(0, 1):
            i = circles_round[0, idx]
            center = (i[0], i[1])
            # circle center
            cv2.circle(src, center, 1, (255, 0, 0), 3)
            # circle outline
            radius = i[2]
            cv2.circle(src, center, radius, (idx * 255, 0, 255), 3)
        r_list.append(radius.item())

    return r_list'''

