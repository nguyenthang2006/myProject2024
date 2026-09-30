import cv2
import numpy as np
from keras.models import load_model
import mediapipe as mp
from keras.preprocessing import sequence
from sklearn.preprocessing import LabelEncoder
import time
import threading
from pynput.keyboard import Key, Controller
class HandGestureRecognition:
    def __init__(self):
        try:
            self.model = load_model("D:/Downloads/khktqg/GestureLibrary/hand_lib/HandSrc/handmodel.h5")
            self.le = LabelEncoder()
            self.le.classes_ = np.load("D:/Downloads/khktqg/GestureLibrary/hand_lib/HandSrc/label_encoder_classes.npy", allow_pickle=True)

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

        # Move the following line out of __init__ method
        mpHands = mp.solutions.hands
        self.mpHands = mpHands.Hands()
        self.mpDraw = mp.solutions.drawing_utils
        self.frames_for_prediction = []

    def _make_landmark_timestep(self, results):
        try:
            c_lm = []
            for hand_landmarks in results.multi_hand_landmarks:
                for id, lm in enumerate(hand_landmarks.landmark):
                    c_lm.append(lm.x)
                    c_lm.append(lm.y)
                    c_lm.append(lm.z)
                    c_lm.append(lm.visibility)
            return c_lm
        except Exception as e:
            print(f"Error during making landmark timestep: {e}")
            return []

    def _draw_landmark_on_image(self, results, img):
        try:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)  # Fix: Use mp.solutions.hands.HAND_CONNECTIONS
                for id, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (cx, cy), 10, (0, 0, 255), cv2.FILLED)
            return img
        except Exception as e:
            print(f"Error during drawing hand landmarks: {e}")
            return img

    def perform_prediction(self, predicted_value):
        label_to_display = ""
        try:
            if predicted_value == 0 or predicted_value == 1:
                label_to_display = "MOBANTAY"
                print(label_to_display)
            elif predicted_value == 2 or predicted_value == 3:
                label_to_display = "CHUMTAY"
                self.keyboard.press(Key.space)
                self.keyboard.release(Key.space)
                print(label_to_display)
            elif predicted_value == 4 or predicted_value == 5:
                label_to_display = "NAMDAM"
                self.keyboard.press(Key.space)
                self.keyboard.release(Key.space)
                print(label_to_display)
            elif predicted_value == 6 or predicted_value == 7:
                label_to_display = "GAPNGONTAY"
                self.keyboard.press(Key.space)
                self.keyboard.release(Key.space)        
                print(label_to_display)
            
            # Print prediction result to console
            print(f"Prediction: {label_to_display}")
            return label_to_display
        except Exception as e:
            print(f"Error during performing prediction: {e}")
            return ""

    def predict_thread(self):
        try:
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
        except Exception as e:
            print(f"Error in prediction thread: {e}")

    def process_frame(self, frame):
        try:
            frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.mpHands.process(frameRGB)  # Fix: Change self.hands to self.mpHands

            if results.multi_hand_landmarks:
                lm = self._make_landmark_timestep(results)
                self.frames_for_prediction.append(lm)

                try:
                    frame = self._draw_landmark_on_image(results, frame)
                except Exception as e:
                    print(f"Error during drawing hand landmarks: {e}")

            return frame
        except Exception as e:
            print(f"Error during processing frame: {e}")
            return frame

    def hand_start_webcam(self):
        try:
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
        except Exception as e:
            print(f"Error during starting webcam: {e}")
