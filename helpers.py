name_helper = """
MDTextField:
    hint_text: "Enter your Name"
    helper_text: "Only english letters and numbers are allowed"
    helper_text_mode: "on_focus"
    icon_right: "account"
    icon_right_color: app.theme_cls.primary_color
    pos_hint:{'center_x':0.5,'center_y':0.6}
    size_hint_x: None
    width: 250
"""

Password_helper = """
MDTextField:
    hint_text: "Enter Your Password"
    helper_text: "Case Sensitive"
    helper_text_mode: "on_focus"
    icon_right: "numeric"
    icon_right_color: app.theme_cls.primary_color
    pos_hint:{'center_x':0.5,'center_y':0.5}
    size_hint_x: None
    password: True
    width: 250

"""

ID_helper = """
MDTextField:
    hint_text: "Enter Your ID"
    helper_text: "Only numbers are allowed"
    helper_text_mode: "on_focus"
    icon_right: "school-outline"
    icon_right_color: app.theme_cls.primary_color
    pos_hint:{'center_x':0.5,'center_y':0.4}
    size_hint_x: None
    width: 250

"""

label = """
MdLabel:
    text:'After Registration\n App will Shut Down!'
    size: self.texture_size
    halign:'center'
    
"""

"""
from kivymd.app import MDApp
from kivy.uix.widget import Widget
import kivy
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.screen import Screen
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton, MDIconButton, MDFloatingActionButton
from kivymd.uix.textfield import MDTextField
from kivy.uix.image import Image, AsyncImage
from kivy.lang import Builder
from helpers import *
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem, MDList
import numpy as np
import cv2
import os
import mysql.connector
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import ScreenManager
from PIL import Image as pilimg
from kivy.core.window import Window
Window.size = (350,633)
class IKUFaceRecognationApp(MDApp):

    def build(self):

        self.theme_cls.primary_palette = "Red"
        self.theme_cls.theme_style = "Dark"
        screen = Screen()

        self.logoimg = Image(source='logo.png', pos_hint={'center_x': 0.5, 'center_y': 0.8})
        self.logoimg.size_hint_x = 0.3
        self.logoimg.size_hint_y = 0.3

        self.logoimg.opacity = 0.2
        screen.add_widget(self.logoimg)
        self.capture = cv2.VideoCapture(1)

        button1 = MDRectangleFlatButton(text='Register',
                                        pos_hint={'center_x': 0.5, 'center_y': 0.3},
                                        on_release=self.dataset_generation
                                        )

        button2 = MDRectangleFlatButton(text='Train',
                                        pos_hint={'center_x': 0.5, 'center_y': 0.2},

                                        on_release=self.train_classifier)

        self.Age = Builder.load_string(age_helper)
        self.Name = Builder.load_string(name_helper)
        self.ID = Builder.load_string(ID_helper)

        screen.add_widget(button1)
        screen.add_widget(button2)
        # screen.add_widget(label)
        screen.add_widget(self.logoimg)
        screen.add_widget(self.Name)
        screen.add_widget(self.Age)
        screen.add_widget(self.ID)

        return screen

    def close_dialog2(self, obj):
        self.dialog2.dismiss()

    def close_dialog(self, obj):
        self.dialog.dismiss()

    def dataset_generation(self, obj):
        close_btn = MDFlatButton(text='Close', on_release=self.close_dialog)
        close_btn2 = MDFlatButton(text='Close', on_release=self.close_dialog2)
        if self.Name.text is "" or self.ID.text is "" or self.Age.text is "":
            self.dialog2 = MDDialog(title='Please fill the boxes',

                                    radius=[20, 20, 20, 20],
                                    size_hint=(0.7, 1),
                                    buttons=[close_btn2])
            self.dialog2.open()

        else:
            db = mysql.connector.connect(
                host="localhost",
                user="root",
                passwd="Wasd0hqvz*",
                database="authorized_user"
            )
            cursor = db.cursor()
            cursor.execute("SELECT * FROM my_table")
            result = cursor.fetchall()
            id = 1
            for x in result:
                id += 1
            sql = "INSERT INTO my_table(id,name,Age,StudentNo) values(%s,%s,%s,%s)"
            val = (id, self.Name.text, int(self.Age.text), self.ID.text)

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
                    cv2.putText(face, str(img_id), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.imshow("Cropped face", face)

                    if cv2.waitKey(1) == 13 or int(img_id) == 200:
                        break

            self.dialog = MDDialog(title='Registration Complete!',

                                   radius=[20, 20, 20, 20],
                                   size_hint=(0.7, 1),
                                   buttons=[close_btn])
            self.dialog.open()
            self.capture.release()

    def train_classifier(self, obj):
        close_btn = MDFlatButton(text='Close', on_release=self.close_dialog)
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
        self.dialog = MDDialog(title='Training Is Done!',

                               radius=[20, 20, 20, 20],
                               size_hint=(0.7, 1),
                               buttons=[close_btn])
        self.dialog.open()


IKUFaceRecognationApp().run()
"""