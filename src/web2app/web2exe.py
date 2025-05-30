import pathlib
import typing
from PIL import Image
import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import io
import os
import re
import unicodedata
import base64
import subprocess
import shutil
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

        if (not name) or (not icon):
            response = requests.get(url)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.text, "html.parser")

        # Handle name
        if not name:
            soup = self.soup
            if soup.title and soup.title.string:
                self.name = soup.title.string.strip()
                logger.warning("`name` not specified, defaulting to title from site URL: %s", self.name)
            else:
                raise TitleNotFound(f"No <title> found at {url} and no name provided.")
        else:
            self.name = name

        # Handle icon
        if not icon:
            soup = self.soup
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
        internal_app_name = re.sub(r"[^A-Za-z]", "", unicodedata.normalize("NFKD", self.name).encode("ascii", "ignore").decode()).upper()

        output_dir = os.path.abspath(output_dir)
        build_path = os.path.abspath(os.path.join(output_dir, "build"))
        os.makedirs(build_path, exist_ok=True)
        cwd = os.getcwd()
        os.chdir(build_path)

        self.icon.save("logo.ico", format="ICO")
        
        Program_cs = """namespace $internal_app_name{internal static class Program{[STAThread]static void Main(){ApplicationConfiguration.Initialize();Application.Run(new $internal_app_name());}}}""".replace("$internal_app_name", internal_app_name)
        with open("Program.cs", "w") as file:
            file.write(Program_cs)

        app_name_cs = """namespace $internal_app_name{public partial class $internal_app_name : Form{public $internal_app_name(){InitializeComponent();this.Resize += new EventHandler(Form_Resize);webView21.Source = new Uri("$url");}private void Form_Resize(object sender, EventArgs e){webView21.Width=this.ClientSize.Width;webView21.Height=this.ClientSize.Height;}}}""".replace("$internal_app_name", internal_app_name).replace("$url", self.url)
        with open(f"{internal_app_name}.cs", "w") as file:
            file.write(app_name_cs)

        app_name_csproj = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>WinExe</OutputType><TargetFramework>net8.0-windows</TargetFramework><Nullable>enable</Nullable><UseWindowsForms>true</UseWindowsForms><ImplicitUsings>enable</ImplicitUsings><ApplicationIcon>logo.ico</ApplicationIcon></PropertyGroup><ItemGroup><Content Include="logo.ico" /></ItemGroup><ItemGroup><PackageReference Include="Microsoft.Web.WebView2" Version="1.0.2957.106" /></ItemGroup></Project>"""
        with open(f"{internal_app_name}.csproj", "w") as file:
            file.write(app_name_csproj)

        app_name_csproj_user = """<?xml version="1.0" encoding="utf-8"?><Project ToolsVersion="Current" xmlns="http://schemas.microsoft.com/developer/msbuild/2003"><ItemGroup><Compile Update="$internal_app_name.cs"><SubType>Form</SubType></Compile></ItemGroup></Project>""".replace("$internal_app_name", internal_app_name)
        with open(f"{internal_app_name}.csproj.user", "w") as file:
            file.write(app_name_csproj_user)

        app_name_designer_cs = """namespace $internal_app_name{partial class $internal_app_name{private System.ComponentModel.IContainer components = null;protected override void Dispose(bool disposing){if (disposing && (components != null)){components.Dispose();}base.Dispose(disposing);}private void InitializeComponent(){System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof($internal_app_name));webView21 = new Microsoft.Web.WebView2.WinForms.WebView2();((System.ComponentModel.ISupportInitialize)webView21).BeginInit();SuspendLayout();webView21.AllowExternalDrop = true;webView21.CreationProperties = null;webView21.DefaultBackgroundColor = Color.White;webView21.Dock = DockStyle.Fill;webView21.Location = new Point(0, 0);webView21.Name = "webView21";webView21.Size = new Size(800, 450);webView21.TabIndex = 0;webView21.ZoomFactor = 1D;AutoScaleDimensions = new SizeF(10F, 25F);AutoScaleMode = AutoScaleMode.Font;ClientSize = new Size(800, 450);Controls.Add(webView21);Icon = (Icon)resources.GetObject("$this.Icon");Name = "$app_name";Text = "$app_name";((System.ComponentModel.ISupportInitialize)webView21).EndInit();ResumeLayout(false);}private Microsoft.Web.WebView2.WinForms.WebView2 webView21;}}""".replace("$internal_app_name", internal_app_name).replace("$app_name", self.name)
        with open(f"{internal_app_name}.Designer.cs", "w") as file:
            file.write(app_name_designer_cs)

        buffer = io.BytesIO()
        self.icon.save(buffer, format="ICO")
        icon_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        app_name_resx = """<?xml version="1.0" encoding="utf-8"?><root><xsd:schema id="root" xmlns="" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:msdata="urn:schemas-microsoft-com:xml-msdata"><xsd:import namespace="http://www.w3.org/XML/1998/namespace" /><xsd:element name="root" msdata:IsDataSet="true"><xsd:complexType><xsd:choice maxOccurs="unbounded"><xsd:element name="metadata"><xsd:complexType><xsd:sequence><xsd:element name="value" type="xsd:string" minOccurs="0" /></xsd:sequence><xsd:attribute name="name" use="required" type="xsd:string" /><xsd:attribute name="type" type="xsd:string" /><xsd:attribute name="mimetype" type="xsd:string" /><xsd:attribute ref="xml:space" /></xsd:complexType></xsd:element><xsd:element name="assembly"><xsd:complexType><xsd:attribute name="alias" type="xsd:string" /><xsd:attribute name="name" type="xsd:string" /></xsd:complexType></xsd:element><xsd:element name="data"><xsd:complexType><xsd:sequence><xsd:element name="value" type="xsd:string" minOccurs="0" msdata:Ordinal="1" /><xsd:element name="comment" type="xsd:string" minOccurs="0" msdata:Ordinal="2" /></xsd:sequence><xsd:attribute name="name" type="xsd:string" use="required" msdata:Ordinal="1" /><xsd:attribute name="type" type="xsd:string" msdata:Ordinal="3" /><xsd:attribute name="mimetype" type="xsd:string" msdata:Ordinal="4" /><xsd:attribute ref="xml:space" /></xsd:complexType></xsd:element><xsd:element name="resheader"><xsd:complexType><xsd:sequence><xsd:element name="value" type="xsd:string" minOccurs="0" msdata:Ordinal="1" /></xsd:sequence><xsd:attribute name="name" type="xsd:string" use="required" /></xsd:complexType></xsd:element></xsd:choice></xsd:complexType></xsd:element></xsd:schema><resheader name="resmimetype"><value>text/microsoft-resx</value></resheader><resheader name="version"><value>2.0</value></resheader><resheader name="reader"><value>System.Resources.ResXResourceReader, System.Windows.Forms, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089</value></resheader><resheader name="writer"><value>System.Resources.ResXResourceWriter, System.Windows.Forms, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089</value></resheader><assembly alias="System.Drawing" name="System.Drawing, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a" /><data name="$this.Icon" type="System.Drawing.Icon, System.Drawing" mimetype="application/x-microsoft.net.object.bytearray.base64"><value>""" + icon_b64 + """</value></data></root>"""
        with open(f"{internal_app_name}.resx", "w") as file:
            file.write(app_name_resx)

        result = subprocess.run(["dotnet", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            logger.fatal("dotnet is not installed on your system. Please install it before continuing.")
            exit(1)

        result = subprocess.run(
            ["dotnet", "build", f"{internal_app_name}.csproj", "--configuration", "Release"],
            cwd=os.path.abspath(build_path),
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise BuildError("DOTNET BUILD ERROR:\n\n" + result.stderr)
    
        build_output_dir = os.path.join(build_path, "bin", "Release", "net8.0-windows")
        for item in os.listdir(build_output_dir):
            s = os.path.join(build_output_dir, item)
            d = os.path.join(output_dir, item)
            shutil.move(s, d)

        os.chdir(cwd)

        shutil.rmtree(build_path)