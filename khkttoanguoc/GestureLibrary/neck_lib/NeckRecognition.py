import cv2
import numpy as np
from keras.models import load_model
import mediapipe as mp
from keras.preprocessing import sequence
from sklearn.preprocessing import LabelEncoder
import time
import threading
import os
from pynput.keyboard import Key, Controller

class NeckGestureController:
    def __init__(self):
        try:
            self.model = load_model("D:/Downloads/khktqg/GestureLibrary/neck_lib/NeckSrc/model.h5")
            self.le = LabelEncoder()
            self.le.classes_ = np.load("D:/Downloads/khktqg/GestureLibrary/neck_lib/NeckSrc/label_encoder_classes.npy", allow_pickle=True)

            self.no_of_timesteps = 10
            self.frames_for_prediction = []
            self.prediction_thread_running = True
            self.last_prediction_time = time.time()
            self.all_predictions = []

            self.keyboard = Controller()

            # Initialize and start prediction thread
            self.prediction_thread = threading.Thread(target=self.predict_thread)
            self.prediction_thread.start()
        except Exception as e:
            print(f"Error during initialization: {e}")

        # Move the following lines out of __init__ method
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose()
        self.mpDraw = mp.solutions.drawing_utils


    # Các phương thức khác ở đây...


    def make_landmark_timestep(self, results):
        c_lm = []
        for id, lm in enumerate(results.pose_landmarks.landmark):
            c_lm.append(lm.x)
            c_lm.append(lm.y)
            c_lm.append(lm.z)
            c_lm.append(lm.visibility)
        return c_lm

    def draw_landmark_on_image(self, results, img):
        self.mpDraw.draw_landmarks(img, results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)

        for id, lm in enumerate(results.pose_landmarks.landmark):
            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(img, (cx, cy), 10, (0, 0, 255), cv2.FILLED)
        return img

    def perform_prediction(self, predicted_value):
        label_to_display = ""
        if predicted_value == 0:
            label_to_display = "THANGMAT"
        elif predicted_value == 1:
            label_to_display = "CUIDAU"
            self.keyboard.press(Key.space)
            self.keyboard.release(Key.space)
        elif predicted_value == 2:
            label_to_display = "NGANGMAT"
            self.keyboard.press(Key.space)
            self.keyboard.release(Key.space)
            print(label_to_display)
        elif predicted_value == 3:
            label_to_display = "QUAYMATPHAI"
            self.keyboard.press(Key.right)
            self.keyboard.release(Key.right)        
            print(label_to_display)
        elif predicted_value == 4:
            label_to_display = "QUAYMATTRAI"
            self.keyboard.press(Key.left)
            self.keyboard.release(Key.left)
            print(label_to_display)
        elif predicted_value == 5:
            label_to_display = "GIUDAUPHAI"
            self.keyboard.press(Key.right)
            self.keyboard.release(Key.right)
            print(label_to_display)
        elif predicted_value == 6:
            label_to_display = "GIUDAUTRAI"
            self.keyboard.press(Key.left)
            self.keyboard.release(Key.left)
            print(label_to_display)
        # Add other prediction cases here

        # Print prediction result to console
        print(f"Prediction: {label_to_display}")
        return label_to_display

    def predict_thread(self):
        while self.prediction_thread_running:
            if len(self.frames_for_prediction) >= self.no_of_timesteps:
                try:
                    self.frames_for_prediction = self.frames_for_prediction[-self.no_of_timesteps:]

                    prediction = self.model.predict(np.array([self.frames_for_prediction]))
                    predicted_class = self.le.inverse_transform([np.argmax(prediction)])[0]
                    predicted_value = self.le.transform([predicted_class])[0]

                    self.all_predictions.append(predicted_class)

                    self.last_prediction_time = time.time()

                    label_to_display = self.perform_prediction(predicted_value)

                    # Display prediction result on the frame
                    # (Note: You may need to pass the 'frame' variable as an argument to this method)
                    # cv2.putText(frame, f"Prediction: {label_to_display}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                except Exception as e:
                    print(f"Error during prediction: {e}")

                self.frames_for_prediction = []

            time.sleep(0.05)

    def process_frame(self, frame):
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frameRGB)

        if results.pose_landmarks:
            lm = self.make_landmark_timestep(results)
            self.frames_for_prediction.append(lm)

            try:
                frame = self.draw_landmark_on_image(results, frame)
            except Exception as e:
                print(f"Error during drawing pose landmarks: {e}")

        return frame

    def neck_start_webcam(self):
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if ret:
                try:
                    frame = self.process_frame(frame)
                    cv2.imshow("Webcam", frame)
                except Exception as e:
                    print(f"Error during displaying frame: {e}")

                if cv2.waitKey(1) == ord('q'):
                    break

        self.prediction_thread_running = False
        self.prediction_thread.join()

        cap.release()
        cv2.destroyAllWindows()

