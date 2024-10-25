from pathlib import Path

from config import SAVE_PATH


class ImageSaver:
    def __init__(self, bot):
        self.bot = bot

    async def save_images(self, photo_path_list, state):
        folder_output = None
        current_state = await state.get_data()
        topic, title, images = current_state.get('topic'), current_state.get('title'), current_state.get('images')

        folder_counter = 1
        while True:
            folder_path = Path(f"{SAVE_PATH}/{topic}_{folder_counter}")
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                folder_output = folder_path
                break
            folder_counter += 1

        for index, photo_path in enumerate(photo_path_list, 1):
            downloaded_file = await self.bot.download_file(photo_path)
            file_name = f"{folder_path}/{title}_{index}.jpg"
            with open(file_name, 'wb') as new_file:
                new_file.write(downloaded_file.getvalue())

        return folder_output