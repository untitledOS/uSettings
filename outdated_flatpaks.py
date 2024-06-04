import subprocess

def get_available_packages():
    """
    Gets a list of available flatpak packages and their versions.
    """
    output = subprocess.run(["flatpak", "list", "--available"], capture_output=True, text=True)
    return output.stdout.strip().split("\n")[1:]    # Remove header and empty line

def get_installed_packages():
    """
    Gets a list of installed flatpak packages and their versions.
    """
    output = subprocess.run(["flatpak", "list"], capture_output=True, text=True)
    return output.stdout.strip().split("\n")[1:]    # Remove header and empty line

def compare_versions(available, installed):
    """
    Compares versions of a specific package.
    Returns True if available version is newer.
    """
    available_version = available.split()[1]
    installed_version = installed.split()[1]
    return available_version > installed_version

def outdated_flatpaks():
    """
    Checks for outdated flatpak packages and prints the count.
    """
    available_packages = get_available_packages()
    installed_packages = get_installed_packages()
    outdated_count = 0

    for available_package in available_packages:
        package_name = available_package.split()[0]
        if any(installed_package.startswith(package_name) for installed_package in installed_packages):
            installed_version = next(package for package in installed_packages if package.startswith(package_name)).split()[1]
            if compare_versions(available_package, installed_version):
                outdated_count += 1
    
    return outdated_count

if __name__ == "__main__":
    outdated_flatpaks()
