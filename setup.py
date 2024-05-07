from setuptools import setup, find_packages

setup(
    name='fably',
    version='1.0',
    python_requires='>3.8',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'openai',
        'apa102-pi',
        'sounddevice',
        'soundfile',
        'click',
        'dotenv',
        'pyyaml',
        'vosk',
        'numpy',
    ],
    entry_points='''
        [console_scripts]
        fably=fably.cli:cli
    ''',
)
