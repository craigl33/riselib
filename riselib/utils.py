import os


def get_files(root_folder, file_type, id_text, subfolder=''):
    """Basic function to walk through folder and return all files of a certain type containing specific text in its name."""
    searched_files = []
    folder = os.path.join(root_folder, subfolder)

    for dirpath, subdirs, files in os.walk(folder):
        for file in files:
            if (file.endswith(file_type)) & (id_text in file):
                searched_files.append(os.path.join(os.path.normpath(dirpath), file))

    return searched_files
