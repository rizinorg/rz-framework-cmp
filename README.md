Comparison tool for Rizin to other RE frameworks or Rizin versions.

# Using and setup

Install `uv`: https://docs.astral.sh/uv/#installation

```
uv venvce .venv/bin/activate
source .venv/bin/activate
uv sync
uv run Compare.py -h
```

# Testing

```
pytest
```

[!NOTE]
> `uv tool run pytest` doesn't seem to work currently.
