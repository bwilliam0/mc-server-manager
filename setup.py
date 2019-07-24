import setuptools

setuptools.setup(
    name='mc_server_manager',
    version='0.2.0',
    description='Manages Minecraft Servers on AWS',
    url='https://github.com/bwilliam0/mc-server-manager',
    author='bwilliam0',
    author_email='dev@mycodeiscompiling.com',
    license='MIT',
    packages=setuptools.find_packages(exclude=('scripts',)),
    entry_points={
        'console_scripts': [
            'mc-manager = mc_server_manager.mc_server_manager:main'
        ]
    },
    install_requires=[
        "boto3>=1.9.188"
        "botocore>=1.12.188"
        "docutils>=0.14"
        "jmespath>=0.9.4"
        "python-dateutil>=2.8.0"
        "s3transfer>=0.2.1"
        "six>=1.12.0"
        "urllib3>=1.25.3"
    ],
    zip_safe=False
)
