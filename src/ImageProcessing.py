# image_processing.py
import cv2
import numpy as np
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label


class ImageProcessing(BoxLayout):
    def __init__(self, **kwargs):
        super(ImageProcessing, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.processed_image_widget = KivyImage(source='', size_hint=(1, None))
        self.add_widget(self.processed_image_widget)

    def process_image(self, selected_file):
        self.clear_widgets()

        image = self.imageRead(selected_file)

        self.applyFilters(image)

        # Segment the wheels and color them differently based on floor contact
        # segmented_image = self.segment_wheels(image, edges)

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

        enfatizate = self.emphasize_large_objects(self.addBorder(floorObjects),40)
        self.add_image_widget(enfatizate, "Imagem enfatizada")

        foundObj, totalObj, objs = self.contornos(enfatizate, 90)
        self.add_image_widget(objs, f"Imagem contornada: TOTAL: {totalObj}; Encontrados: {foundObj}")

        originalFloor = self.getInterestAreaPredetermined(interestArea,init=0, end=1)
        self.add_image_widget(originalFloor, "Imagem inicial com linha de contato sobre o solo")

        if (totalObj == 1):
            enfatizate2 = self.emphasize_large_objects(self.addBorder(floorObjects), 20)
            self.add_image_widget(enfatizate2, "Imagem enfatizada2")
            foundObj2, totalObj2, objs2 = self.contornos(enfatizate2, 20)
            self.add_image_widget(objs2, f"Imagem contornada2: TOTAL: {totalObj2}; Encontrados: {foundObj2}")
#2
        #imageWithBorder = self.addBorder(gausssianBlur)
#
        #gausssianBlur2 = cv2.GaussianBlur(imageWithBorder, (3, 3), 2)
        #self.add_image_widget(gausssianBlur, "Imagem utilizando o borramento Gaussiano2")
#
        ##aplicado, total, edged = self.contornos(gausssianBlur2)
        ##self.add_image_widget(edged, f"Imagem contornada: TOTAL: {total}, {aplicado}")
#
        #sobel = self.sobel(gausssianBlur2)
        #magnitude_colored = cv2.merge([sobel, sobel, sobel])
        #self.add_image_widget(magnitude_colored, "Imagem sobel")

        #aplcado2, total2, edged2 = self.contornos(magnitude_colored)
        #self.add_image_widget(edged2, f"Imagem contornada: TOTAL: {total2} , {aplcado2}")

####
        #blur = cv2.blur(sobel, ksize=(5,5))
        #self.add_image_widget(blur, "Imagem blur")
        ##blur = cv2.blur(blur, ksize=(5,5))
        #blur = cv2.merge([blur, blur, blur])
        ##self.add_image_widget(blur, "Imagem blur")
        #bordered = self.addBorder(blur)
        ##bordered = cv2.merge([bordered, bordered, bordered])
#
        #enfatizate = self.emphasize_large_objects(self.addBorder(gausssianBlur2))
        #self.add_image_widget(enfatizate, "Imagem enfatizada")
#
        #sobel = self.sobel(enfatizate)
        #magnitude_colored = cv2.merge([sobel, sobel, sobel])
        #self.add_image_widget(magnitude_colored, "Imagem sobel")
        #aplcado2, total2, edged2 = self.contornos(enfatizate)
        #self.add_image_widget(edged2, f"Imagem contornada: TOTAL: {total2} , {aplcado2}")
    # self.add_image_widget(self.segmentWheels(laplacianFilter, cannyEdgeDetection), "Imagem final")

        #self.add_image_widget(self.encontraContorno(enfatizate), "contorno")


    def addBorder(self, image, borderSize=3):
       return cv2.copyMakeBorder(image, borderSize, borderSize, borderSize, borderSize,
                                                      cv2.BORDER_CONSTANT, value=(0, 0, 0))


    def emphasize_large_objects(self, image, thresh):
        # Converta a imagem para escala de cinza
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Binarize a imagem
        _, binary = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)#moto deixa 20

        # Encontre os contornos na imagem binarizada
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        masks = [np.zeros_like(gray) for _ in contours]
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area > 5:
                cv2.drawContours(masks[i], [contour], -1, 255, thickness=cv2.FILLED)

        # Combine todas as máscaras
        combined_mask = sum(masks)

        # Aplique a máscara combinada para realçar todos os objetos
        emphasized_image = cv2.bitwise_and(image, image, mask=combined_mask)

        return emphasized_image

    def contornos(self, image, thresh):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(gray_image, thresh, 255, cv2.THRESH_BINARY)#90

        # Encontrar contornos na imagem binarizada
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Definir uma área mínima para filtrar objetos pequenos
        min_area = 13

        # Criar uma máscara para eliminar objetos pequenos
        mask = np.zeros_like(gray_image)
        total =0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= min_area:
                total = total+1
                cv2.drawContours(mask, [contour], -1, 255, thickness=cv2.FILLED)

        # Aplicar a máscara à imagem original
        result_image = cv2.bitwise_and(gray_image, gray_image, mask=mask)
        return total, len(contours), result_image

    def removeBackgroud(self, image):
        # Criação de uma máscara invertida (todas as cores diferentes de verde)
        mask = cv2.inRange(image, (0, 40, 0), (100, 255, 100))

        # Substituição das áreas filtradas na imagem original por branco
        result_image = image.copy()
        result_image[mask != 0] = [0, 0, 0]

        return result_image

    def sobel(self, image):
        # Aplicar filtro Sobel nos eixos x e y
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        sobel_x = cv2.Sobel(gray_image, cv2.CV_64F, 4, 0, ksize=5)
        sobel_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)

        # Calcular a magnitude do gradiente
        magnitude = np.sqrt(sobel_x ** 2 + sobel_y ** 2)

        # Normalizar a magnitude para valores entre 0 e 255
        magnitude = np.uint8(255 * magnitude / np.max(magnitude))

        return magnitude



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
        # Convert CV2 image to Kivy texture
        kivy_texture = self.convert_cv2_to_kivy_texture(cv2_image)

        # Create Kivy Image widget
        kivy_image = KivyImage(texture=kivy_texture)

        # Optionally, you can add a label for the image title
        self.add_widget(Label(text=title))

        # Add the Kivy Image widget to the root layout
        container = BoxLayout(orientation='vertical')
        self.add_widget(kivy_image)

    def convert_cv2_to_kivy_texture(self, cv2_image):
        if len(cv2_image.shape) == 2:
            # A imagem é em escala de cinza
            cv2_image_rgba = cv2.cvtColor(cv2_image, cv2.COLOR_GRAY2RGBA)
        else:
            # A imagem é colorida
            cv2_image_rgba = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGBA)

        # Convert the CV2 image to Kivy texture
        h, w, _ = cv2_image_rgba.shape
        kivy_texture = Texture.create(size=(w, h))
        kivy_texture.blit_buffer(cv2_image_rgba.tostring(), colorfmt='rgba', bufferfmt='ubyte')

        return kivy_texture
