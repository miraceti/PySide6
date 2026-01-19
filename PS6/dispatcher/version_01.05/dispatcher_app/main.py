import sys
from PySide6.QtWidgets import QApplication

from ui.accueil import Accueil
from config.loader import load_config
config = load_config()

def main():
    app = QApplication(sys.argv)
    
    # Fenêtre principale (A0)
    accueil = Accueil(config) # type: ignore
    accueil.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
