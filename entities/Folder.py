from services.util.jsonutil import obj_to_json, write_json_file, load_json_file_as_dict
import re


class Folder:

    def __init__(self, name: str):
        self.name = name
        self.folder_list = []
        self.video_list = []
        self.garbage_list = []

    def __eq__(self, other):
        if not isinstance(other, Folder):
            return False

        if self.name != other.name:
            return False

        for video in self.video_list:
            if video not in other.video_list:
                return False

        for garbage in self.garbage_list:
            if garbage not in other.garbage_list:
                return False

        for folder in self.folder_list:
            if folder not in other.folder_list:
                return False

        return True

    def __lt__(self, other):
        return self.name < other.name

    def add_folder(self, folder):
        self.folder_list.append(folder)

    def add_video(self, video: str):
        self.video_list.append(video)

    def add_garbage(self, garbage: str):
        self.garbage_list.append(garbage)

    def has_folder_named(self, name: str):
        for folder in self.folder_list:
            if self.name == name:
                return folder
        return Folder('empty')

    def compare_to(self, folder):
        for video in self.video_list[:]:
            if video in folder.video_list:
                self.video_list.remove(video)

        for garbage in self.garbage_list[:]:
            if garbage in folder.garbage_list:
                self.garbage_list.remove(garbage)

        for child_folder in self.folder_list[:]:
            if child_folder in folder.folder_list:
                self.folder_list.remove(child_folder)
            folder_exists = folder.has_folder_named(child_folder.name)
            if folder_exists.name != 'empty':
                child_folder.compare_to(folder_exists)

    def get_folder_type(self):
        unity_regex = re.compile('(u|unidade)\s?\d', flags=re.IGNORECASE)
        match_obj = unity_regex.search(self.name)
        if match_obj:
            match_text = match_obj.group()
            number_index = len(match_text) - 1
            unity_number = match_text[number_index]
            return f"Unidade {str(unity_number)}"
        return self.name

    def print_folder_content(self):
        if len(self.video_list) > 0:
            print(f"{str(len(self.video_list)):>2}")
        folder_and_vid = len(self.video_list) + len(self.folder_list)
        if folder_and_vid == 0:
            print(f"{'-'*33}NO VIDEO FOUND{'-'*33}")
        for folder in self.folder_list:
            folder.name = folder.get_folder_type()
        self.folder_list.sort()
        for folder in self.folder_list:
            print()
            if len(folder.video_list) > 0:
                print(f"{folder.name + ' ' + '-'*78:.78s}", end='')
                folder.print_folder_content()
            else:
                print(folder.name)
                folder.print_folder_content()

    def to_json_obj(self):
        return obj_to_json(self)

    def to_json_file(self):
        return write_json_file(self)

    def compare_to_last_from_log(self):
        last_folder = load_last_folder()
        self.compare_to(last_folder)


def dict_to_folder(dictionary):
    folder_name = str(dictionary["name"])
    folder = Folder(folder_name)
    for video in dictionary["video_list"]:
        folder.add_video(str(video))

    for garbage in dictionary["garbage_list"]:
        folder.add_garbage(str(garbage))

    for new_folder in dictionary["folder_list"]:
        folder.add_folder(dict_to_folder(new_folder))

    return folder


def load_last_folder():
    last_dict = load_json_file_as_dict()
    if last_dict is None:
        empty_folder = Folder('empty')
        return empty_folder

    last_folder = dict_to_folder(last_dict)

    return last_folder
