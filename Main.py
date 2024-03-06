import pickle
import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import tkinter as tk
import time

def read_aloud(predicted_character):
    engine = pyttsx3.init()
    engine.say(predicted_character)
    engine.runAndWait()

def update_predicted_word(predicted_character):
    current_text = text_widget.get("1.0", tk.END).strip()  # Get current text
    text_widget.delete("1.0", tk.END)  # Clear existing text
    updated_text = current_text + " " + predicted_character + " "  # Append predicted character
    text_widget.insert(tk.END, updated_text)  # Update text widget

model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']

cap = cv2.VideoCapture(0)
new_character=''

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

labels_dict = { 0 : "Hii",
                1 : "Hello",
                2 : "Welcome",
                3 : "End",
                4 : "Me",
                5 : "I",
                6 : "You",
                7 : "You",
                8 : "Call Me",
                9 : "Like",
                10 : "Dislike",
                11 : "Okay/Nice",
                12 : "Please",
                13 : "Good Luck",
                14 : "I Love You"
               }


root = tk.Tk()
root.title("Predicted Word Display")
root.configure(bg="black")

text_widget = tk.Text(root,height = 10,width=50, bg="black", fg="white", font=("Arial", 14))
text_widget.pack()

while True:

    data_aux = []
    x_ = []
    y_ = []

    ret, frame = cap.read()

    H, W, _ = frame.shape

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(frame_rgb)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,  # image to draw
                hand_landmarks,  # model output
                mp_hands.HAND_CONNECTIONS,  # hand connections
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

        for hand_landmarks in results.multi_hand_landmarks:
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y

                x_.append(x)
                y_.append(y)

            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x - min(x_))
                data_aux.append(y - min(y_))

        x1 = int(min(x_) * W) - 10
        y1 = int(min(y_) * H) - 10

        x2 = int(max(x_) * W) - 10
        y2 = int(max(y_) * H) - 10

        prediction = model.predict([np.asarray(data_aux)])

        predicted_character = labels_dict.get(int(prediction[0]), "Unknown")

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
        cv2.putText(frame, predicted_character, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3,
                    cv2.LINE_AA)
        
        # Update the predicted word display only if it's different from the previous one
        if new_character != predicted_character:
            if predicted_character != "Unknown":
                update_predicted_word(predicted_character)
            new_character = predicted_character
            read_aloud(predicted_character)
        

    cv2.imshow('frame', frame)
    cv2.waitKey(1)

    root.update_idletasks()
    root.update()

cap.release()
cv2.destroyAllWindows()