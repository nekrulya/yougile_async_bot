import json

import requests
from config import API_KEY

class URLS:
    COMPANIES: str = "https://ru.yougile.com/api-v2/auth/companies"
    PROJECTS: str = "https://ru.yougile.com/api-v2/projects"
    BOARDS: str = "https://ru.yougile.com/api-v2/boards"
    COLUMNS: str = "https://ru.yougile.com/api-v2/columns"
    TASKS: str = "https://ru.yougile.com/api-v2/tasks"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

async def set_task(title: str, description: str, column_id: str, deadline: int | None = None):
    data = {
        "title": title,
        "description": description,
        "columnId": column_id,
    }

    if deadline:
        data["deadline"] = {
            "deadline": deadline
        }

    response = requests.post(URLS.TASKS, headers=HEADERS, data=json.dumps(data))
    return response.json().get('id')