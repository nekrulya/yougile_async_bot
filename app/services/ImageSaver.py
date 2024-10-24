from pathlib import Path

from config import SAVE_PATH


class ImageSaver:
    def __init__(self, bot):
        self.bot = bot

    async def save_images(self, photo_id_list, state):
        current_state = await state.get_data()
        topic, title, images = current_state.get('topic'), current_state.get('title'), current_state.get('images')
        for photo_id in photo_id_list:
            file_info = await self.bot.get_file(photo_id)
            file_path = file_info.file_path
            downloaded_file = await self.bot.download_file(file_path)

            folder_counter = 0
            while True:
                folder_path = Path(f"{SAVE_PATH}/{topic}_{folder_counter}")
                if not folder_path.exists():
                    folder_path.mkdir(parents=True, exist_ok=True)
                    break
                folder_counter += 1

            file_name = f"{folder_path}/{title}_{len(images) + 1}.jpg"
            with open(file_name, 'wb') as new_file:
                new_file.write(downloaded_file.getvalue())

