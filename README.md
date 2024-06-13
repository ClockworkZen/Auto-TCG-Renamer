
# TCG OCR Processing Script

## Overview

This script processes images of Pokémon and Magic: The Gathering trading cards, utilizing OCR technology to recognize and rename the cards accordingly. It is designed to work with two separate folders (`Pokemon` and `Magic`) and processes images found within their subdirectories, moving processed images to a `Processed` directory and handling errors by moving problematic images to an `Error` directory.

## Features

- **EasyOCR Integration**: Uses EasyOCR to extract text from Magic: The Gathering cards.
- **OpenAI GPT Integration**: Utilizes OpenAI's GPT-4o to identify Pokémon cards based on image input.
- **Subdirectory Processing**: Processes images in subdirectories, ignoring `Processed` and `Error` directories.
- **Error Handling**: Logs errors and moves problematic files to an `Error` directory.
- **File Preprocessing**: Sanitizes filenames to ensure compatibility.


## Prerequisites

- Python 3.x
- Required Python libraries: `os`, `cv2` (OpenCV), `easyocr`, `requests`, `logging`, `re`, `unicodedata`, `shutil`, `base64`, `json`, `sys`, `pathlib`

Install the required libraries using pip:

```bash
pip install easyocr requests opencv-python
```

## Setup

1. Create a `tcg.cfg` configuration file in the root directory with your OpenAI API key:

    ```cfg
    api_key=YOUR_OPENAI_API_KEY
    ```

2. Ensure you have the following folder structure:

    ```
    .
    ├── tcg.cfg
    ├── Auto-TCG-Renamer.py
    ├── Pokemon
    │   ├── Subfolder1
    │   ├── Subfolder2
    │   └── ...
    └── Magic
        ├── Subfolder1
        ├── Subfolder2
        └── ...
    ```

3. Place your Pokémon card images in the appropriate subfolders under the `Pokemon` directory.
4. Place your Magic: The Gathering card images in the appropriate subfolders under the `Magic` directory.

## Usage

1. Run the script:

    ```bash
    python Auto-TCG-Renamer.py
    ```

2. The script will start with a "Script is starting up..." message.
3. It will process images found in the `Pokemon` and `Magic` subdirectories.
4. Processed images will be moved to a `Processed` directory under each subfolder.
5. If any errors occur, the problematic images will be moved to an `Error` directory under each subfolder.
6. If no new files are detected, the script will display "No new files detected." and exit gracefully.

## Logging

- The script logs its actions and any errors to `log.txt`.

### Enabling CUDA

This has only been tested on Windows.

 1. Download and install [CUDA Toolkit 11.8](https://developer.nvidia.com/cuda-11-8-0-download-archive)
 2. Downlaod and install [cuDNN](https://developer.nvidia.com/cudnn-downloads)
 3. 3. Set your PATH directories correctly with the following commands
     ```
     setx PATH "%PATH%;C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin;C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\libnvvp;C:\tools\cuda\bin"
     setx CUDA_HOME "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8"
  4. Verify that your paths are correct by using the following command on the command line:
     `nvcc --version`
  5. Install the correct version of Torch using the following command:
    `pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`

If everything is set up correctly, open up a python console and execute the following command: 
```
import torch
print(torch.cuda.is_available())
```
If this returns True, you can use CUDA now!


## Troubleshooting

- Ensure your API key is correctly set in the `tcg.cfg` file.
- Check `log.txt` for any error messages if the script does not behave as expected.
- Verify that your images are in the correct subfolders under `Pokemon` and `Magic`.

## License

This project is licensed under the MIT License.
