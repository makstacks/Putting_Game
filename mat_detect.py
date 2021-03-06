import cv2
import numpy as np

def nothing(x):
    # any operation
    pass

def detect_mat(cap):

    approx_mat = 0.03
    approx_holes = 0.003

    kern_mat = 8
    kern_holes = 15

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


    cv2.namedWindow("Trackbars mat")
    cv2.createTrackbar("L-H", "Trackbars mat", 30, 180, nothing)
    cv2.createTrackbar("L-S", "Trackbars mat", 5, 255, nothing)
    cv2.createTrackbar("L-V", "Trackbars mat", 5, 255, nothing)
    cv2.createTrackbar("U-H", "Trackbars mat", 110, 180, nothing)
    cv2.createTrackbar("U-S", "Trackbars mat", 255, 255, nothing)
    cv2.createTrackbar("U-V", "Trackbars mat", 255, 255, nothing)
    cv2.namedWindow("Trackbars hole")
    cv2.createTrackbar("L-H", "Trackbars hole", 30, 180, nothing)
    cv2.createTrackbar("L-S", "Trackbars hole", 5, 255, nothing)
    cv2.createTrackbar("L-V", "Trackbars hole", 5, 255, nothing)
    cv2.createTrackbar("U-H", "Trackbars hole", 110, 180, nothing)
    cv2.createTrackbar("U-S", "Trackbars hole", 255, 255, nothing)
    cv2.createTrackbar("U-V", "Trackbars hole", 255, 255, nothing)

    font = cv2.FONT_HERSHEY_COMPLEX
    count = 0
    while True:

        _, frame = cap.read()
        height, width, _ = frame.shape
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        l_h = cv2.getTrackbarPos("L-H", "Trackbars mat")
        l_s = cv2.getTrackbarPos("L-S", "Trackbars mat")
        l_v = cv2.getTrackbarPos("L-V", "Trackbars mat")
        u_h = cv2.getTrackbarPos("U-H", "Trackbars mat")
        u_s = cv2.getTrackbarPos("U-S", "Trackbars mat")
        u_v = cv2.getTrackbarPos("U-V", "Trackbars mat")

        # lower_green = np.array([30, 5, 5])
        # upper_green = np.array([110, 255, 255])
        lower_green = np.array([l_h, l_s, l_v])
        upper_green = np.array([u_h, u_s, u_v])

        mask = cv2.inRange(hsv, lower_green, upper_green)
        kernel = np.ones((kern_mat, kern_mat), np.uint8)
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
            approx = cv2.approxPolyDP(cnt, approx_mat*cv2.arcLength(cnt, True), True)
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

        w_mat = maxx - minx

        polyfill1 = np.array([[0, 0], [minxmin, 0], [minx, maxy], [0, maxy]])
        polyfill2 = np.array([[0, maxy], [minx, maxy], [minx, height], [0, height]])
        polyfill3 = np.array([[maxx, maxy], [width, maxy], [width, height], [maxx, height]])
        polyfill4 = np.array([[maxxmin, 0], [width, 0], [width, maxy], [maxx, maxy]])
        #polyfill5 = np.array([[minx, maxy], [maxx, maxy], [maxx, height], [minx, height]])
        cv2.fillPoly(frame, pts=[polyfill1], color=(255,255,255))
        cv2.fillPoly(frame, pts=[polyfill2], color=(255,255,255))
        cv2.fillPoly(frame, pts=[polyfill3], color=(255,255,255))
        cv2.fillPoly(frame, pts=[polyfill4], color=(255,255,255))
        #cv2.fillPoly(frame, pts=[polyfill5], color=(255,255,255))

        frame2 = frame.copy()
        hsv2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV)


        l_hh = cv2.getTrackbarPos("L-H", "Trackbars hole")
        l_sh = cv2.getTrackbarPos("L-S", "Trackbars hole")
        l_vh = cv2.getTrackbarPos("L-V", "Trackbars hole")
        u_hh = cv2.getTrackbarPos("U-H", "Trackbars hole")
        u_sh = cv2.getTrackbarPos("U-S", "Trackbars hole")
        u_vh = cv2.getTrackbarPos("U-V", "Trackbars hole")

        # lower_hole = np.array([37, 10, 10])
        # upper_hole = np.array([150, 255, 255])
        lower_hole = np.array([l_hh, l_sh, l_vh])
        upper_hole = np.array([u_hh, u_sh, u_vh])

        mask2 = cv2.inRange(hsv2, lower_hole, upper_hole)
        kernel = np.ones((kern_holes, kern_holes), np.uint8)
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
            contours2, _ = cv2.findContours(mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        else:
            # Opencv 3.x.x
            _, contours2, _ = cv2.findContours(mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        frame3 = frame2.copy()
        for cnt in contours2:
            area = cv2.contourArea(cnt)
            approx = cv2.approxPolyDP(cnt, approx_holes*cv2.arcLength(cnt, True), True)
            x = approx.ravel()[0]
            y = approx.ravel()[1]

            if 500 < area < (720 * 1280) / 4:
                #Draw contours for detecting hole
               # cv2.drawContours(frame2, [approx], 0, (0, 0, 255), 3)

                # if len(approx) == 3:
                #     cv2.putText(frame2, "Triangle", (x, y), font, 1, (0, 0, 0))
                # elif len(approx) == 4:
                #     cv2.putText(frame2, "Rectangle", (x, y), font, 1, (0, 0, 0))
                # Identify candidates for potential holes
                if 20 < len(approx):
                    #cv2.putText(frame2, "Circle", (x, y), font, 1, (0, 0, 0))
                    id_point_candidates.append(cnt)

            for cnt in id_point_candidates:
                x, y, w, h = cv2.boundingRect(cnt)
                ellipse = cv2.fitEllipse(cnt)
                #print(ellipse)
                #points.append(cnt[:])
                #origins.append((x, y))
                ellipses.append(ellipse)

                ex = round(ellipse[0][0])
                ey = round(ellipse[0][1])

                Hr = round(ellipse[1][0] / 2)
                Hh = round(ellipse[1][0] / 2)

                H_ax_l = (Hr, Hh)

                Hr = round(w / 2)
                Hh = round(h / 2)

                ex = round(x) + Hr
                ey = round(y) + Hh


                H_ax_l = (round(w/2), round(h/2))


                # if hole is within our limits
                if w_mat / 12 < Hr < w_mat / 4:
# store in first array if small hole and second (index 1) if big hole
                    if ex < maxx - w_mat / 2:
                        H1_cx = ex
                        H1_cy = ey
                        r1 = Hr + 5
                        h1 = Hh + 5
                        H1_ax_l = (r1, h1)
                    else:
                        H2_cx = ex
                        H2_cy = ey
                        r2 = Hr + 10
                        h2 = Hh + 10
                        H2_ax_l = (r2, h2)
                #cv2.ellipse(frame, origins[cnt], )
                    #cv2.rectangle(frame2, (x, y), (x + w, y + h), (0, 0, 255), 1)
                    cv2.ellipse(frame3, (ex, ey), H_ax_l, angle, startAngle, endAngle, (23, 30, 255), 3)


        minandmax = [minx, maxx, miny, maxy, minxmin, maxxmin, n3ay, H1_cx, H1_cy, H1_ax_l, r1, h1, H2_cx, H2_cy, H2_ax_l, r2, h2]
        #cv2.putText(frame2, "Press ENTER to proceed", (20, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)

        #cv2.putText(frame2, "Press ENTER to proceed", (20, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)

        # Let's see the results:
        #cv2.imshow("Frame for mat detect", frame)
        cv2.imshow("Frame", frame3)
        #cv2.imshow("Mask", mask2)

        key = cv2.waitKey(0)
        # if user wants to draw circles
        if key == ord("d"):
            #cv2.destroyAllWindows()
            r1est = round(w_mat / 12)
            h1est = r1est
            r2est = round(w_mat / 12)
            h2est = r2est
            cx1est = round(minx + w_mat / 4)
            cy1est = round(maxy - 2 * r1est)
            cx2est = round(maxx - w_mat / 4)
            cy2est = cy1est
            # cv2.namedWindow("Trackbars hole draw")
            # cv2.createTrackbar("r1", "Trackbars mat", r1est, 2*r1est, nothing)
            # cv2.createTrackbar("h1", "Trackbars mat", 5, 255, nothing)
            # cv2.createTrackbar("cx1", "Trackbars mat", 5, 255, nothing)
            # cv2.createTrackbar("cy1", "Trackbars mat", 110, 180, nothing)
            # cv2.createTrackbar("r2", "Trackbars mat", 30, 180, nothing)
            # cv2.createTrackbar("h2", "Trackbars mat", 5, 255, nothing)
            # cv2.createTrackbar("cx2", "Trackbars mat", 5, 255, nothing)
            # cv2.createTrackbar("cy2", "Trackbars mat", 110, 180, nothing)
            while True:

                cv2.ellipse(frame3, (cx1est, cy1est), (r1est, h1est), 0, 0, 0, (23, 30, 255), 3)
                cv2.ellipse(frame3, (cx2est, cy2est), (r2est, h2est), 0, 0, 0, (23, 30, 255), 3)
                # r1est = cv2.getTrackbarPos("L-H", "Trackbars hole")
                # l_sh = cv2.getTrackbarPos("L-S", "Trackbars hole")
                # l_vh = cv2.getTrackbarPos("L-V", "Trackbars hole")
                # u_hh = cv2.getTrackbarPos("U-H", "Trackbars hole")
                # u_sh = cv2.getTrackbarPos("U-S", "Trackbars hole")
                # u_vh = cv2.getTrackbarPos("U-V", "Trackbars hole")
                cv2.imshow("draw holes", frame2)
                cv2.waitKey(30)

        elif key == 13 or key == 27:
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

# cap = cv2.VideoCapture("C:\\Users\\Salmonservices\\putting_game\\assets\\perfectpractice.mp4")
# cap = cv2.VideoCapture(0)
# detect_mat(cap)
