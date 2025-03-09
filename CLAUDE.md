# CLAUDE.md - Discord Notify Project Guidelines

## Run Commands
- Run notifier: `python twitch_discord_notifier.py`
- Run with verbose logging: `python twitch_discord_notifier.py --verbose`
- Test notification: `python twitch_discord_notifier.py --test`
- Specify config file: `python twitch_discord_notifier.py --config your_config.json`

## Installation
- Install dependencies: `pip install -r requirements.txt`

## Code Style Guidelines
- **Imports**: Standard library first, third-party next, local modules last
- **Type Hints**: Use typing annotations for all function parameters and returns
- **Naming**: Use snake_case for variables/functions, PascalCase for classes
- **Error Handling**: Use try/except blocks with specific exceptions; log errors
- **Logging**: Use the logging module with appropriate levels (info, debug, error)
- **Documentation**: Docstrings for all classes and functions
- **JSON Config**: Use for all configuration parameters
- **Constants**: Define at module or class level in UPPER_CASE