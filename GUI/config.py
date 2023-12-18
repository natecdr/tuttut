import os

class UIOpenMode:
    NONE = 0
    CHROME = 1
    USER_DEFAULT = 2

# Frontend
FRONTEND_ASSET_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'web')

# Argument-influenced configuration
ui_open_mode = UIOpenMode.CHROME
