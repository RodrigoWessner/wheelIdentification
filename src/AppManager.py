from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from src.ImageProcessing import ImageProcessing
from src.ImageSelection import ImageSelection


class AppManager(BoxLayout):
    def __init__(self, **kwargs):
        super(AppManager, self).__init__(**kwargs)

        # Create a BoxLayout to hold the ImageSelection and ImageProcessing
        content_layout = BoxLayout(orientation='vertical', spacing=10)

        # Image Selection App
        self.image_selection_app = ImageSelection(appManager=self)
        content_layout.add_widget(self.image_selection_app)

        # Image Processing App
        self.image_processing_app = ImageProcessing()
        content_layout.add_widget(self.image_processing_app)

        # Set the content of the ScrollView
        self.add_widget(content_layout)


    def update_image(self, selected_file):
        # Call a method in ImageProcessing to handle the selected image
        self.image_processing_app.process_image(selected_file)


class AppManagerApp(App):
    def build(self):
        return AppManager()
