When you need to share a document, image, or other file, return a `Path` object pointing to the file.

```python
from kamihi import bot
from pathlib import Path

@bot.action
async def send_report() -> Path:
    # Generate or locate your file
    report_path = Path("reports/monthly_summary.pdf")
    return report_path
```

!!! warning
    Use `Path` objects, not strings. Returning `"my_file.pdf"` sends the filename as a text message, not the actual file.
