---
name: SPL 2.0 runtime location
description: The active SPL 2.0 runtime is at /home/gongai/projects/digital-duck/SPL20, not references/SPL20 or SPL
type: project
---

The installed SPL 2.0 runtime that `spl` CLI uses is at `/home/gongai/projects/digital-duck/SPL20/spl/`.

**Why:** There are multiple SPL directories — `references/SPL20` (cookbook reference copy), `/home/gongai/projects/digital-duck/SPL` (old v1), and `/home/gongai/projects/digital-duck/SPL20` (the live runtime). Edits to cli.py or other runtime files must go to `/home/gongai/projects/digital-duck/SPL20/spl/`.

**How to apply:** Always verify with `python3 -c "import spl.cli; print(spl.cli.__file__)"` if unsure. Edit the file that command points to.
