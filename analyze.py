import cv2
import mediapipe as mp

def hand(load_path):
    """
    param: 
        load_path: video load path
        save_path:result save path
    """
    # mp.solutions.drawing_utils用于绘制
    mp_drawing = mp.solutions.drawing_utils

    # 参数：1、颜色，2、线条粗细，3、点的半径
    DrawingSpec_point = mp_drawing.DrawingSpec((0, 255, 0), 1, 1)
    DrawingSpec_line = mp_drawing.DrawingSpec((0, 0, 255), 1, 1)

    # mp.solutions.hands，是人的手
    mp_hands = mp.solutions.hands

    # 参数：1、是否检测静态图片，2、手的数量，3、检测阈值，4、跟踪阈值
    hands_mode = mp_hands.Hands(max_num_hands=2)

    cap = cv2.VideoCapture(load_path)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    out = cv2.VideoWriter('out.mp4',fourcc, 20.0, (1280, 720))

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break
        
        image1 = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 处理RGB图像
        results = hands_mode.process(image1)

        # 绘制

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for id, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = image1.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    print(id, cx, cy)
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS, DrawingSpec_point, DrawingSpec_line)
        out.write(image)
        #cv2.imshow('MediaPipe Hands', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    hands_mode.close()
    cap.release()
    out.release()
