## Summary

- reconnect the scaffold `uv run` invocation in `install.sh` to `/dev/tty` so `curl | bash` keeps interactive prompts
- add `scaffold._tty_input()` to read from the active terminal when stdin is piped
- replace scaffold prompt reads with `_tty_input()` and print a clean error message instead of a traceback when no terminal input is available
- update scaffold unit tests for the new input wrapper and cover TTY, `/dev/tty`, and EOF error paths

## Verification

- `bash -n install.sh`
- `python -m compileall scaffold.py tests/unit/test_scaffold.py`
- manual Python sanity checks for `_tty_input()` and `main()` EOF handling
- installer smoke via `script(1)` with local `file://.../scaffold.py`: prompts appeared normally before the run later failed on offline dependency resolution

## Environment Limits

- `uv run pytest ...` and `uv run ruff ...` could not be completed in this sandbox because it has no network access and no preinstalled `pytest` or `ruff`
- a fully non-interactive `install.sh` smoke without a controlling TTY could not be reproduced here because the shell itself fails opening `/dev/tty` before Python starts
