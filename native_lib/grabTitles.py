#!/usr/bin/env python
import time
import urllib.error
import urllib.request

url = "https://napi.v10lator.de/db?t=go"
request = urllib.request.Request(
    url,
    headers={"User-Agent": "NUSspliBuilder/2.1"},
)

print("Downloading db.go...")

content_bytes = None

for attempt in range(1, 5):
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content_bytes = response.read()
        break
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        if attempt == 4:
            raise RuntimeError(
                f"Impossibile scaricare il database dopo {attempt} tentativi."
            ) from error

        wait_seconds = 2 ** attempt
        print(
            f"Download non riuscito (tentativo {attempt}/4): {error}\n"
            f"Nuovo tentativo tra {wait_seconds} secondi..."
        )
        time.sleep(wait_seconds)

content = content_bytes.decode("utf-8")
before, separator, after = content.partition("var titleEntry")

if not separator:
    raise RuntimeError("Il server ha restituito un database in formato inatteso.")

content = (
    'package main\n'
    'import wiiudownloader "github.com/Xpl0itU/WiiUDownloader"\n'
    + separator
    + after
)
content = content.replace("[]TitleEntry{", "[]wiiudownloader.TitleEntry{")

with open("db.go", "w", encoding="utf-8") as file:
    file.write(content)

print("Database salvato in db.go")
