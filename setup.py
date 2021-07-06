from setuptools import setup

APP=['AppsWebScraping.py']
DATA_FILES = ['icons']
APP_NAME = "News Web Scraping"
OPTIONS={
    'iconfile':'icons/news.icns',
    'argv_emulation': True,
    'includes': ['PyQt5', 'pandas', 'time', 'requests', 'math'],

}

setup(
    name=APP_NAME,
    app=APP,
    data_files=DATA_FILES,
    options={'py2app':OPTIONS},
    setup_requires=['py2app']
)