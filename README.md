# OpenEXR Viewer

A simple Python based viewer for OpenEXR (.exr) files with annotation capabilities. I built this quickly as a prototype so I could figure out how to support and display OpenEXR in a another app. It turned out to work well enough to share here for anyone who needs to support OpenEXR.

## Features

- View high dynamic range OpenEXR (.exr) images with proper tone mapping
- Draw and annotate directly on images
- Support for OpenEXR and PNG used by the animation industry
- Export annotated images back to OpenEXR or convert to PNG
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

  ## Next Update

- Change colour of annotation tool
- Undo/Redo annotation tool
- More file formats to convert
- Binaries for macOS and Windows

## License

This project is licensed under the Apache License Version 2.0.

[OpenImageIO](https://github.com/AcademySoftwareFoundation/OpenImageIO) for EXR file support

Since this project uses [PySide](https://doc.qt.io/qtforpython-6/licenses.html), it follows the LGPL requirements.
