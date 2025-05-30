# web2app
PyPI package for converting a website into an app.

## Installation

Download from pip:

```shell
pip install web2app
```

## Usage

You can turn your website into an app as easy as this:

```python
from web2app import Web2Exe

exe = Web2Exe("https://www.google.com/")

exe.create(output_dir="output")
```

This infers the application icon and name from the `<title>` of the website, and the favicon from the site.

You can also specify a custom favicon and app name:

```python
exe = Web2Exe(
  name="Google",
  url="https://www.google.com/",
  icon="assets/logo512.png",
)
```

You can specify the `icon` object as a path to an icon, a PIL.Image object, or a BytesIO containing valid image data.