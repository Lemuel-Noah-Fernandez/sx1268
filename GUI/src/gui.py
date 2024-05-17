import json
import os
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout

class DataDisplay(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create a label for the Science Data table
        self.science_table_label = Label(text="Science Data", size_hint=(None, None), size=(400, 30))
        self.science_table_label.pos_hint = {'x': 0, 'top': 1}
        self.add_widget(self.science_table_label)

        # Create a layout for the Science Data table
        self.science_table_layout = GridLayout(cols=2, size_hint=(None, None), size=(400, 200))
        self.science_table_layout.pos_hint = {'x': 0, 'top': 0.95}
        self.add_widget(self.science_table_layout)

        # Create a label for the Pose Data table
        self.pose_table_label = Label(text="Pose Data", size_hint=(None, None), size=(400, 30))
        self.pose_table_label.pos_hint = {'x': 0.5, 'top': 1}
        self.add_widget(self.pose_table_label)

        # Create a layout for the Pose Data table
        self.pose_table_layout = GridLayout(cols=2, size_hint=(None, None), size=(400, 200))
        self.pose_table_layout.pos_hint = {'x': 0.5, 'top': 0.95}
        self.add_widget(self.pose_table_layout)

        # Create a label for the WOD Data table
        self.wod_table_label = Label(text="WOD Data", size_hint=(None, None), size=(400, 30))
        self.wod_table_label.pos_hint = {'x': 0, 'top': 0.4}
        self.add_widget(self.wod_table_label)

        # Create a layout for the WOD Data table
        self.wod_table_layout = GridLayout(cols=2, size_hint=(None, None), size=(400, 200))
        self.wod_table_layout.pos_hint = {'x': 0, 'top': 0.35}
        self.add_widget(self.wod_table_layout)

        # Schedule the update method to be called every 5 seconds
        self.update_data(10)
        Clock.schedule_interval(self.update_data, 5)

    def update_data(self, dt):
        data_files = {
            'wod_data.json': None,
            'pose_data.json': None,
            'science_data.json': None,
            'misc_data.json': None
        }

        data_dir = 'GUI/data'
        for file_name in data_files.keys():
            file_path = os.path.join(data_dir, file_name)
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    if data:
                        data_files[file_name] = data[-1]  # Get the last entry
            except (FileNotFoundError, json.JSONDecodeError):
                data_files[file_name] = None

        self.display_data(data_files['science_data.json'], 'science')
        self.display_data(data_files['pose_data.json'], 'pose')
        self.display_data(data_files['wod_data.json'], 'wod')

    def display_data(self, data, data_type):
        if data_type == 'science':
            layout = self.science_table_layout
        elif data_type == 'pose':
            layout = self.pose_table_layout
        elif data_type == 'wod':
            layout = self.wod_table_layout

        layout.clear_widgets()

        if not data:
            return

        # Display the data in the table
        for key, value in data.items():
            if key == "datasets" and data_type == "wod":
                if value:
                    first_dataset = value[0]
                    for sub_key, sub_value in first_dataset.items():
                        layout.add_widget(Label(text=sub_key))
                        layout.add_widget(Label(text=str(sub_value)))
            else:
                layout.add_widget(Label(text=key))
                layout.add_widget(Label(text=str(value)))

class DataApp(App):
    def build(self):
        return DataDisplay()

if __name__ == '__main__':
    DataApp().run()
