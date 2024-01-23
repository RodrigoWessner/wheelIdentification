from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from src.ImageProcessing import ImageProcessing
from src.ImageSelection import ImageSelection


class AppManager(BoxLayout):
    def __init__(self, **kwargs):
        super(AppManager, self).__init__(**kwargs)

        content_layout = BoxLayout(orientation='vertical', spacing=10)

        self.image_selection_app = ImageSelection(appManager=self)
        content_layout.add_widget(self.image_selection_app)

        self.image_processing_app = ImageProcessing()
        content_layout.add_widget(self.image_processing_app)

        self.add_widget(content_layout)

    def update_image(self, selected_file):
        self.image_processing_app.process_image(selected_file)


class AppManagerApp(App):
    def build(self):
        return AppManager()
