# KeyClean

## Version 0, before Gemini review

I want to create a "keyboard cleaning application" for Linux, MacOS and Windows.
The basic idea is to grab the keyboard and allow the user to press any key or combination (as much as possible) without
any effect while wiping and pressing randomly.

A special keyboard sequence ("keys are clean") or mouse click on a button to end the "cleaning".
The screen should display an extended keyboad (F1 to F12, arrow keys, numpad) in the middle showing which key is
currently pressed and a counter of total number of keys pressed so far.
Instructions and a "Done" button to exit the application should be shown on the bottom.

The project must use:

- Python (3.9 and newer) and the `pygame` for multiplatform compatability.
- The extremely fast Python package manager `uv` should be used.
- The tools `autopep8`, `pylint`, `pytest` and `tox` should be used for formatting and testing.

The source files should be under a `src` directory.
The project will be uploaded to https://test.pypi.org/ and https://pypi.org/ using twine.
The license will be the Unlicense.
A sample `Makefile` is provided and must be updated.
An `.editorconfig` file is provided and should be respected.
Type hints should be added where possible.

Is it possible? Concerns? Ask questions.

Prepare a plan for implementation and let me review it.

## Version 1

# Project: KeyClean

Role: Lead Software Architect / Developer

## Objective

Create a cross-platform keyboard cleaning utility for Linux, macOS, and Windows.
The app must "lock" the keyboard, visually reflecting keypresses on a virtual UI while suppressing their effect on the
OS,
allowing users to wipe their physical keyboard without triggering commands.

## Core Requirements

1. **Input Handling:** - Capture all keyboard events. Use `pygame` for the UI, but acknowledge that native OS hooks (
   e.g., `pynput` or platform-specific APIs) might be needed to achieve a "Global Hook" that suppresses system
   shortcuts.
    - Requirement: The app must prevent accidental "destructive" key combos (like Alt+F4 or Cmd+Q) while in cleaning
      mode.
2. **Visual Feedback:**
    - A 100% (Full/Extended) keyboard layout visualization (F-keys, arrows, numpad).
    - Real-time highlighting of keys currently held down.
    - A persistent counter showing total key strikes during the session.
3. **Exit Mechanics:**
    - A specific "Safety Sequence" (e.g., typing 'keys are clean') or a prominent "Done" button clickable via mouse to
      release the lock and exit.

## Technical Stack & Constraints

- **Language:** Python 3.9+ with strict Type Hinting.
- **UI:** `pygame`.
- **Environment:** Use `uv` for dependency management (provide a `pyproject.toml`).
- **DevOps/QA:**
    - Formatting: `autopep8`.
    - Linting: `pylint`.
    - Testing: `pytest` (with `pytest-mock` for input simulation) and `tox` for cross-version testing.
- **Structure:** `src/` layout.
- **Deployment:** Ready for PyPI/TestPyPI via `twine`.
- **Licensing:** Unlicense.
- **Artifacts:** Update the existing `Makefile` and respect the `.editorconfig`.

## Instructions for Claude

1. Analyze the feasibility of "Global Input Suppression" across Linux (X11/Wayland), macOS (Accessibility Permissions),
   and Windows (LowLevelHooks).
2. Detail how you will handle high-frequency random inputs (keyboard mashing) without crashing the event queue.
3. Provide a directory structure and a step-by-step implementation plan.
4. DO NOT write all the code yet. Present the plan and the proposed `pyproject.toml` for review first.
5. Ask questions to clarify unclear points.

# More prompts

> These are the prompts used in the Claude Sonnet 4.6 vibe-coding session.

1. "0. My name is 'Doncho Nikolaev Gunchev', not 'Dimitar'. 1. Yes, use 'keys are clean' exactly. 2. ISO 105 key. 3. Full screen application. 4. Use pygame-ce. 5. Yes, update the Makefile accordingly, this is just a sample/skeleton. 6. Use `pynput`. And write the plan to PLAN.md."

2. "Excellent, I added minor detail with date/time display. Please proceed with the plan." *(after manually editing the renderer line in PLAN.md)*

3. "Write this summary after all done to CHANGELOG.md."

4. "I added all files to git, please commit."

5. "The command `uv sync --group dev` does not seem to do anything."

6. "Add this info to README, development section."

7. "commit please"

8. "On Linux (KDE, Wayland) the Super (windows) key is showing the start menu. Is there a way to capture it. Is some dependency missing?"

9. "Yes please, implement option A and commit." *(during implementation)* "Please add a notice to `sudo usermod -aG input $USER` to the user, if the access is not granted on /dev/*..."

10. "The `Enter` key overlaps with `Del`. Please shorten the `# ~` key and fit the `Enter` there." *(with screenshot)*

11. "Please add a `Makefile` targed that creates new release. Something like `make V=0.2.0 release` that updates the version everywhere, tags it in git and adds the changes (from git log) to @CHANGELOG.md."

12. "If /dev/input/event* isn't readable, in addition to logging: sudo usermod -aG input $USER for stronger evdev-level suppression, add it below the \"keys are clean\" hint."

13. "Before the clock on the top add the application title and short description as a header. Make the milliseconds from the clock optional, it is too \"busy\"."

14. "Nice. Append the prompts I used to PROMPT.md in the project root. Make release 0.9.0, tag it and commit (without PROMPT.md)."

15. For some reason the Super key gets captured by KeyClean, but shortly after KDE's application launcher picks it up too.

16. Nope, same story. Maybe take a look how @~/github/gunchev/kbdclean/ does it, there is no problem with Super.

17. Put the release part in a separate python script `release.py`, clean the Makefile.

18. Clean and fix the "clean" target in the @Makefile.

19. "Add a `run` make target, that does all the uv sync steps and then uv runs the app. Development mode."

20. "Hey, won't that only work on Linux?"

21. "When I run it locally, everything works, the Super key is captured. When I upload to pypi and run it with `uvx keyclean` the Super key leaks to KDE. What could be wrong, missing dependency?"

22. "Nice, make new release and upload."

23. "Add the version to the first line."

24. "Add `-dev` to the version if there are uncommitted changes or commits after the last tag." *(interrupted after proposal — see next)*

25. "Yes please. And do a release."

26. "`__init__.py` in the release shows `0.9.5-dev` instead of `0.9.4`."

27. "Add all prompts missing from @PROMPT.md, this one included, commit, then `make release V=0.9.5` please."

28. "On MacOS I noticed a warning that some dependency is missing. I used `uv tool install keyclean`. Is it also missing/optional, like `evdev` was on Linux?"

29. "On MacOS I also noticed that the arrow keys have boxes instead of arrows (missing font glyphs?)."

30. "Next to the left Shift there is an extra `\|` button, remove it and enlarge the shift key."

31. "Move the first line of keys, `Esc` ... `F12` ... `Pause` a bit up, doubling the distance they have from the second line. Align `Print Screen` with `Ins` and `Del` horizontally. Align the right side of the `Enter` key with `Backspace` and the right `Shift`."

32. "Add more spacing to the first row (`Esc` .. `F12`) so that `F12` aligns with `Backspace` on the right. Remove the `#~` key on the bottom left of the `Enter` key and join the space to the `Enter` key. Expand the `\|` key on the left top of the `Enter` key to normal width, taking the space from `Enter`. Move the `Enter` label down to use the newly joined space."

33. "Auch, make the `Enter` key only use the second line. Shift `\|` right to not overlap with `]}` and extend it right to align with `Backspace`."

34. "Perfection. Now, you mentioned something about handling negative rows. Won't shifting everything a bit down solve that problem?"

35. "Nice. Add all prompts to @PROMPT.md and create a new release please."

36. "Interesting, on MacOS 0.9.5 was working, but 0.9.6 is crashing and I am getting a prompt to reopen it (which does not work). Also, I get `keyclean` and `keyclean-gui`, what is the use of the second script?"

37. "Let's test that. You know the drill, @PROMPT.md, release and I will test."
