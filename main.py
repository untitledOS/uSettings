from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QListWidget, QStackedWidget, QCheckBox, QPushButton
from PySide6.QtCore import Qt
from PySide6 import QtCore
from PySide6.QtGui import QPixmap

import sys, platform, psutil, shutil, subprocess, os

class UpdateSystemThread(QtCore.QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sources = []
    
    def run(self):
        if "pacman" in self.sources:
            print("Updating pacman packages.")
            subprocess.run(["sudo", "pacman", "-Syu"])
        if "apt" in self.sources:
            print("Updating apt packages.")
            subprocess.run(["sudo", "apt", "update"])
            subprocess.run(["sudo", "apt", "upgrade"])
        if "dnf" in self.sources:
            print("Updating dnf packages.")
            subprocess.run(["sudo", "dnf", "update"])
        if "zypper" in self.sources:
            print("Updating zypper packages.")
            subprocess.run(["sudo", "zypper", "update"])
        if "Flatpak" in self.sources:
            print("Updating Flatpak packages.")
            # update and pass argument to not prompt user
            subprocess.run(["flatpak", "update", "-y"])
        if "pip" in self.sources:
            print("Updating pip packages.")
            subprocess.run(["pip", "install", "--upgrade", "pip"])

class WallpaperWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Change Wallpaper")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        self.wallpapers_label = QLabel("Wallpapers")
        self.layout.addWidget(self.wallpapers_label, alignment=Qt.AlignCenter)

        wallpaper_dirs = []

        if os.path.exists("/usr/share/backgrounds"):
            for wallpaper in os.listdir("/usr/share/backgrounds"):
                wallpaper_dirs.append("/usr/share/backgrounds/" + wallpaper)
        if os.path.exists("/usr/share/wallpapers"):
            for wallpaper in os.listdir("/usr/share/wallpapers"):
                wallpaper_dirs.append("/usr/share/wallpapers/" + wallpaper)

        for wallpaper in wallpaper_dirs:
            if wallpaper.endswith(".jpg") or wallpaper.endswith(".png"):
                wallpaper_image = QLabel()
                wallpaper_image.setFixedSize(100, 66)
                wallpaper_pixmap = QPixmap(wallpaper)
                wallpaper_pixmap = wallpaper_pixmap.scaled(100, 66, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                wallpaper_image.setPixmap(wallpaper_pixmap)
                self.layout.addWidget(wallpaper_image, alignment=Qt.AlignCenter)
                wallpaper_button = QPushButton(wallpaper.split("/")[-1].split(".")[0])
                self.layout.addWidget(wallpaper_button, alignment=Qt.AlignCenter)

        self.layout.addStretch()

        self.setLayout(self.layout)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("uSettings")
        self.setGeometry(100, 100, 800, 600)
        
        self.layout = QHBoxLayout()

        self.sidebar_layout = QVBoxLayout()
        self.layout.addLayout(self.sidebar_layout)

        self.settings_label = QLabel("Settings")
        self.sidebar_layout.addWidget(self.settings_label)

        self.sidebar_list = QListWidget()
        self.sidebar_list.addItem("Appearance")
        self.sidebar_list.addItem("About this system")
        self.sidebar_list.addItem("System Update")
        self.sidebar_list.addItem("Users")
        self.sidebar_layout.addWidget(self.sidebar_list)

        self.pages = QStackedWidget()
        self.layout.addWidget(self.pages)

        self.appearance = QWidget()
        appearance_layout = QVBoxLayout()
        appearance_label = QLabel("Appearance")
        appearance_layout.addWidget(appearance_label, alignment=Qt.AlignCenter)
        wallpaper_button = QPushButton("Change Wallpaper")
        wallpaper_button.clicked.connect(self.change_wallpaper)
        appearance_layout.addWidget(wallpaper_button, alignment=Qt.AlignCenter)
        appearance_layout.addStretch()
        self.appearance.setLayout(appearance_layout)
        
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
        self.update_system_layout = QVBoxLayout()
        update_system_label = QLabel("System Update", alignment=Qt.AlignCenter)
        self.update_system_layout.addWidget(update_system_label)
        for source in self.get_update_sources():
            self.update_system_layout.addWidget(QCheckBox(source, checked=True))
        update_button = QPushButton("Update System")
        self.update_system_layout.addWidget(update_button)
        update_button.clicked.connect(self.start_update_system_thread)
        self.update_system_layout.addStretch()
        self.update_system.setLayout(self.update_system_layout)

        self.pages.addWidget(self.appearance)
        self.pages.addWidget(self.update_system)
        self.pages.addWidget(QLabel("Users page"))

        self.sidebar_list.currentTextChanged.connect(self.update_page)
        self.sidebar_list.setCurrentRow(0)

        self.buttons_layout = QHBoxLayout()

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)
        self.buttons_layout.addWidget(self.quit_button)

        self.about_button = QPushButton("About")
        self.buttons_layout.addWidget(self.about_button)

        self.sidebar_layout.addLayout(self.buttons_layout)

        self.setLayout(self.layout)

    def change_wallpaper(self):
        self.wallpaper_window = WallpaperWindow()
        self.wallpaper_window.show()

    def start_update_system_thread(self):
        self.update_system_layout.itemAt(self.update_system_layout.count() - 2).widget().setText("Updating System...")
        self.update_thread = UpdateSystemThread()
        sources = []
        for i in range(self.update_system_layout.count() - 2):
            checkbox = self.update_system_layout.itemAt(i).widget()
            if checkbox is not None and type(checkbox) == QCheckBox:
                if checkbox.isChecked():
                    sources.append(checkbox.text())
        self.update_thread.sources = sources
        self.update_thread.finished.connect(self.finished_updating)
        self.update_thread.start()

    def finished_updating(self):
        print("Finished updating.")
        self.update_thread.deleteLater()
        self.update_system_layout.itemAt(self.update_system_layout.count() - 2).widget().setText("System Update Complete.")

    def update_page(self, text):
        pages = {0: self.appearance, 1: self.about_system, 2: self.update_system}
        self.pages.setCurrentWidget(pages[self.sidebar_list.currentRow()])

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
            elif distro == "Fedora Linux":
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
        sources = []
        if package_manager != None:
            sources.append(package_manager)
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
