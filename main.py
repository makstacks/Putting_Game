import cv2
from tracker import *
from mat_detect import *
#from hole_detect import *
import game_calculator
import imutils
import pickle
import time
from collections import deque
from imutils.video import VideoStream
#
cap = cv2.VideoCapture("C:\\Users\\Salmonservices\\putting_game\\bigholetest.mp4")
cap = cv2.VideoCapture(0)
time.sleep(2)

# functions to determine if two lines intersect
def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

# Return true if line segments AB and CD intersect
def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def is_empty(any_structure):
    if any_structure:
        return False
    else:
        return True

# function to check if point is within ellipse (hole)
def is_in_hole(x, y, h, k, rx, ry):
    if ((x - h)**2) / rx**2 + ((y - k)**2) / ry**2 <= 1:
        return True
    else:
        return False

def start_game(cap):
    # get user inputs for number of players/teams/game modes
    #game_mode = input("Select game mode\n [F] Free Play\n [P] Points Game\n> ")
    #game_mode = "F"
    game_mode = "P"
    num_players = 4
    team_no = 2
    if game_mode != "F" and game_mode != "f" and game_mode != "P" and game_mode != "p":
        start_game(cap)
    if game_mode == "f" or game_mode == "F":
        game_mode = "F"
        game_string = "FREE PLAY"
        num_players = 1
        team_no = 1
    if game_mode == "p" or game_mode == "P":
        game_mode = "P"
        game_string = "POINTS GAME"
    # if game_mode != "F":
    #     num_players = int(input("Enter number of players\n> "))
    #     if num_players < 3:
    #         team_no = num_players
    #     else:
    #         team_no = int(input("Enter number of Teams\n> "))

    rounds = 3
    shotspround = 3

    players = [] * num_players
    game_string = "HOLY MOLY"
    # define points amount for points game
    s_pts = 1.5
    b_pts = 1

    for n in range(num_players):
        players.append(n+1)
        players.append(n+1)

    if num_players == 1:
        teams = [[1]]
        team_no = 1
    elif num_players != 1:
        #team_no = int(input("Select how many teams (e.g. 4p, 2 teams = 2v2\n> "))
        teams = [[] for i in range(team_no)]
        if num_players == 2:
            if team_no == 1:
                teams = [[1, 2]]
            elif team_no == 2:
                teams = [[1], [2]]
        elif num_players == 3:
            if team_no == 1:
                teams = [[1, 2, 3]]
            elif team_no == 2:
                teams = [[1], [2, 3]]
            elif team_no == 3:
                teams = [[1], [2], [3]]
        elif num_players == 4:
            if team_no == 1:
                teams = [[1, 2, 3, 4]]
            elif team_no == 2:
                teams = [[1, 2], [3, 4]]
            elif team_no == 3:
                teams = [[1], [2], [3, 4]]
            elif team_no == 4:
                teams = [[1], [2], [3], [4]]
        elif num_players == 5:
            if team_no == 1:
                teams = [[1, 2, 3, 4, 5]]
            elif team_no == 2:
                teams = [[1, 2], [3, 4, 5]]
            elif team_no == 3:
                teams = [[1], [2, 3], [4, 5]]
            elif team_no == 4:
                teams = [[1], [2], [3], [4, 5]]
            elif team_no == 5:
                teams = [[1], [2], [3], [4], [5]]
        elif num_players == 6:
            if team_no == 1:
                teams = [[1, 2, 3, 4, 5, 6]]
            elif team_no == 2:
                teams = [[1, 2, 3], [4, 5, 6]]
            elif team_no == 3:
                teams = [[1, 2], [3, 4], [5, 6]]
            elif team_no == 4:
                teams = [[1], [2], [3, 4], [5, 6]]
            elif team_no == 5:
                teams = [[1], [2], [3], [4], [5, 6]]
            elif team_no == 6:
                teams = [[1], [2], [3], [4], [5], [6]]
    team_string = ""
    for team in range(team_no):
        team_string = team_string + str(len(teams[team])) + "v"
    team_string = team_string[:-1]

    if team_no == num_players:
        team_bool = False
    else:
        team_bool = True

    # Create tracker object
    tracker = EuclideanDistTracker()

    # Object detection from Stable camera
    object_detector = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=50)

    shot_count = 0
    hole1_count = 0
    hole2_count = 0
    missed_count = 0
    object_shot = []
    object_hole1 = []
    object_hole2 = []
    object_holes = []
    object_missed = []
    oldyint = 0
    olderyint = 0
    oldxint = 0
    olderxint = 0
    distH1x = 0
    distH1y = 0
    distH1 = 0
    distH1xo = 0
    distH1yo = 0
    distH1o = 0
    distH2x = 0
    distH2y = 0
    distH2 = 0
    distH2xo = 0
    distH2yo = 0
    distH2o = 0
    shot_pcnt = 0
    shot_record = []
    p_ind = 1
    p_shots = 0
    cur_rnd = 1
    t_ind = 1
    # points per shot
    pps = 0
    streak_count = 0
    max_streak_count = 0
    H1streak_count = 0
    H2streak_count = 0

    # array to store how many rounds a player has completed
    p_rnd_comp = [0] * num_players

    cyo = [[] for i in range(1000)]
    cxo = [[] for i in range(1000)]
    cy_all = [[] for i in range(200)]
    cx_all = [[] for i in range(200)]
    cy_sh = [[] for i in range(200)]
    cx_sh = [[] for i in range(200)]
    p_scores = [[] for i in range(num_players)]
    t_scores = [[0] for i in range(team_no)]
    p_pts = [[] for i in range(num_players)]
    sum_p_pts = [[] for i in range(num_players)]
    pps_a = [[0] for i in range(num_players)]
    streak_count_a = [[] for i in range(num_players)]
    max_streak_a = [[0] for i in range(num_players)]
    H_count_a = [[] for i in range(num_players)]
    H1_count_a = [[] for i in range(num_players)]
    H2_count_a = [[] for i in range(num_players)]
    missed_count_a = [[] for i in range(num_players)]
    shot_count_a = [[] for i in range(num_players)]
    shot_pcnt_a = [[0] for i in range(num_players)]
    t_pts = [[] for i in range(team_no)]
    stats_list_a = [[] for i in range(num_players)]
    shot_zone1 = False
    shot_zone2 = False
    shot_bool = False
    miss_bool = False
    miss_left = False
    miss_right = False
    miss_end = False
    small_hole_bool = False
    big_hole_bool = False
    hole_bool = False
    streak_broke1 = False
    streak_broke2 = False
    streak_broke3 = False
    sz1bool = False
    sz2bool = False
    sz3bool = False

    matvals = detect_mat(cap)
# matvals = [minx, maxx, miny, maxy, minxmin, maxxmin, n3ay, H1_cx, H1_cy, H1_ax_l, r1, h1, H2_cx, H2_cy, H2_ax_l, r2, h2]
    minx = matvals[0]
    maxx = matvals[1]
    miny = matvals[2]
    maxy = matvals[3]
    minxmin = matvals[4]
    maxxmin = matvals[5]
    n3ay = matvals[6]
    H1_cx = matvals[7]
    H1_cy = matvals[8]
    H1_ax_l = matvals[9]
    r1 = matvals[10]
    h1 = matvals[11]
    H2_cx = matvals[12]
    H2_cy = matvals[13]
    H2_ax_l = matvals[14]
    r2 = matvals[15]
    h2 = matvals[16]

    # defining left/right/up/down points on holes
    H1_xl = H1_cx - r1
    H1_xr = H1_cx + r1
    H1_yu = H1_cy - h1
    H1_yd = H1_cy + h1
    H2_xl = H2_cx - r1
    H2_xr = H2_cx + r1
    H2_yu = H2_cy - h2
    H2_yd = H2_cy + h2

    #hw_ratio = round(hmax_mat / wmax_mat, 1)
    # gaps between shot zones
    szy_adj = 150
    szy_inter = 50
    #nodes coordinates
    n1x = minxmin
    n1y = miny
    n2x = maxxmin
    n2y = n1y
    n3x = minx
    n3y = n3ay
    n4x = maxx
    n4y = maxy
    n5x = minx
    n5y = n1y + szy_adj
    n6x = maxx
    n6y = n5y
    n7x = n5y
    n7y = n5y
    n8x = n5y
    n8y = n5y

    node1 = (n1x, n1y)
    node2 = (n2x, n2y)
    node3 = (n3x, n3y)
    node4 = (n4x, n4y)
    node5 = (n5x, n5y)
    node6 = (n6x, n6y)

    roi1 = (n3x, n1y)
    roi2 = (n4x, n1y)
    roi3 = (n3x, n3y)
    roi4 = (n4x, n3y)

 # defining nodes for shot zones
    sz1n1 = node1
    sz1n2 = node2
    sz2n1 = node5
    sz2n2 = node6
    sz3n1y = n5y + szy_inter
    sz3n1 = (n5x, sz3n1y)
    sz3n2 = (n6x, sz3n1y)

    angle = 0
    startAngle = 0
    endAngle = 360

    sz1list = []
    sz2list = []
    sz3list = []

# define dimensions for stat positioning on scorecard
    hd = 720
    wd = 1280
    scorecard_fs = 2
    if num_players > 4:
        scorecard_fs = 1.5
    stat_fs = 1
    stat_th = 2
    stat_indent = 280
    statxsen = 30
    statysen = 60
    nameyst = 60
    nameyen = 160
    smdif = 80
    scrygap1 = 100
    scrygap2 = scrygap1 + 120
    scrygap3 = scrygap2 + smdif
    sc_end = nameyen + scrygap3 + smdif + smdif
    p_dist = round((wd - stat_indent) / (num_players))
    p_name_y = 80
    staty = []
    staty.append(nameyen + statysen)
    staty.append(nameyen + scrygap1 + statysen)
    staty.append(nameyen + scrygap2 + statysen)
    staty.append(nameyen + scrygap3 + statysen)
    staty.append(nameyen + scrygap3 + smdif + statysen)

    streakHSname = "streak_highscores.pkl"
    # with open(streakHSname, "rb") as fp:   #Pickling
    #     streak_highscores = pickle.load(fp)
    streak_highscores = [["N", 0], ["N", 0], ["N", 0]]

    # define dimensions for scoreboard drawing
    hb = 80
    hs = hb / 2
    # if not one player per team ie team game we want extra rows for total team scores

    # defining lines for scoreboard
    num_sec = num_players + team_no
    font_col = (100, 150, 100)
    font_colour = (0, 100, 0)
    font_thick = 2
    font_size = 2
    t_al_x = round(hb + hb / 8)
    ls_col = (100, 150, 100)
    ls_thick = 2
    ls_thin = round(ls_thick / 2)
    pls_thick = 10

    count = 0
    while True:

        ret, frame = cap.read()

        height, width, _ = frame.shape

        # Extract Region of interest
        roi = frame[miny: maxy, minx: maxx]

        line_colour = (0, 0, 255)
        line_thickness = 2

        # fill shapes to only reveal mat
        polyfill1 = np.array([[0, 0], [minxmin, 0], [minx, n3ay], [0, n3ay]])
        polyfill2 = np.array([[0, n3ay], [minx, n3ay], [minx, height], [0, height]])
        polyfill3 = np.array([[maxx, n3ay], [width, n3ay], [width, height], [maxx, height]])
        polyfill4 = np.array([[maxxmin, 0], [width, 0], [width, maxy], [maxx, maxy]])
        polyfill5 = np.array([[minx, maxy], [maxx, maxy], [maxx, height], [minx, height]])
        cv2.fillPoly(frame, pts=[polyfill1], color=(255,255,255))
        cv2.fillPoly(frame, pts=[polyfill2], color=(255,255,255))
        cv2.fillPoly(frame, pts=[polyfill3], color=(255,255,255))
        cv2.fillPoly(frame, pts=[polyfill4], color=(255,255,255))
        cv2.fillPoly(frame, pts=[polyfill5], color=(255,255,255))

        drawing = np.zeros((hd, wd, 3), dtype=np.uint8)
        drawing.fill(255)

        cv2.putText(drawing, str(game_string), (20, 40), cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 0, 0), 3)
        l1sc = cv2.line(drawing, (0, nameyst), (wd, nameyst), ls_col, ls_thick)
        l2sc = cv2.line(drawing, (280, nameyen), (wd, nameyen), ls_col, pls_thick)
        l2bsc = cv2.line(drawing, (0, nameyen), (280, nameyen), ls_col, ls_thick)
        l3sc = cv2.line(drawing, (0, nameyen + scrygap1), (wd, nameyen + scrygap1), ls_col, ls_thick)
        l4sc = cv2.line(drawing, (0, nameyen + scrygap2), (wd, nameyen + scrygap2), ls_col, ls_thick)
        l5sc = cv2.line(drawing, (0, nameyen + scrygap3), (wd, nameyen + scrygap3), ls_col, ls_thick)
        l6sc = cv2.line(drawing, (0, nameyen + scrygap3 + smdif), (wd, nameyen + scrygap3 + smdif), ls_col, ls_thick)
        l7sc = cv2.line(drawing, (0, sc_end), (wd, sc_end), ls_col, ls_thick + 5)
        stat1 = cv2.putText(drawing, "POINTS", (statxsen, staty[0]), cv2.FONT_HERSHEY_COMPLEX, stat_fs, (0, 0, 0), stat_th)
        stat2 = cv2.putText(drawing, "HOLES MADE", (statxsen, staty[1]), cv2.FONT_HERSHEY_COMPLEX, stat_fs, (0, 0, 0), stat_th)
        stat3 = cv2.putText(drawing, "SHOT %", (statxsen, staty[2]), cv2.FONT_HERSHEY_COMPLEX, stat_fs, (0, 0, 0), stat_th)
        stat4 = cv2.putText(drawing, "POINTS/SHOT", (statxsen, staty[3]), cv2.FONT_HERSHEY_COMPLEX, stat_fs, (0, 0, 0), stat_th)
        stat5 = cv2.putText(drawing, "MAX. STREAK", (statxsen, staty[4]), cv2.FONT_HERSHEY_COMPLEX, stat_fs, (0, 0, 0), stat_th)

        for p in range(num_players):
            lsp = cv2.line(drawing, (280 + p_dist * p, nameyst + 20), (280 + p_dist * p, sc_end), ls_col, pls_thick)

        # if num_players != team_no:
        #     for i in range(num_sec):
        #         ls1 = cv2.line(drawing, (0, 2*hb + (i + 1) * hb), (wd, 2 * hb + (i + 1) * hb), ls_col, ls_thick)
        # el

        for player in range(1, num_players + 1):
            for team in range(team_no):
                #print(teams[team])
                if player in teams[team] and num_players > 1:
                    p_fs = 2
                    p_xpos = round(280 + p_dist / 2 + (player - 1) * p_dist)
                    if not team_bool:
                        cv2.putText(drawing, str("P" + str(player)), (p_xpos, 140), cv2.FONT_HERSHEY_COMPLEX,
                                    p_fs, (0, 0, 0), 3)
                    else:
                        cv2.putText(drawing, str("P" + str(player)), (p_xpos, 140), cv2.FONT_HERSHEY_COMPLEX,
                                    p_fs * 0.75, (0, 0, 0), 3)
                # elif num_players == 1:
                #     cv2.putText(drawing, "Tiger", (t_al_x - 40, round(2*hb + hb - hb/4)), cv2.FONT_HERSHEY_COMPLEX, 1.4, (0, 0, 0), 3)


        for team_ref in range(team_no - 1):
            teaml_thick = 15
            teaml_fc = (0, 0, 0)
            if team_ref == 0:
                tline1x = stat_indent + (p_dist * len(teams[team_ref]))
                tline1 = cv2.line(drawing, (tline1x, nameyst), (tline1x, hd), teaml_fc, teaml_thick)
            elif team_ref == 1:
                tline2x = stat_indent + (p_dist * (len(teams[team_ref]) + len(teams[team_ref - 1])))
                #tline1 = cv2.line(drawing, (0, 2 * hb + len(teams[team_ref - 1])), (wd, 2 * hb + len(teams[team_ref])), font_col, 5)
                tline2 = cv2.line(drawing, (tline2x, nameyst), (tline2x, hd), teaml_fc, teaml_thick)
            elif team_ref == 2:
                tline3x = stat_indent + (p_dist * (len(teams[team_ref]) + len(teams[team_ref - 1]) + len(teams[team_ref - 2])))
                tline3 = cv2.line(drawing, (tline3x, nameyst), (tline3x, hd), teaml_fc, teaml_thick)


        # 1. Object Detection

        mask = object_detector.apply(frame)
        kernel = np.ones((8, 8), np.uint8)
        mask = cv2.erode(mask, kernel)

        _, mask = cv2.threshold(mask, 254.9, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        #detect_hole(roi)
        no_detection = False
        detections = []
        cent = []
        #maths for lines
        xmidmin = (minx + minxmin) / 2
        xmidmax = (maxx + maxxmin) / 2
        contr = 0
        for cnt in contours:
            # Calculate area and remove small elements
            area = cv2.contourArea(cnt)
            if area > 40:
                #cv2.drawContours(roi, [cnt], -1, (0, 255, 0), 2)
                x, y, w, h = cv2.boundingRect(cnt)
                # left_ind = y - (m1 * x) - c1
                # right_ind = y - (m2 * x) - c2
                #if left_ind > 0 and right_ind < 0 and y < maxy:
                detections.append([x, y, w, h])
            contr += 1

        if is_empty(contours):
            no_detection = True

        # 2. Object Tracking
        boxes_ids = tracker.update(detections, H1_xl, H1_xr, H2_xl, H2_xr, maxy, sz3n1y)
        a, b, c, d = [255, 390, 515, 480]

        for box_id in boxes_ids:
            x, y, w, h, id = box_id
            cv2.putText(frame, str(id), (x, y - 15), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)

        centr_dict = tracker.center_points
        zone_count = 0
        time_hole1 = 0
        time_hole2 = 0
        delx = 100
        dely = 100
        sens = r2
        # Main loop to identify shots
        for key in centr_dict:
            cx = centr_dict[key][0]
            cy = centr_dict[key][1]

            cyo[key].append([cy])
            cxo[key].append([cx])
            xinit = cxo[key][0][0]
            yinit = cyo[key][0][0]
            if key in object_shot:
                oldy = cyo[key][-2]
                oldery = cyo[key][-3]
                oldyint = int(oldy[-1])
                olderyint = int(oldery[-1])

                oldx = cxo[key][-2]
                olderx = cxo[key][-3]
                oldxint = int(oldx[-1])
                olderxint = int(olderx[-1])

                delx = ((cx - oldxint)**2)**0.5
                dely = ((cy - oldyint)**2)**0.5

                #print(key, delx, dely)

                # check intersections of ball path with lines at end of holes (to check misses)
                miss_end = intersect((cx, cy), (xinit, yinit), node3, node4)
                miss_left = intersect((cx, cy), (xinit, yinit), node3, node1)
                miss_right = intersect((cx, cy), (xinit, yinit), node4, node2)

                distH1x = ((cx - H1_cx)**2)**0.5
                distH1y = ((cy - H1_cy)**2)**0.5
                distH1 = (distH1x**2 + distH1y**2)**0.5
                distH1xo = ((oldxint - H1_cx)**2)**0.5
                distH1yo = ((oldyint - H1_cy)**2)**0.5
                distH1o = (distH1xo**2 + distH1yo**2)**0.5

                distH2x = ((cx - H2_cx)**2)**0.5
                distH2y = ((cy - H2_cy)**2)**0.5
                distH2 = (distH2x**2 + distH2y**2)**0.5
                distH2xo = ((oldxint - H1_cx)**2)**0.5
                distH2yo = ((oldyint - H1_cy)**2)**0.5
                distH2o = (distH2xo**2 + distH2yo**2)**0.5


            sz1bool = intersect((cx, cy), (xinit, yinit), node1, node2)
            sz2bool = intersect((cx, cy), (xinit, yinit), node5, node6)
            sz3bool = intersect((cx, cy), (xinit, yinit), sz3n1, sz3n2)

            if len(cyo[key]) > 1 and cyo[key][-1] > cyo[key][-2]:
                # if sz1bool and key not in sz1list and key not in sz2list and key not in sz3list and key not in object_shot:
                #     sz1list.append(key)
                if key not in sz2list and sz2bool:
                    sz2list.append(key)
                if key not in sz3list and key in sz2list and sz3bool:
                    sz3list.append(key)

            #if ball goes through zone register it as a shot if current y value greater than previous y position
                if key not in object_shot and key in sz3list and len(cyo[key]) > 2:
                    if minx < cx < maxx and cy < maxy and cyo[key][-1] > cyo[key][-2] > cyo[key][-3]:
                        shot_count += 1
                        #print(shot_count)
                        object_shot.append(key)
                        shot_bool = True
                        p_shots += 1
                        # if previous shot result not tracked register as miss
                        if len(object_shot) > 1:
                            if object_shot[-2] not in object_holes and object_shot[-2] not in object_missed:
                                object_missed.append(object_shot[-2])

            if key in object_shot and key not in object_missed and key not in object_holes:
                if miss_end or miss_left or miss_right:
                    object_missed.append(key)
                    missed_count += 1
                    streak_count = 0
                    H1streak_count = 0
                    H2streak_count = 0
                    shot_record.append(0)
                    miss_bool = True
                    print("miss wide/far")

                elif minx < cx < maxx and cy < H2_yu - 2 * r2 and cyo[key][-1] < cyo[key][-2] < cyo[key][-3]:
                    missed_count += 1
                    streak_count = 0
                    H1streak_count = 0
                    H2streak_count = 0
                    object_missed.append(key)
                    shot_record.append(0)
                    miss_bool = True
                    print("rolled back miss")

        # if a shot has been missed/holed set shot bool to false as shot is finished
        if miss_bool or hole_bool:
            shot_bool = False

        # if no object is being tracked and last shot result not tracked we check if it was a hole or miss
        if len(object_shot) > 0:
            last_shot_key = object_shot[-1]
            cxls = int(cxo[last_shot_key][-1][0])
            cyls = int(cyo[last_shot_key][-1][0])
            if no_detection and shot_bool:
            # Check if last traced location was within small hole
                if is_in_hole(cxls, cyls, H1_cx, H1_cy, r1, h1):
                    hole1_count += 1
                    streak_count += 1
                    H1streak_count += 1
                    H2streak_count = 0
                    object_hole1.append(key)
                    object_holes.append(key)
                    shot_record.append(1)
                    small_hole_bool = True
                    hole_bool = True
                    print("small hole")
            # check if ball in big hole
                elif is_in_hole(cxls, cyls, H2_cx, H2_cy, r2, h2):
                    hole2_count += 1
                    streak_count += 1
                    H2streak_count += 1
                    H1streak_count = 0
                    object_hole2.append(key)
                    object_holes.append(key)
                    shot_record.append(2)
                    big_hole_bool = True
                    hole_bool = True
                    print("big hole")

                    print(H2_cx, H2_cy)
                else:
                    missed_count += 1
                    streak_count = 0
                    H1streak_count = 0
                    H2streak_count = 0
                    object_missed.append(key)
                    shot_record.append(0)
                    miss_bool = True
                    # print("missed, dist to H1:")
                    # print(object_shot[-1], str(((cxls - H1_cx)**2)**0.5), str(((cyls - H1_cy)**2)**0.5), r2, h2)
                    # print("dist to H2:")
                    # print(object_shot[-1], str(((cxls - H2_cx)**2)**0.5), str(((cyls - H2_cy)**2)**0.5), r2, h2)

        if miss_bool or hole_bool:
            shot_bool = False

        total_holes = hole1_count + hole2_count
        sum_points = sum(p_pts[0])

# assign points and record stats etc for players
        for player in range(num_players):
            if p_ind == player + 1 and len(object_shot) > 0:
                if hole_bool:
                    streak_count_a[player].append(1)
                    H_count_a[player].append(1)
                if small_hole_bool:
                    H1_count_a[player].append(1)
                    p_pts[p_ind - 1].append(s_pts)
                    for team in range(team_no):
                        if p_ind in teams[team]:
                            t_pts[team].append(s_pts)
                elif big_hole_bool:
                    H2_count_a[player].append(1)
                    p_pts[p_ind - 1].append(b_pts)
                    for team in range(team_no):
                        if p_ind in teams[team]:
                            t_pts[team].append(b_pts)
                elif miss_bool:
                    missed_count_a[player].append(1)
                    streak_count_a[player].clear()
                    p_pts[player].append(0)
                    for team in range(team_no):
                        if p_ind in teams[team]:
                            t_pts[team].append(0)
                missed_temp = int(sum(missed_count_a[player]))
                holes_temp = int(sum(H_count_a[player]))
                if miss_bool or hole_bool:
                    shtpct = round(holes_temp * 100 / (missed_temp + holes_temp))
                    shot_pcnt_a[player].append(shtpct)
                    shot_count_a[p_ind - 1].append(1)
                    sum_p_pts[player].append(sum(p_pts[player]))
                    if sum(p_pts[player]) > 0:
                        sum_shots_temp = sum(shot_count_a[player])
                        pps_temp = round(sum_p_pts[player][-1] / sum_shots_temp, 2)
                        pps_a[player].append(pps_temp)
            # record maximum streak for each player
                max_str_temp = sum(streak_count_a[player])
                if max_str_temp > max_streak_a[player][0]:
                    max_streak_a[player][0] = max_str_temp

        # if game_mode == "F":
        #     game_stats = game_calculator.game_calc(teams, shot_record, game_mode)
        #     shots_taken = game_stats[0]
        #     small_holes = game_stats[1]
        #     big_holes = game_stats[2]
        #     total_holes = game_stats[3]
        #     l_align = 2 * hb
        #     startytext = 40
        #     text_pos = (l_align, startytext)
        #     cv2.putText(drawing, str(hole1_count + hole2_count), (l_align + 15, round(p_name_y - 35)), cv2.FONT_HERSHEY_DUPLEX, 1.4, font_col, 3)
        #     cv2.putText(drawing, "/" + str(shot_count), (round(l_align + hb/2 - 10), p_name_y - 5), cv2.FONT_HERSHEY_DUPLEX, 0.8, font_col, 3)
        #     #if shot_count > 0:
        #     if shot_pcnt < 100:
        #         cv2.putText(drawing, str(shot_pcnt) + "%", (round(l_align + hb + 10), round(p_name_y - 20)), cv2.FONT_HERSHEY_DUPLEX, 1.2, font_col, 3)
        #     else:
        #         cv2.putText(drawing, str(shot_pcnt) + "%", (round(l_align + hb + 5), round(p_name_y - 20)), cv2.FONT_HERSHEY_DUPLEX, 1.0, font_col, 2)
        #     cv2.putText(drawing, str(sum_points), (l_align + 15 + 3 * hb, round(p_name_y - 40)), cv2.FONT_HERSHEY_DUPLEX, 1, font_col, 3)
        #     cv2.putText(drawing, "PTS", (l_align + 10 + 3 * hb, round(p_name_y)), cv2.FONT_HERSHEY_DUPLEX, 1, font_col, 3)
        #     cv2.putText(drawing, "PTS/SHOT: " + str(pps), (round(l_align + 3 * hb/2 - 10), round(hd + hb /3 + 10)), cv2.FONT_HERSHEY_DUPLEX, 1, font_col, 3)
        #     h1circ = cv2.circle(drawing, (round(l_align + 25 + 3 * hb - hb), round(p_name_y - 10)), 4, (0, 0, 0), 8)
        #     h2circ = cv2.circle(drawing, (round(l_align + 70 + 3 * hb - hb), round(p_name_y - 10)), 6, (0, 0, 0), 12)
        #     # else:
        #     #     cv2.putText(drawing, str("0 %"), (l_align, 155), cv2.FONT_HERSHEY_DUPLEX, 1, font_colour, 2)
        #     #     cv2.putText(drawing, str("Points: 0" + str(sum(p_pts[0]))), (l_align, 170), cv2.FONT_HERSHEY_DUPLEX, 1, font_colour, 2)
        #     if hole1_count or hole2_count < 10:
        #         cv2.putText(drawing, str("x" + str(hole1_count) + " x" + str(hole2_count)), (round(l_align + 5 + 2 * hb), round(p_name_y - 40)), cv2.FONT_HERSHEY_DUPLEX, 0.8, font_col, 3)
        #     else:
        #         cv2.putText(drawing, str("x" + str(hole1_count) + " x" + str(hole2_count)), (round(l_align + 5 + 2 * hb), round(p_name_y - 40)), cv2.FONT_HERSHEY_DUPLEX, 0.6, font_col, 3)
        #     if streak_count > 1:
        #         cv2.putText(drawing, str("STREAK x" + str(streak_count)), (t_al_x - 25, round(hd + hb /3 + 10)), cv2.FONT_HERSHEY_DUPLEX, 1, (50, 50, 255), 3)
        #         # calculate Streak highscore
        #     if streak_count > streak_highscores[0][1]:
        #         streak_highscores[0][1] = streak_count
        #         streak_broke1 = True
        #     elif streak_count > streak_highscores[1][1]:
        #         streak_highscores[1][1] = streak_count
        #         streak_broke2 = True
        #     elif streak_count > streak_highscores[2][1]:
        #         streak_highscores[2][1] = streak_count
        #         streak_broke3 = True

        for i in range(num_players):
            score_xpos = round(stat_indent + p_dist / 3 + i * p_dist)
            cv2.putText(drawing, str(sum(p_pts[i])), (score_xpos, staty[0]), cv2.FONT_HERSHEY_DUPLEX, scorecard_fs, font_col, 3)
            cv2.putText(drawing, str(sum(H_count_a[i])), (score_xpos - 20, staty[1]), cv2.FONT_HERSHEY_DUPLEX, scorecard_fs, font_col, 3)
            cv2.putText(drawing, "/" + str(sum(shot_count_a[i])), (score_xpos + 40, staty[1] + 30), cv2.FONT_HERSHEY_DUPLEX, scorecard_fs - 0.5, font_col, 2)
            cv2.putText(drawing, str(shot_pcnt_a[i][-1]), (score_xpos, staty[2]), cv2.FONT_HERSHEY_DUPLEX, scorecard_fs, font_col, 3)
            cv2.putText(drawing, str(pps_a[i][-1]), (score_xpos, staty[3]), cv2.FONT_HERSHEY_DUPLEX, scorecard_fs, font_col, 3)
            cv2.putText(drawing, str(max_streak_a[i][0]), (score_xpos, staty[4]), cv2.FONT_HERSHEY_DUPLEX, scorecard_fs, font_col, 3)
            if num_players < 4:
                xholsens = 60
                yholsens = 30
                h1circ = cv2.circle(drawing, (round(score_xpos + p_dist / 3), staty[1] - yholsens), 4, (0, 0, 0), 8)
                h2circ = cv2.circle(drawing, (round(score_xpos + p_dist / 3) + xholsens, staty[1] - yholsens), 6, (0, 0, 0), 12)
                cv2.putText(drawing, "x" + str(sum(H1_count_a[i])), (round(score_xpos + p_dist / 3.5), staty[1] + yholsens), cv2.FONT_HERSHEY_DUPLEX, scorecard_fs - 0.5, font_col, 3)
                cv2.putText(drawing, "x" + str(sum(H2_count_a[i])), (round(score_xpos + p_dist / 3.5) + xholsens + 20, staty[1] + yholsens), cv2.FONT_HERSHEY_DUPLEX, scorecard_fs - 0.5, font_col, 3)
            if sum(streak_count_a[i]) > 1:
                cv2.putText(drawing, "x" + str(sum(streak_count_a[i])), (round(score_xpos - p_dist / 6), nameyst + 40), cv2.FONT_HERSHEY_DUPLEX, scorecard_fs - 0.25, (50, 100, 255), 5)

        if game_mode == "P":
            if num_players > 1:
                cv2.putText(drawing, team_string, (500, 40), cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 0, 0), 3)
                #cv2.putText(drawing, "PLAYER " + str(p_ind) + "'s turn", (round(wd / 3), round(4 * hb / 3)), cv2.FONT_HERSHEY_COMPLEX, scorecard_fs, (0, 0, 0), 3)
            cv2.putText(drawing, ">", (300 + (p_ind - 1) * p_dist, 140), cv2.FONT_HERSHEY_COMPLEX, 2, (50, 50, 255), 15)
            cv2.putText(drawing, "ROUND " + str(cur_rnd) + "/" + str(rounds), (925, 25), cv2.FONT_HERSHEY_COMPLEX, 1, font_col, 3)
            cv2.putText(drawing, "SHOTS TAKEN  " + str(p_shots) + "/" + str(shotspround), ((925, 55)), cv2.FONT_HERSHEY_COMPLEX, 1, font_col, 3)
            for team in range(team_no):
                if team_bool:
                    t_scores[team] = sum(t_pts[team])
                    first_mem = teams[team][0]
                    last_mem = teams[team][-1]
                    len_team = len(teams[team])
                    tsc_xpos = round(stat_indent + last_mem * p_dist - len_team * p_dist / 2 )
                    cv2.putText(drawing, "TEAM PTS", (statxsen, hd - 30), cv2.FONT_HERSHEY_DUPLEX, 1.5, font_col, 4)
                    cv2.putText(drawing, str(t_scores[team]), (round(tsc_xpos - p_dist / 3), hd - 30), cv2.FONT_HERSHEY_DUPLEX, 2, font_col, 2)
                    teamboxsensx = round(p_dist / 4)
                    teamboxsensy = 30
                    w = round(len_team * p_dist - teamboxsensx)
                    h = round(hd - sc_end - teamboxsensy)
                    x = round(stat_indent + ((first_mem - 1) * p_dist) + teamboxsensx / 2)
                    y = round(sc_end + teamboxsensy / 2)
                    cv2.rectangle(drawing, (x, y), (x + w, y + h), (0, 0, 255), 3)

            # if game finished we want to find winner
            if hole1_count + hole2_count + missed_count == num_players * shotspround * rounds:
                drawing = np.zeros((round(hd + hb / 2), wd, 3), dtype=np.uint8)
                drawing.fill(255)
                f_size_win = 2.5
                if not team_bool:
                    winning_pts = sum(p_pts[0])
                    winning_p = 1
                    for i in range(len(p_pts)):
                        if sum(p_pts[i]) > winning_pts:
                            winning_pts = sum(p_pts[i])
                            winning_p = i + 1
                        elif sum(p_pts[i]) > winning_pts:
                            winning_pts = 0
                            winning_p = 0
                    if winning_p > 0:
                        cv2.putText(drawing, "PLAYER " + str(winning_p) + " WINS", (round(wd / 3), round(hd / 2)), cv2.FONT_HERSHEY_COMPLEX, f_size_win, font_col, 5)
                    else:
                        cv2.putText(drawing, "DRAW", (round(wd /2), round(hd / 2)), cv2.FONT_HERSHEY_COMPLEX, f_size_win, font_col, 5)
                    cv2.imshow("Scoreboard", drawing)

                elif team_bool:
                    winning_pts = sum(t_pts[0])
                    winning_p = 1
                    for i in range(len(t_pts)):
                        if sum(t_pts[i]) > winning_pts:
                            winning_pts = sum(p_pts[i])
                            winning_p = i + 1
                        elif sum(p_pts[i]) > winning_pts:
                            winning_pts = 0
                            winning_p = 0
                    drawing = np.zeros((round(hd + hb /2), wd, 3), dtype=np.uint8)
                    drawing.fill(255)
                    if winning_p > 0:
                        cv2.putText(drawing, "Team " + str(winning_p) + " wins", (round(wd / 6), round(hd / 2)), cv2.FONT_HERSHEY_COMPLEX, f_size_win, font_col, 5)

                    else:
                        cv2.putText(drawing, "DRAW", (round(wd / 4), round(hd / 2)), cv2.FONT_HERSHEY_COMPLEX, f_size_win, font_col, 5)
                    cv2.imshow("Scoreboard", drawing)

                print("\nPlayer " + str(i + 1) + "\nTotal Shots: " + str(sum(shot_count_a[i])))
                print("Total Holes: " + str(sum(H_count_a[i])) + " (" + str(shot_pcnt_a[i][-1])  + " %)")
                print("Points: " + str(sum(sum_p_pts[i])) + " (" + str(pps_a[i][-1]) + " pts/shot)")
                print("Small Holes: " + str(sum(H1_count_a[i])) + "\nBig Holes: " + str(sum(H2_count_a[i])))
                print("Max. Streak: " + str(sum(max_streak_a[i])))
                stats_list_a[i].append(i + 1)
                stats_list_a[i].append(sum(shot_count_a[i]))
                stats_list_a[i].append(sum(H_count_a[i]))
                stats_list_a[i].append(shot_pcnt_a[i][-1])
                stats_list_a[i].append(sum(sum_p_pts[i]))
                stats_list_a[i].append(pps_a[i][-1])
                stats_list_a[i].append(sum(H1_count_a[i]))
                stats_list_a[i].append(sum(H2_count_a[i]))

                k1 = cv2.waitKey(0)
                if k1 == 13:         # wait for ENTER key to proceed
                    #cap.release()
                    cv2.destroyAllWindows()
                start_game(cap)


        # loop to determine next player if all shots for round have been taken and find indicator for player/team turn
        if miss_bool or hole_bool:
            if p_shots == shotspround:
                #print(p_shots, shotspround)
                p_rnd_comp[p_ind - 1] = int(p_rnd_comp[p_ind - 1]) + 1
                # t_ind += 1
                # if t_ind > team_no:
                #     t_ind = 1
                p_shots = 0
                if (missed_count + hole1_count + hole2_count) % (num_players * shotspround) == 0:
                    cur_rnd = int(shot_count / (num_players * shotspround)) + 1
                t_ind += 1
                if t_ind > team_no:
                    t_ind = 1
                while True:
                    p_ind += 1
                    if p_ind > num_players:
                        p_ind = 1
                    if p_ind not in teams[t_ind - 1]:
                        continue
                    else:
                        posit = teams[t_ind - 1].index(p_ind)
                    if posit > 0 and shot_count_a[p_ind - 1] < shot_count_a[p_ind - 2]:
                        break
                    elif posit == 0 and shot_count_a[p_ind - 1] == shot_count_a[teams[t_ind -1][-1] - 1]:
                        break


        cv2.imshow("Scoreboard", drawing)

        miss_bool = False
        miss_left = False
        miss_right = False
        miss_end = False
        small_hole_bool = False
        big_hole_bool = False
        hole_bool = False
        sz1bool = False
        sz2bool = False
        sz3bool = False
        if total_holes > 0:
            shot_pcnt = int(round(100 * (total_holes) / (total_holes + missed_count)))
            pps = round(sum_points / (total_holes + missed_count), 2)
        if streak_count > max_streak_count:
            max_streak_count = streak_count
        round_stats = [total_holes, shot_pcnt, sum(p_pts[0]), pps, hole1_count, hole2_count]

        cv2.imshow("frame for main", frame)
        #cv2.imshow("mask2", mask2)
        #cv2.imshow("ROI", roi)

        key = cv2.waitKey(30)
        # while key == ord("s"):
        #     end_line = cv2.line(frame, (minx, maxy), node4, line_colour, line_thickness)
        #     sz1_line = cv2.line(frame, node1, node2, line_colour, line_thickness)
        #     sz2_line = cv2.line(frame, node5, node6, line_colour, line_thickness)
        #     sz3_line = cv2.line(frame, sz3n1, sz3n2, line_colour, line_thickness)
        #     left_line = cv2.line(frame, node1, node3, line_colour, line_thickness)
        #     right_line = cv2.line(frame, node2, node4, line_colour, line_thickness)
        #     #hole1 = cv2.circle(frame, (H1_cx, H1_cy), r1, line_colour, 3)
        #     #hole2 = cv2.circle(frame, (H2_cx, H2_cy), r2, line_colour, 3)
        #     hole1_ell = cv2.ellipse(frame, centreH1, H1_ax_l, angle, startAngle, endAngle, line_colour, line_thickness)
        #     hole2_ell = cv2.ellipse(frame, centreH2, H2_ax_l, angle, startAngle, endAngle, line_colour, line_thickness)
        #     cv2.imshow("frame for main", frame)
        if key == 27:
            # save_opt = input("Save out stats? \n[Y]\n[N]\n> ")
            # if save_opt == "Y" or save_opt == "y":
            #     csv_name = input("Enter file name: \n> ")
            #     csv_rowlist = [round_stats]
            #     with open(csv_name + '.csv', 'w') as file:
            #         writer = csv.writer(file)
            #         writer.writerows(csv_rowlist)
            #print(shot_pcnt_a)
            #print(sum_p_pts)
            for i in range(num_players):
                print("\nPlayer " + str(i + 1) + "\nTotal Shots: " + str(sum(shot_count_a[i])))
                print("Total Holes: " + str(sum(H_count_a[i])) + " (" + str(shot_pcnt_a[i][-1])  + " %)")
                print("Points: " + str(sum(sum_p_pts[i])) + " (" + str(pps_a[i][-1]) + " pts/shot)")
                print("Small Holes: " + str(sum(H1_count_a[i])) + "\nBig Holes: " + str(sum(H2_count_a[i])))
                print("Max. Streak: " + str(sum(max_streak_a[i])))
                stats_list_a[i].append(i + 1)
                stats_list_a[i].append(sum(shot_count_a[i]))
                stats_list_a[i].append(sum(H_count_a[i]))
                stats_list_a[i].append(shot_pcnt_a[i][-1])
                stats_list_a[i].append(sum(sum_p_pts[i]))
                stats_list_a[i].append(pps_a[i][-1])
                stats_list_a[i].append(sum(H1_count_a[i]))
                stats_list_a[i].append(sum(H2_count_a[i]))
                stats_list_a[i].append(sum(max_streak_a[i]))
            break
        elif key == ord("c"):
            matvals = detect_mat(cap)
            # matvals = [minx, maxx, miny, maxy, minxmin, maxxmin, n3ay, H1_cx, H1_cy, H1_ax_l, r1, h1, H2_cx, H2_cy, H2_ax_l, r2, h2]
            minx = matvals[0]
            maxx = matvals[1]
            miny = matvals[2]
            maxy = matvals[3]
            minxmin = matvals[4]
            maxxmin = matvals[5]
            n3ay = matvals[6]
            H1_cx = matvals[7]
            H1_cy = matvals[8]
            H1_ax_l = matvals[9]
            r1 = matvals[10]
            h1 = matvals[11]
            H2_cx = matvals[12]
            H2_cy = matvals[13]
            H2_ax_l = matvals[14]
            r2 = matvals[15]
            h2 = matvals[16]

            # defining left/right/up/down points on holes
            H1_xl = H1_cx - r1
            H1_xr = H1_cx + r1
            H1_yu = H1_cy - h1
            H1_yd = H1_cy + h1
            H2_xl = H2_cx - r1
            H2_xr = H2_cx + r1
            H2_yu = H2_cy - h2
            H2_yd = H2_cy + h2

            #hw_ratio = round(hmax_mat / wmax_mat, 1)
            # gaps between shot zones
            szy_adj = 150
            szy_inter = 50
            #nodes coordinates
            n1x = minxmin
            n1y = miny
            n2x = maxxmin
            n2y = n1y
            n3x = minx
            n3y = n3ay
            n4x = maxx
            n4y = maxy
            n5x = minx
            n5y = n1y + szy_adj
            n6x = maxx
            n6y = n5y
            n7x = n5y
            n7y = n5y
            n8x = n5y
            n8y = n5y

            node1 = (n1x, n1y)
            node2 = (n2x, n2y)
            node3 = (n3x, n3y)
            node4 = (n4x, n4y)
            node5 = (n5x, n5y)
            node6 = (n6x, n6y)

            roi1 = (n3x, n1y)
            roi2 = (n4x, n1y)
            roi3 = (n3x, n3y)
            roi4 = (n4x, n3y)

            # defining nodes for shot zones
            sz1n1 = node1
            sz1n2 = node2
            sz2n1 = node5
            sz2n2 = node6
            sz3n1y = n5y + szy_inter
            sz3n1 = (n5x, sz3n1y)
            sz3n2 = (n6x, sz3n1y)

            # define ellipses parameters for holes
            centreH1 = (H1_cx, H1_cy)
            centreH2 = (H2_cx, H2_cy)

        count += 1

    cap.release()
    cv2.destroyAllWindows()

start_game(cap)


