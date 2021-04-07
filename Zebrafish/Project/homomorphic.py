import cv2
import numpy as np
import math


def hom_filter(fname, out_fname):
    cutoff, order, boost = 0.45, 2, 2
    img = cv2.imread(fname, 1)
    img = np.float32(img)

    rows, cols, dim = img.shape

    img = (img - img.min()) / (img.max() - img.min())

    '''
    imgYCrCb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(imgYCrCb)
    '''

    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(img_hsv)

    v = v - np.min(v)
    v = v / np.max(v)

    v_log = np.log(v+0.01)

    v_fft = np.fft.fft2(v_log)

    v_fft_shift = np.fft.fftshift(v_fft)

    G = np.ones((rows, cols))

    xrange = []
    yrange = []

    for i in range(int((img.shape[1]) / -2), int(img.shape[1] / 2 - 1)):
        xrange.append(i / img.shape[1])
    for j in range(int((img.shape[0]) / -2), int(img.shape[0] / 2 - 1)):
        yrange.append(j / img.shape[0])
    y, x = np.meshgrid(yrange, xrange, sparse=False, indexing='ij')
    radius = []
    k = 0
    for i in range(y.shape[0]):
        for j in range(x.shape[1]):
            radius.append(math.sqrt(math.pow(y[i][j], 2)) + math.pow(x[i][j], 2))
            G[i, j] = (1.0 - 1/boost)*(1.0 - (1.0 / (1.0 + math.pow(radius[k] / cutoff, (2 * order))))) + 1/boost
            #G[i, j] = 1.0 / (1.0 + math.pow(radius[k] / cutoff, (2 * order)))
            k = k + 1
    G = 1 - G
    G = ((1-1/2) * G) + 1/2

    result_filter = G * v_fft_shift

    result_interm = np.real(np.fft.ifft2(np.fft.ifftshift(result_filter)))

    result = np.exp(result_interm)
    result = np.float32(result)


    #f = cv2.merge((result, cr, cb))
    f = cv2.merge((h, s, result))

    #colored = cv2.cvtColor(f, cv2.COLOR_YCrCb2BGR)
    #fin = cv2.cvtColor(colored, cv2.COLOR_BGR2GRAY)
    colored = cv2.cvtColor(f, cv2.COLOR_HSV2BGR)
    fin = cv2.cvtColor(colored, cv2.COLOR_BGR2GRAY)
    final = ((fin-0.01)*255).astype(np.uint8)

    final_image = cv2.equalizeHist(final)
    #cv2.imshow('display', final_image)


    cv2.imwrite(out_fname, final_image)
