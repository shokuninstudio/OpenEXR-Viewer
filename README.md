# OpenEXR Viewer

A simple Python based viewer for OpenEXR (.exr) files with annotation capabilities.

## Features

- View high dynamic range OpenEXR (.exr) images with proper tone mapping
- Draw and annotate directly on images
- Support for OpenEXR and PNG used by the animation industry
- Export annotated images back to OpenEXR or PNG
- Simple and intuitive user interface

The application allows you to make annotations and notes directly on your images for:

- Marking areas of interest in HDR images
- Adding comments for collaborators
- Highlighting artifacts or areas for correction
- Creating visual guides and references

When displaying EXR images, the application uses the Reinhard tone mapping operator to convert high dynamic range content to a displayable range while preserving detail in both highlights and shadows.

If you need to add support for OpenEXR in your Python based app feel free to use the import and export code herewithin. 
## Screenshot

[![temp-Image-V0-Pxnq.avif](https://i.postimg.cc/jq6gbrhm/temp-Image-V0-Pxnq.avif)](https://postimg.cc/bdJHxWW9)

## Installation

1. Prerequisites

- Python 3.6 or higher
- PySide6 (Qt for Python)
- NumPy
- OpenImageIO

2. Install dependencies

  `pip install pyside6 numpy openimageio`

3. Run the application

  `python openexr_viewer.py`

## License

This project is licensed under the BSD 2-Clause License.

[OpenImageIO]([https://doc.qt.io/qtforpython-6/licenses.html](https://github.com/AcademySoftwareFoundation/OpenImageIO) for EXR file support

Since this project uses [PySide](https://doc.qt.io/qtforpython-6/licenses.html), it follows the LGPL requirements.
