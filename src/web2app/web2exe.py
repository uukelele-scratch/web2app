import pathlib
import typing
from PIL import Image
import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import io
from .errors import *


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",)
logger = logging.getLogger(__name__)

class Web2Exe:
    """
    Use Web2Exe to create a Web2Exe object.

    This class helps package a website into an executable.
    """

    def __init__(
        self,
        url: str,
        name: str = "",
        icon: typing.Union[str, pathlib.Path, Image.Image, io.BytesIO] = "",
    ) -> None:
        """
        Initialize a new Web2Exe instance.

        Args:
            url (str): The URL of the site. **Required**.
            name (str, optional): The name of the executable. If not specified, the site's `<title>` is used.
            icon (str | pathlib.Path | PIL.Image.Image | io.BytesIO, optional): Path, URL, PIL.Image, or io.BytesIO object for the icon. 
                If not specified, the favicon from the site URL is used.
        """

        
        self.url = url

        # Handle name
        if not name:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            if soup.title and soup.title.string:
                self.name = soup.title.string.strip()
                logger.warning("`name` not specified, defaulting to title from site URL: %s", self.name)
            else:
                raise TitleNotFound(f"No <title> found at {url} and no name provided.")
        else:
            self.name = name

        # Handle icon
        if not icon:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            icon_link = soup.find("link", rel=lambda x: x and "icon" in x.lower())
            if icon_link and icon_link.has_attr("href"):
                favicon_url = urljoin(url, icon_link["href"])
            else:
                favicon_url = urljoin(url, "/favicon.ico")

            res = requests.get(favicon_url)
            if res.status_code != 200:
                raise FaviconNotFound(f"No favicon found at {favicon_url} and no icon provided.")
            self.icon = io.BytesIO(res.content)
            logger.warning("`icon` not specified, defaulting to favicon from site URL.")
        else:
            self.icon = icon

        # Format icon into PIL.Image
        match type(self.icon):
            case Image.Image:
                pass
            case io.BytesIO:
                self.icon = Image.open(self.icon)
            case pathlib.Path:
                self.icon = Image.open(self.icon)
            case str:
                self.icon = Image.open(self.icon)


    def create(
        self,
        output_dir: typing.Union[str, pathlib.Path]
    ):
        """
        Build an Exe app.

        Args:
            output_dir (str | pathlib.Path): The output directory to write to. **Required**.
        """
        pass