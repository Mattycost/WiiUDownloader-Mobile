#!/usr/bin/env python
import time
import urllib.error
import urllib.request

url = "https://napi.v10lator.de/db?t=go"
request = urllib.request.Request(
    url,
    # Match the current upstream WiiUDownloader build script's user agent.
    headers={"User-Agent": "NUSspliBuilder/2.2"},
)

print("Downloading db.go...")
content_bytes = None
last_error = None

# The database endpoint has been intermittently disconnecting CI runners.
# Retry transient failures with bounded backoff before failing clearly.
for attempt in range(1, 7):
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            content_bytes = response.read()
        if not content_bytes:
            raise RuntimeError("Il server ha restituito un database vuoto.")
        break
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        last_error = error
        if attempt == 6:
            raise RuntimeError(
                f"Impossibile scaricare il database dopo {attempt} tentativi."
            ) from error
        wait_seconds = min(2 ** attempt, 30)
        print(
            f"Download non riuscito (tentativo {attempt}/6): {error}\n"
            f"Nuovo tentativo tra {wait_seconds} secondi..."
        )
        time.sleep(wait_seconds)

if content_bytes is None:
    raise RuntimeError(f"Download del database fallito: {last_error}")

try:
    content = content_bytes.decode("utf-8")
except UnicodeDecodeError as error:
    raise RuntimeError("Il database ricevuto non è UTF-8 valido.") from error

_, separator, after = content.partition("var titleEntry")
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
