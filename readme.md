# Th Nuremberg moodle PDF crawler

## How to use

1. Install Firefox
2. Install poetry
3. Install dependencies with `poetry install`
4. configure the `config.ini` file for your course
5. Run `poetry run python src/crawler --username <username> --password <password>`
6. Run `poetry run python src/sroter.py`
6. will place all found files in the corosponding folder

## How to configure

The `config.ini` file is used to configure the crawler. The structure:

```ini
[course]
url = https://moodlepage.de/course/view.php?id=12345

[moodle]
url_login = https://moodlepage.de/course/login/index.php
```

The `file_structure.json` is used to declare where to copy files to

```json
{
    "format": "file sorter 0.1.0",
    "files": [
        {
            "name": "Audio.mp3",
            "destination": "music",
            "last_change": "",
            "overwrite": "true"
        }
    ]
}
```
