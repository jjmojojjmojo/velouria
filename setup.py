from setuptools import setup, find_packages
setup(
    name = "velouria",
    version = "0.1",
    packages = find_packages('src'),
    package_dir = {'':'src'},
    install_requires = [
        ""
    ],
    entry_points = {
        'console_scripts': [
            'velouria = velouria:main',
            'velouria-ctl = velouria:ctl',
        ],
        'velouria.slide': [
            'image = velouria.slide:ScaledImageSlide',
            'browser = velouria.slide:BrowserSlide',
            'test = velouria.slide:Slide'
        ]
    },
)
