import toml
import sys

version = sys.argv[1]
print(f"🔧 Updating pyproject.toml version to {version}")

with open("pyproject.toml", "r") as f:
    data = toml.load(f)

data["project"]["version"] = version

with open("pyproject.toml", "w") as f:
    toml.dump(data, f)