from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QListWidget, QStackedWidget, QCheckBox, QPushButton
from PySide6.QtCore import Qt
from PySide6 import QtCore

import sys, platform, psutil, GPUtil, shutil

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("uSettings")
        self.setGeometry(100, 100, 800, 600)
        
        self.layout = QHBoxLayout()

        self.sidebar_layout = QVBoxLayout()
        self.layout.addLayout(self.sidebar_layout)

        self.system_label = QLabel("System")
        self.sidebar_layout.addWidget(self.system_label)

        self.list_system = QListWidget()
        self.list_system.addItem("About this system")
        self.list_system.addItem("System Update")
        self.list_system.addItem("Users")
        self.sidebar_layout.addWidget(self.list_system)

        self.pages = QStackedWidget()
        self.layout.addWidget(self.pages)

        self.about_system = QWidget()
        about_system_layout = QVBoxLayout()
        about_software_label = QLabel("Software")
        about_system_layout.addWidget(about_software_label, alignment=Qt.AlignCenter)
        for key, value in self.get_software_information().items():
            about_system_layout.addWidget(QLabel(f"{key}: {value}", alignment=Qt.AlignCenter))
        about_hardware_label = QLabel("Hardware", alignment=Qt.AlignCenter)
        about_system_layout.addWidget(about_hardware_label)
        for key, value in self.get_hardware_information().items():
            about_system_layout.addWidget(QLabel(f"{key}: {value}", alignment=Qt.AlignCenter))
        about_system_layout.addStretch()
        self.about_system.setLayout(about_system_layout)
        self.pages.addWidget(self.about_system)

        self.update_system = QWidget()
        update_system_layout = QVBoxLayout()
        update_system_label = QLabel("System Update", alignment=Qt.AlignCenter)
        update_system_layout.addWidget(update_system_label)
        for source in self.get_update_sources():
            update_system_layout.addWidget(QCheckBox(source, checked=True))
        update_button = QPushButton("Update")
        update_system_layout.addWidget(update_button)
        update_system_layout.addStretch()
        self.update_system.setLayout(update_system_layout)
        self.pages.addWidget(self.update_system)

        self.pages.addWidget(QLabel("Users page"))

        self.list_system.currentTextChanged.connect(self.update_page)

        self.setLayout(self.layout)

    def update_page(self, text):
        if text == "About this system":
            self.pages.setCurrentIndex(0)
        elif text == "System Update":
            self.pages.setCurrentIndex(1)
        elif text == "Users":
            self.pages.setCurrentIndex(2)

    def get_software_information(self):
        info = {}
        info["Hostname"] = platform.node()
        info["Architecture"] = platform.machine()
        info["System"] = platform.system()
        info["Distribution"] = platform.freedesktop_os_release().get("NAME", "Unknown")
        info["Kernel"] = platform.release()
        info["Python version"] = platform.python_version()
        info["Qt version"] = QtCore.__version__
        return info
    
    def get_hardware_information(self):
        info = {}
        # dont use platform for hardware info
        info["CPU Cores"] = psutil.cpu_count()
        info["CPU Clock Speed"] = f"{psutil.cpu_freq().current / 1000:.2f} GHz"
        info["RAM"] = f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GiB"
        return info
    
    def get_update_sources(self):
        if platform.system() == "Linux":
            distro = platform.freedesktop_os_release().get("NAME", "Unknown")
            if distro == "Arch Linux":
                package_manager = "pacman"
            elif distro == "Debian GNU/Linux":
                package_manager = "apt"
            elif distro == "Fedora":
                package_manager = "dnf"
            elif distro == "openSUSE Leap":
                package_manager = "zypper"
            elif distro == "Ubuntu":
                package_manager = "apt"
            else:
                package_manager = None
        if shutil.which("flatpak"):
            flatpak = True
        else:
            flatpak = False
        sources = [f"{package_manager}"]
        if flatpak:
            sources.append("Flatpak")
        try:
            import pip
            sources.append("pip")
            del pip
        except ImportError:
            pass
        return sources

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())