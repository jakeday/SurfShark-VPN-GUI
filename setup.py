#!/usr/bin/python3
import setuptools
import setuptools.command.build_py

setuptools.setup(
    name='SurfShark VPN GUI',
    version='1.0',
    description='SurfShark VPN GUI',
    keywords='vpn',
    author='Jake Day',
    url='https://github.com/jakeday/SurfShark-VPN-GUI',
    python_requires='>=3.8',
    include_package_data=True,
    data_files=[
        ('/usr/share/icons/hicolor/scalable/apps', ['surfsharkgui/assets/surfsharkgui.png']),
        ('/usr/share/applications', ['surfsharkgui/assets/surfsharkgui.desktop'])
    ],
    package_data={
        '': ['assets/*']
    },
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'surfsharkvpngui=surfsharkgui:main',
        ],
    },
)
