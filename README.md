Comparison tool for Rizin to other RE frameworks or Rizin versions.

## Using and setup

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

## Requirements

- Tested binaries MUST have DWARF information.
  The covered address ranges of symbols are only calculated with that data to ensure they are accurate.

## Measurements

The runtime and resource measurements are very much approximates.
Mostly because "Python". But also the sample frequency is just not that high for some variables (e.g. Maximum RAM used).
It still should be decent enough for judgments.
