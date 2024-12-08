import toml
import requests

def fetch_latest_version(package_name):
    """Fetch the latest version of a package from PyPI."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()["info"]["version"]
    except requests.RequestException as e:
        print(f"Error fetching version for {package_name}: {e}")
        return None

def update_pipfile(pipfile_path="Pipfile"):
    """Update Pipfile with the latest versions of packages."""
    pipfile = toml.load(pipfile_path)
    for section in ["packages", "dev-packages"]:
        if section in pipfile:
            for package in pipfile[section]:
                if pipfile[section][package] == "*":
                    latest_version = fetch_latest_version(package)
                    if latest_version:
                        pipfile[section][package] = f">={latest_version}"
                        print(f"Updated {package} to >= {latest_version}")
    # Save the updated Pipfile
    with open(pipfile_path, "w") as f:
        toml.dump(pipfile, f)
        print("Pipfile updated successfully!")

# Run the script
update_pipfile()
