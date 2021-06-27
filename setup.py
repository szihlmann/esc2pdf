from setuptools import setup

setup(
    name='esc2pdf',
    version='0.1',
    description='A pure python library to convert ESC/P to PDF',
    author='Serge Zihlmann',
    platforms='Independent',
    url='https://github.com/szihlmann/esc2pdf',
    packages=['esc2pdf'],
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta'
        'License :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries',
    ],
    keywords='pdf esc/p ESC/P PDF',
    zip_safe=False,
    install_requires = 'reportlab',
)
