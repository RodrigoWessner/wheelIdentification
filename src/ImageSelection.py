from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.label import Label
from kivy.uix.popup import Popup


class ImageSelection(BoxLayout):
    def __init__(self, appManager, **kwargs):
        super(ImageSelection, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.app_manager = appManager
        self.folder_path = "C:/Users"
        # "C:/Users/rodrigo.wessner/Documents/UNISC/Processamento de imagens/Downloads"

        self.label_widget = Label(text="Imagem selecionada: nenhuma imagem foi selecionada")
        self.add_widget(self.label_widget)

        self.button_widget = Button(text="Clique para selecionar uma imagem", on_press=self.select_image)
        self.add_widget(self.button_widget)

        self.file_chooser = FileChooserIconView()
        self.file_chooser.bind(on_submit=self.on_file_selected)

    def select_image(self, *args):
        file_chooser = FileChooserIconView(path=self.folder_path, filters=["*.jpg", "*.png"])
        file_chooser.bind(on_submit=self.on_file_selected)

        popup = Popup(title="Escolha uma imagem", content=file_chooser, size_hint=(0.9, 0.9))
        file_chooser.popup = popup
        popup.open()

    def on_file_selected(self, instance, selection, *args):
        if selection:
            selected_file = selection[0]
            self.label_widget.text = f"Imagem Selecionada: {selected_file}"

            self.app_manager.update_image(selected_file)

            instance.popup.dismiss()
