from pathlib import Path

from aiogram.fsm.context import FSMContext

from config import SAVE_PATH

class AttachmentSaver:
    def __init__(self, bot):
        self.bot = bot

    async def save(self, state: FSMContext):
        folder_path = None
        state_data = await state.get_data()
        topic, title, image_paths, document_paths = (state_data.get("topic", ""),
                                                     state_data.get("title", ""),
                                                     state_data.get("image_paths", []),
                                                     state_data.get("document_paths", []))

        folder_counter = 1
        while image_paths + document_paths:
            folder_path = Path(f"{SAVE_PATH}/{topic}_{folder_counter}")
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                break
            folder_counter += 1

        for index, document_path in enumerate(image_paths + document_paths):
            downloaded_file = await self.bot.download_file(document_path)
            file_extension = document_path.split(".")[-1]
            file_name = f"{folder_path}/{title}_{index}.{file_extension}"
            with open(file_name, 'wb') as new_file:
                new_file.write(downloaded_file.getvalue())

        return folder_path


# class ImageSaver:
#     def __init__(self, bot):
#         self.bot = bot
#
#     async def save_images(self, photo_path_list, state):
#         folder_path = None
#         current_state = await state.get_data()
#         topic, title, images = current_state.get('topic'), current_state.get('title'), current_state.get('images')
#
#         folder_counter = 1
#         while True:
#             folder_path = Path(f"{SAVE_PATH}/{topic}_{folder_counter}")
#             if not folder_path.exists():
#                 folder_path.mkdir(parents=True, exist_ok=True)
#                 break
#             folder_counter += 1
#
#         for index, photo_path in enumerate(photo_path_list, 1):
#             downloaded_file = await self.bot.download_file(photo_path)
#             file_name = f"{folder_path}/{title}_{index}.jpg"
#             with open(file_name, 'wb') as new_file:
#                 new_file.write(downloaded_file.getvalue())
#
#         return folder_path
#
#
# class DocumentSaver:
#     def __init__(self, bot):
#         self.bot = bot
#
#     async def save(self, document_path_list, state):
