from setuptools import setup, find_packages

setup(
    name='dongdong',
    version='0.0.4',
    description='Be notified when your running script is complete',
    long_description='This package is used to monitor python scripts and push status messages to Bark, WeChat, DingTalk, Teams and Desktop.',
    long_description_content_type='text/markdown',
    url='https://github.com/ChenglongLi777/DongDong',
    author='Chenglong Li',
    author_email='chenglongli@cug.edu.cn',
    license='MIT',
    packages=find_packages(),
        entry_points={
            'console_scripts': [
                'dongdong = dongdong.__main__:main'
            ]
    },
    zip_safe=False,
    python_requires='>=3.6',
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ]
)