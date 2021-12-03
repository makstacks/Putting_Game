import cv2
import numpy as np

def nothing(x):
    # any operation
    pass

def detect_mat(cap):

    minx = 0
    minxmin = 75
    maxx = 100
    maxxmin = 25
    miny = 0
    maxy = 200
    n3ay = 100
    r1 = 10
    h1 = 10
    r2 = 20
    h2 = 20
    H1_ax_l = (r1, h1)
    H2_ax_l = (r2, h2)
    H1_cx = 100
    H1_cy = 100
    H2_cx = 200
    H2_cy = 200
    minandmax = [minx, maxx, miny, maxy, minxmin, maxxmin, n3ay]


    # cv2.namedWindow("Trackbars")
    # cv2.createTrackbar("L-H", "Trackbars", 30, 180, nothing)
    # cv2.createTrackbar("L-S", "Trackbars", 5, 255, nothing)
    # cv2.createTrackbar("L-V", "Trackbars", 5, 255, nothing)
    # cv2.createTrackbar("U-H", "Trackbars", 110, 180, nothing)
    # cv2.createTrackbar("U-S", "Trackbars", 255, 255, nothing)
    # cv2.createTrackbar("U-V", "Trackbars", 255, 255, nothing)

    font = cv2.FONT_HERSHEY_COMPLEX
    count = 0
    while True:

        _, frame = cap.read()
        height, width, _ = frame.shape
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #
        # l_h = cv2.getTrackbarPos("L-H", "Trackbars")
        # l_s = cv2.getTrackbarPos("L-S", "Trackbars")
        # l_v = cv2.getTrackbarPos("L-V", "Trackbars")
        # u_h = cv2.getTrackbarPos("U-H", "Trackbars")
        # u_s = cv2.getTrackbarPos("U-S", "Trackbars")
        # u_v = cv2.getTrackbarPos("U-V", "Trackbars")

        lower_green = np.array([30, 5, 5])
        upper_green = np.array([110, 255, 255])

        mask = cv2.inRange(hsv, lower_green, upper_green)
        kernel = np.ones((8, 8), np.uint8)
        mask = cv2.erode(mask, kernel)
        ret, thresh = cv2.threshold(mask, 80, 255, cv2.THRESH_BINARY)

# Contours detection
        if int(cv2.__version__[0]) > 3:
            # Opencv 4.x.x
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            #contours, hierarchy= cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        else:
            # Opencv 3.x.x
            _, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            #_, contours, hierarchy= cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            #if area < 200:
               # contours[cnt] = 0
            approx = cv2.approxPolyDP(cnt, 0.03*cv2.arcLength(cnt, True), True)
            x = approx.ravel()[0]
            y = approx.ravel()[1]

        # create hull array for convex hull points
        hull = []
        hullx = []
        hullxmin = []
        hully3 = []
        hully = []
        # calculate points for each contour
        for i in range(len(contours)):
        # creating convex hull object for each contour
            hull.append(cv2.convexHull(contours[i], False))
        drawing = np.zeros((thresh.shape[0], thresh.shape[1], 3), np.uint8)

        for i in range(len(hull)):
            for j in range(len(hull[i])):
                hullx.append(hull[i][j][-1][0])
                hully.append(hull[i][j][-1][1])
                minx = min(hullx)
                maxx = max(hullx)
                miny = min(hully)
                maxy = max(hully)
                if hull[i][j][-1][1] == 0:
                    hullxmin.append(hull[i][j][-1][0])
                    minxmin = min(hullxmin)
                    maxxmin = max(hullxmin)
                if hull[i][j][-1][0] == minx:
                    hully3.append(hull[i][j][-1][1])
                    #print(hully3)
                    n3ay = hully3[-1]

        color = (0, 0, 255)
        line_colour = (0, 0, 255)
        line_thickness = 2
        rn = 3
        n1 = (minxmin, miny)
        n2 = (maxxmin, miny)
        n3 = (minx, maxy)
        n4 = (maxx, maxy)
        node1 = cv2.circle(frame, n1, rn, color, 6)
        node2 = cv2.circle(frame, n2, rn, color, 6)
        node3 = cv2.circle(frame, n3, rn, color, 6)
        node4 = cv2.circle(frame, n4, rn, color, 6)

        w_matend = maxx - minx

        polyfill1 = np.array([[0, 0], [minxmin, 0], [minx, maxy], [0, maxy]])
        polyfill2 = np.array([[0, maxy], [minx, maxy], [minx, height], [0, height]])
        polyfill3 = np.array([[maxx, maxy], [width, maxy], [width, height], [maxx, height]])
        polyfill4 = np.array([[maxxmin, 0], [width, 0], [width, maxy], [maxx, maxy]])
        polyfill5 = np.array([[minx, maxy], [maxx, maxy], [maxx, height], [minx, height]])
        cv2.fillPoly(frame, pts=[polyfill1], color=(255,255,255))
        cv2.fillPoly(frame, pts=[polyfill2], color=(255,255,255))
        cv2.fillPoly(frame, pts=[polyfill3], color=(255,255,255))
        cv2.fillPoly(frame, pts=[polyfill4], color=(255,255,255))
        cv2.fillPoly(frame, pts=[polyfill5], color=(255,255,255))


        frame2 = frame.copy()
        hsv2 = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_hole = np.array([37, 0, 0])
        upper_hole = np.array([147, 255, 255])

        mask2 = cv2.inRange(hsv2, lower_hole, upper_hole)
        kernel = np.ones((18, 18), np.uint8)
        mask2 = cv2.erode(mask2, kernel)

        points = []
        origins = []
        ellipses = []
        id_point_candidates = []
        small_point_candidates = []

        angle = 0
        startAngle = 0
        endAngle = 360

        holes = [[]] * 2

        # Contours detection
        if int(cv2.__version__[0]) > 3:
            # Opencv 4.x.x
            contours, _ = cv2.findContours(mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        else:
            # Opencv 3.x.x
            _, contours, _ = cv2.findContours(mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            approx = cv2.approxPolyDP(cnt, 0.001*cv2.arcLength(cnt, True), True)
            x = approx.ravel()[0]
            y = approx.ravel()[1]

            if area > 200:
                #cv2.drawContours(frame2, [approx], 0, (0, 0, 255), 3)

                # if len(approx) == 3:
                #     cv2.putText(frame2, "Triangle", (x, y), font, 1, (0, 0, 0))
                # elif len(approx) == 4:
                #     cv2.putText(frame2, "Rectangle", (x, y), font, 1, (0, 0, 0))
                if 10 < len(approx):
                    #cv2.putText(frame2, "Circle", (x, y), font, 1, (0, 0, 0))
                    id_point_candidates.append(cnt)


            # for cnt in contours:
            #     if cv2.contour_sanity_check(cnt, cv2.im.shape[0], point_d=0.02):
            #         id_point_candidates.append(cnt)
            #     elif cv2.contour_sanity_check(cnt, cv2.im.shape[0], point_d=0.01):
            #         small_point_candidates.append(cnt)
            for cnt in id_point_candidates:
                x, y, w, h = cv2.boundingRect(cnt)
                ellipse = cv2.fitEllipse(cnt)
                #print(ellipse)
                points.append(cnt[:])

                ex = round(ellipse[0][0])
                ey = round(ellipse[0][1])

                Hr = round(ellipse[1][0] / 2)
                Hh = round(ellipse[1][0] / 2)

                H_ax_l = (Hr, Hh)

                # if hole is within our limits
                if w_matend / 6 < Hr < w_matend / 3:
# store in first array if small hole and second (index 1) if big hole
                    if ex < maxx - w_matend / 2:
                        H1_cx = ex
                        H1_cy = ey
                        r1 = Hr
                        h1 = Hh
                        H1_ax_l = (r1, h1)
                    else:
                        H2_cx = ex
                        H2_cy = ey
                        r2 = Hr
                        h2 = Hh
                        H2_ax_l = (r2, h2)


                origins.append((x, y))
                ellipses.append(ellipse)
                #cv2.ellipse(frame, origins[cnt], )
                cv2.rectangle(frame2, (x, y), (x + w, y + h), (0, 0, 255), 1)
                cv2.ellipse(frame2, (ex, ey), H_ax_l, angle, startAngle, endAngle, (255, 0, 0), 3)

        minandmax = [minx, maxx, miny, maxy, minxmin, maxxmin, n3ay, H1_cx, H1_cy, H1_ax_l, r1, h1, H2_cx, H2_cy, H2_ax_l, r2, h2]
        cv2.putText(frame, "ENTER to proceed", (20, 50), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 255), 2)

    # Let's see the results:
        cv2.imshow("Frame for mat detect", frame)
        cv2.imshow("Frame", frame2)
        cv2.imshow("Mask", mask2)

        key = cv2.waitKey(0)
        if key == 13 or key == 27:
            #cap.release()
            print("H1")
            print(H1_cx, H1_cy)
            print(r1)
            print("H2")
            print(H2_cx, H2_cy)
            print(r2)
            cv2.destroyAllWindows()
    #            print(minandmax)
            return minandmax
            #break

# #cap = cv2.VideoCapture("C:\\Users\\Salmonservices\\putting_game\\puts.MOV")
# cap = cv2.VideoCapture(0)
# detect_mat(cap)
