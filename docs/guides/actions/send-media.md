This guide details how to send any type of media supported by Kamihi.

## Sending media

There are two ways of sending media using Kamihi:

- **Implicit**: you return a `Path` object in your function, and the framework automatically detects the best way of sending the file.
- **Explicit**: you return a `bot.Media` subclass that tells the framework how to treat the file.

=== "Implicit"

    ```python
    from kamihi import bot
    from pathlib import Path
                 
    @bot.action
    async def start() -> Path:
        return Path("actions/start/file.txt")
    ```

=== "Explicit"

    ```python
    from kamihi import bot
    from pathlib import Path
                 
    @bot.action
    async def start() -> bot.Document:
        return bot.Document("actions/start/file.txt")
    ```

!!! warning
    Only media types based on files can be sent implicitly.

## Supported media types

Kamihi supports sending the following media types:

| Media                 | Type           | Allowed formats                    | Max. size | Notes                                                                                       |
|-----------------------|----------------|------------------------------------|-----------|---------------------------------------------------------------------------------------------|
| Documents             | `bot.Document` | Any                                | 50MB      | Default sending mode                                                                        |
| Photos                | `bot.Photo`    | JPG <br/> PNG <br/> GIF <br/> WEBP | 10MB      | -                                                                                           |
| Videos                | `bot.Video`    | MP4                                | 50MB      | -                                                                                           |
| Audios                | `bot.Audio`    | MP3 <br/> M4A                      | 50MB      | If less than 1MB, it will be detected as a voice note                                       |
| Voice notes           | `bot.Voice`    | MP3 <br/> M4A <br/> OGG (Opus)     | 1MB       | If more than 1MB, it will be detected as audio                                              |
| Media groups (albums) | `list`         | -                                  | -         | Only sent as group if all items are of the same type (Photo and Video are considered equal) |
| Location              | `bot.Location` | -                                  | -         | Defined by latitude, longitude and optional horizontal accuracy                             |


## Examples

=== "Documents"

    ```python
    from kamihi import bot
    from pathlib import Path

    # implicit
    @bot.action
    async def start() -> Path:
        return Path("actions/start/file.txt")

    # explicit
    @bot.action
    async def start() -> bot.Document:
        return bot.Document("actions/start/file.txt")
    ```

=== "Photos"

    ```python
    from kamihi import bot
    from pathlib import Path

    # implicit
    @bot.action
    async def start() -> Path:
        return Path("actions/start/image.jpg")

    # explicit
    @bot.action
    async def start() -> bot.Photo:
        return bot.Photo(Path("actions/start/image.jpg"))
    ```

=== "Videos"

    ```python
    from kamihi import bot
    from pathlib import Path

    # implicit
    @bot.action
    async def start() -> Path:
        return Path("actions/start/video.mp4")

    # explicit
    @bot.action
    async def start() -> bot.Video:
        return bot.Video(Path("actions/start/video.mp4"))
    ```

=== "Audios"

    ```python
    from kamihi import bot
    from pathlib import Path

    # implicit
    @bot.action
    async def start() -> Path:
        return Path("actions/start/audio.mp3")

    # explicit
    @bot.action
    async def start() -> bot.Audio:
        return bot.Audio(Path("actions/start/audio.mp3"))
    ```

=== "Voice notes"

    ```python
    from kamihi import bot
    from pathlib import Path

    # implicit
    @bot.action
    async def start() -> Path:
        return Path("actions/start/voice.ogg")

    # explicit
    @bot.action
    async def start() -> bot.Voice:
        return bot.Voice(Path("actions/start/voice.ogg"))
    ```

=== "Media groups"

    ```python
    from kamihi import bot
    from pathlib import Path

    # implicit
    @bot.action
    async def start() -> list[Path]:
        return [
            Path("actions/start/image1.jpg"),
            Path("actions/start/image2.jpg"),
            Path("actions/start/video.mp4")
        ]

    # explicit
    @bot.action
    async def start() -> list[bot.Audio]:
        return [
            bot.Photo(Path("actions/start/audio1.mp3")),
            bot.Photo(Path("actions/start/audio2.mp3")),
        ]
    ```

=== "Location"

    ```python
    from kamihi import bot
    from pathlib import Path

    # explicit
    @bot.action
    async def start() -> bot.Location:
        return bot.Location(latitude=37.7749, longitude=-122.4194, horizontal_accuracy=100)
    ```

## Adding captions

Adding captions to media you send is only possible when marking the type of media explicitly. You just need to pass the `caption` keyword argument to the constructor of the media type.

```python
from kamihi import bot
from pathlib import Path
             
@bot.action
async def start() -> bot.Document:
    return bot.Document(Path("actions/start/file.txt"), caption="This is a file caption.")
```

!!! info
    To caption media groups, there are two options:
    
    - Caption every item in the group with their own caption by passing the `caption` keyword argument.
    - Caption just the first item in the group, and it will be used as the caption for the entire group.
