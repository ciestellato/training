import os

folder_path = r"C:\Users\0602JP\Desktop\新しいフォルダー"

for filename in os.listdir(folder_path):
    if filename.endswith(".py"):
        new_filename = filename.replace(".py", ".txt")
        os.rename(
            os.path.join(folder_path, filename),
            os.path.join(folder_path, new_filename)
        )