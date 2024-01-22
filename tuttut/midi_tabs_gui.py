import numpy as np
np.seterr(divide="ignore")

from tuttut.GUI import config, gui

def run():
    """ Lance l'application """

    try:
        config.ui_open_mode = config.UIOpenMode.CHROME
        gui.start(config.ui_open_mode)
    except:
        config.ui_open_mode = config.UIOpenMode.USER_DEFAULT
        gui.start(config.ui_open_mode)

if __name__ == '__main__':
    run()