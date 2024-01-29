import cv2
import numpy as np
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
import time

class ImageProcessing(BoxLayout):
    def __init__(self, **kwargs):
        super(ImageProcessing, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.processed_image_widget = KivyImage(source='', size_hint=(1, None))
        self.add_widget(self.processed_image_widget)

    def process_image(self, selected_file):
        self.clear_widgets()

        image = self.imageRead(selected_file)

        start_time = time.time()
        self.applyFilters(image)
        end_time = time.time()

        print(f"{end_time - start_time}")

    def imageRead(self, selected_file):
        try:
            image = cv2.imread(selected_file)
        except Exception as e:
            print(f"Erro ao ler imagem: {e}")

        image = cv2.flip(image, 0)
        self.add_image_widget(image, "Imagem Original")
        return image

    def applyFilters(self, image):
        interestArea = self.getInterestArea(image)
        self.add_image_widget(interestArea, "Seleção de área de interesse")

        interestObjects = self.removeBackgroud(interestArea)
        self.add_image_widget(interestObjects, "Imagem sem fundo")

        gausssianBlur = cv2.GaussianBlur(interestObjects, (5, 5), 3)
        self.add_image_widget(gausssianBlur, "Imagem utilizando o borramento Gaussiano")

        floorObjects = self.getInterestAreaPredetermined(gausssianBlur)
        self.add_image_widget(floorObjects, "Area selecionada para analise de pneus em contato com o chão")

        self.getObjectsFound(floorObjects)

        originalFloor = self.getInterestAreaPredetermined(interestArea, init=0, end=1)
        self.add_image_widget(originalFloor, "Imagem inicial com linha de contato sobre o solo")

    def getObjectsFound(self, image):
        enphatizatedObjects = self.emphasize_large_objects(image, 40)
        foundObj, totalObj, objs = self.contorns(enphatizatedObjects, 90)

        if (totalObj == 1):
            enphatizatedObjects = self.emphasize_large_objects(image, 20)
            foundObj, totalObj, objs = self.contorns(enphatizatedObjects, 20)

        self.add_image_widget(enphatizatedObjects, "Imagem enfatizada")
        self.add_image_widget(objs, f"Imagem contornada: Objetos encontrados: {foundObj}")

    def emphasize_large_objects(self, image, thresh):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        masks = [np.zeros_like(gray) for _ in contours]

        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area > 5:
                cv2.drawContours(masks[i], [contour], -1, 255, thickness=cv2.FILLED)

        combined_mask = sum(masks)
        emphasized_image = cv2.bitwise_and(image, image, mask=combined_mask)
        return emphasized_image

    def contorns(self, image, thresh):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(gray_image, thresh, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_area = 13
        mask = np.zeros_like(gray_image)
        total = 0

        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= min_area:
                total = total + 1
                cv2.drawContours(mask, [contour], -1, 255, thickness=cv2.FILLED)

        result_image = cv2.bitwise_and(gray_image, gray_image, mask=mask)
        return total, len(contours), result_image

    def removeBackgroud(self, image):
        # Criação de uma máscara invertida (todas as cores diferentes de verde)
        mask = cv2.inRange(image, (0, 40, 0), (100, 255, 100))

        # Substituição das áreas filtradas na imagem original por branco
        result_image = image.copy()
        result_image[mask != 0] = [0, 0, 0]
        return result_image

    def getInterestAreaPredetermined(self, image, init=0, end=2):
        return image[init:end, :]

    def getInterestArea(self, image):
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        color_threshold = 50
        height, width = image.shape[:2]
        transition_point = height

        for y in range(height):
            # Check if the pixel color in HSV is above the color threshold
            if hsv_image[y, 0, 1] > color_threshold:  # Adjust index based on the desired channel (1 for saturation)
                transition_point = y
                break

        initTransitionPoint = transition_point + 1
        endTransitionPoint = initTransitionPoint * 2

        if (endTransitionPoint == initTransitionPoint):
            endTransitionPoint += endTransitionPoint

        result_image = self.getInterestAreaPredetermined(image, init=initTransitionPoint, end=endTransitionPoint)
        return result_image

    def add_image_widget(self, cv2_image, title):
        kivy_texture = self.convert_cv2_to_kivy_texture(cv2_image)
        kivy_image = KivyImage(texture=kivy_texture)
        self.add_widget(Label(text=title))
        container = BoxLayout(orientation='vertical')
        self.add_widget(kivy_image)

    def convert_cv2_to_kivy_texture(self, cv2_image):
        if len(cv2_image.shape) == 2:
            cv2_image_rgba = cv2.cvtColor(cv2_image, cv2.COLOR_GRAY2RGBA)
        else:
            cv2_image_rgba = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGBA)

        h, w, _ = cv2_image_rgba.shape
        kivy_texture = Texture.create(size=(w, h))
        kivy_texture.blit_buffer(cv2_image_rgba.tostring(), colorfmt='rgba', bufferfmt='ubyte')
        return kivy_texture
