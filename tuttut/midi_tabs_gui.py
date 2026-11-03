import numpy as np
np.seterr(divide="ignore")

from tuttut.GUI import config, gui

def run():
    """ Lance l'application """

    try:
        gui.start(config.UIOpenMode.CHROME)
    except Exception as e:
        print(f"Could not start in Chrome app mode ({e}), falling back to the default browser.")
        gui.start(config.UIOpenMode.USER_DEFAULT)

if __name__ == '__main__':
    run()