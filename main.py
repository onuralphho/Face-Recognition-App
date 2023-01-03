
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton
from kivy.uix.image import Image
from kivy.lang import Builder
from helpers import *
from kivymd.uix.dialog import MDDialog
import numpy as np
import cv2
import mysql.connector
from kivy.graphics.texture import Texture
from PIL import Image as pilimg
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.clock import Clock
import os



Window.size = (400, 633)


class IKUFaceRecognitionApp(MDApp):

    def build(self):
        self.icon = "windowlogo.png"
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.theme_style = "Dark"
        layout = MDBoxLayout(orientation='vertical')
        self.image = Image()
        self.Password = Builder.load_string(Password_helper)
        self.Name = Builder.load_string(name_helper)
        self.ID = Builder.load_string(ID_helper)
        label1 = MDLabel(text='After Registration \nApp Will Reset It Self!', halign='center', font_style='Body2',
                         size_hint=(0.7, 0.3), pos_hint={"center_x": .5, "center_y": .1})
        button1 = MDRectangleFlatButton(text='Register',
                                        pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                        on_release=self.dataset_generation
                                        )


        self.logoimg = Image(source='logo.png', pos_hint={'center_x': 0.5, 'center_y': 0.1})
        self.logoimg.size_hint_x = 0.3
        self.logoimg.size_hint_y = 0.3

        self.logoimg.opacity = 0.2
        layout.add_widget(self.logoimg)
        layout.add_widget(self.Name)
        layout.add_widget(self.Password)
        layout.add_widget(self.ID)
        layout.add_widget(self.image)

        layout.add_widget(button1)


        self.capture = cv2.VideoCapture(0)
        self.faceCascade = cv2.CascadeClassifier("data/haarcascade_frontalface_default.xml")

        self.clf = cv2.face.LBPHFaceRecognizer_create()

        self.clf.read("classifier.xml")

        Clock.schedule_interval(self.load_video, 1.0 / 30.0)

        layout.add_widget(label1)

        return layout

    def load_video(self, *args):

        def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, clf):

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            features = classifier.detectMultiScale(gray, scaleFactor, minNeighbors)

            coords = []

            for (x, y, w, h) in features:

                id, pred = clf.predict(gray[y:y + h, x:x + w])
                confidence = int(100 * (1 - pred / 300))
                #print(confidence)
                if confidence < 78:
                    color = (0, 0, 255)

                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                db = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    passwd="Wasd0hqvz*",
                    database="authorized_user"

                )
                cursor = db.cursor()

                cursor.execute("SELECT name FROM ikuusers where StudentNo=" + str(id))
                nme = cursor.fetchone()
                if nme == None:
                    cv2.putText(img, "UNKNOWN", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 1, cv2.LINE_AA)

                else:
                    nme = '' + ''.join(nme)

                if confidence > 78:
                    cv2.putText(img, nme, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1, cv2.LINE_AA)
                    # print("Welcome "+ str(nme))
                    # Window.close()


                else:
                    cv2.putText(img, "UNKNOWN", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 1, cv2.LINE_AA)

                coords = [x, y, w, h]
            return coords

        def recognizer(img, clf, faceCascade):

            draw_boundary(img, faceCascade, 1.1, 10, (0, 255, 0), clf)
            return img



        ret, frame = self.capture.read()

        self.image_frame = recognizer(frame, self.clf, self.faceCascade)

        buffer = cv2.flip(frame, 0).tostring()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        self.image.texture = texture

    def close_dialog3(self, obj):
        self.dialog3.dismiss()

    def close_dialog2(self, obj):
        self.dialog2.dismiss()

    def close_dialog(self, obj):
        self.dialog.dismiss()

    def dataset_generation(self, obj):

        close_btn = MDFlatButton(text='Close', on_release=self.close_dialog)
        close_btn2 = MDFlatButton(text='Close', on_release=self.close_dialog2)
        close_btn3 = MDFlatButton(text='Close', on_release=self.close_dialog3)
        if self.Name.text is "" or self.ID.text is "" or self.Password.text is "":
            self.dialog2 = MDDialog(title='Please fill the boxes',

                                    radius=[20, 20, 20, 20],
                                    size_hint=(0.7, 0.2),
                                    buttons=[close_btn2])
            self.dialog2.open()

        else:
            self.dialog = MDDialog(title='Registration Complete!',

                                   radius=[20, 20, 20, 20],
                                   size_hint=(0.7, 0.2),
                                   buttons=[close_btn])
            self.dialog3 = MDDialog(title='Wait Until Registration Complete!',

                                    radius=[20, 20, 20, 20],
                                    size_hint=(0.7, 0.2),
                                    buttons=[close_btn3])
            self.dialog3.open()
            self.dialog.open()

            db = mysql.connector.connect(
                host="localhost",
                user="root",
                passwd="Wasd0hqvz*",
                database="authorized_user"
            )
            cursor = db.cursor()
            cursor.execute("SELECT * FROM ikuusers")
            result = cursor.fetchall()
            id = 1
            for x in result:
                id += 1
            sql = "INSERT INTO ikuusers(id,name,Password,StudentNo) values(%s,%s,%s,%s)"
            val = (id, self.Name.text, self.Password.text, self.ID.text)

            cursor.execute(sql, val)
            db.commit()
            face_classifier = cv2.CascadeClassifier("data/haarcascade_frontalface_default.xml")

            def face_cropped(img):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_classifier.detectMultiScale(gray, 1.3, 5)
                if faces is ():
                    return None
                for (x, y, w, h) in faces:
                    cropped_face = img[y:y + h, x:x + w]
                return cropped_face

            img_id = 0
            while True:
                ret, frame = self.capture.read()
                if face_cropped(frame) is not None:
                    img_id += 1
                    face = cv2.resize(face_cropped(frame), (250, 250))
                    face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                    file_name_path = "data_img/users." + self.ID.text + "." + str(img_id) + ".jpg"
                    cv2.imwrite(file_name_path, face)


                    if cv2.waitKey(1) == 13 or int(img_id) == 200:
                        break

            self.capture.release()


            data_dir = 'data_img'

            path = [os.path.join(data_dir, f) for f in os.listdir(data_dir)]
            faces = []
            ids = []

            for image in path:
                img = pilimg.open(image).convert('L')
                imageNp = np.array(img, 'uint8')
                id = int(os.path.split(image)[1].split(".")[1])

                faces.append(imageNp)
                ids.append(id)
            ids = np.array(ids)

            clf = cv2.face.LBPHFaceRecognizer_create()
            clf.train(faces, ids)
            clf.write("classifier.xml")
            MDApp.get_running_app().stop()
            Window.close()
            os.system("python main.py")




IKUFaceRecognitionApp().run()
