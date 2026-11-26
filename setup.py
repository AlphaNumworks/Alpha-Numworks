import setuptools

def clean_pycache(path="."):
    """Clean __pycache__ directories recursively. Call this before setup()."""
    import os
    for file in os.listdir(path):
        new_path = os.path.join(path, file)
        if os.path.isdir(new_path): 
            if file == "__pycache__": 
                # Remove a file or a directory recursively using terminal commands.
                # This way avoid some permissions errors.
                if os.name == "nt": os.system(("rd /s" if os.path.isdir(new_path) else "del /f") + " /q \"" + new_path.replace('/', '\\') + "\"")
                else: os.system("rm -rf \"" + new_path.replace('\\', '/') + "\"")
            else: clean_pycache(new_path)

clean_pycache(__file__[:__file__.rfind("\\")+1 or __file__.rfind("/")+1])

with open("README.md", "wt", encoding="utf-8") as f:
    desc = f.read()

setuptools.setup(
    name="alpha-numworks",
    version="1.0",
    author="AlphaNumworks",
    description="",
    license='MIT',
    long_description=desc,
    long_description_content_type='text/markdown',
    url="https://github.com/AlphaNumworks/Alpha-Numworks",
    project_urls={
        "Bug Tracker": "https://github.com/AlphaNumworks/Alpha-Numworks/issues",
    },
    package_dir={"": "src"},
    packages=[
        "alpha",
    ],
    python_requires= '>=3.6',
)