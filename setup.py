from setuptools import setup, find_packages

setup(
    name = "workspace-filesystem",
    version = "0.0.1",
    description = "Manage workspaces",
    long_description = open('README.md').read(),
    long_description_content_type = 'text/markdown',
    packages = find_packages(),
    install_requires = [
    ],
    python_requires = '>=3.6',
    entry_points = {
        'console_scripts': [
            'wf=wfscli.cli:main',
        ],
    }
)