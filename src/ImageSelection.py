# image_selection.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup


class ImageSelection(BoxLayout):
    def __init__(self, appManager, **kwargs):
        super(ImageSelection, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.app_manager = appManager
        self.folder_path = "C:/Users/rodrigo.wessner/Documents/UNISC/Processamento de imagens/Downloads"

        # Label to display the selected image path
        self.label_widget = Label(text="Imagem selecionada: nenhuma imagem foi selecionada")
        self.add_widget(self.label_widget)

        # Button to open file selection dialog
        self.button_widget = Button(text="Clique para selecionar uma imagem", on_press=self.select_image)
        self.add_widget(self.button_widget)

        # FileChooser for selecting an image
        self.file_chooser = FileChooserIconView()
        self.file_chooser.bind(on_submit=self.on_file_selected)

    def select_image(self, *args):
        # Open the file selection dialog
        file_chooser = FileChooserIconView(path=self.folder_path, filters=["*.jpg", "*.png"])
        file_chooser.bind(on_submit=self.on_file_selected)

        # Create a popup and add the FileChooserIconView to it
        popup = Popup(title="Escolha uma imagem", content=file_chooser, size_hint=(0.9, 0.9))
        file_chooser.popup = popup
        popup.open()

    def on_file_selected(self, instance, selection, *args):
        # Callback when a file is selected
        if selection:
            selected_file = selection[0]
            self.label_widget.text = f"Imagem Selecionada: {selected_file}"

            # Update the Image widget in AppManager
            self.app_manager.update_image(selected_file)

            # Dismiss the popup
            instance.popup.dismiss()
