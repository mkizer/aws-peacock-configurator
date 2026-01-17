# AWS Peacock Configurator

This utility creates and updates the configuration file for the AWS Peacock Management Console browser plugin. It provides a user-friendly graphical interface to manage your AWS console customizations, including environment-specific configurations and color themes.

The browser plugin is available here: [AWS Peacock Management Console](https://chromewebstore.google.com/detail/aws-peacock-management-co/bknjjajglapfhbdcfgmhgkgfomkkaidj)

The plugin source code is also on GitHub: [aws-peacock-management-console](https://github.com/xhiroga/aws-peacock-management-console)

## Features

-   **Graphical Configuration**: Easy-to-use GUI for creating and editing your JSON configuration files.
-   **Environment Management**: Configure multiple AWS accounts and regions with distinct visual styles.
-   **Picklist Support**: Maintain local picklists for frequently used Regions and Account IDs to speed up configuration.
-   **Theme Generation**: Automatically generate harmonious color pairs for your environments.
-   **Clipboard Integration**: Quickly copy your generated configuration to the clipboard for use in the extension.

## Prerequisites

-   Python 3.x installed on your system.
-   `pip` package manager.

## Installation

1.  Clone this repository or download the source code:

    ```bash
    git clone <repository_url>
    cd aws-peacock-configurator
    ```

2.  Create and activate a virtual environment:

    ```bash
    python -m venv .venv
    .\.venv\Scripts\Activate  # On Windows
    # source .venv/bin/activate  # On macOS/Linux
    ```

3.  Install the required Python dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Run the application:

    ```bash
    python configurator.py
    ```

2.  **Managing Configurations**:
    -   **Load Config**: Open an existing `.json` configuration file.
    -   **Add Block**: Create a new configuration block for a specific environment (Account/Region).
    -   **Manage Picklists**: Add or remove frequently used Accounts and Regions to populate dropdown menus.
    -   **Generate Theme**: Use the "Generate Theme" button within a block to create a unique color scheme.
    -   **Save Config**: Save your changes back to a file.
    -   **Copy Config**: Copy the current configuration JSON to your clipboard to paste into the AWS Peacock extension settings.

## Configuration Structure

The tool generates a JSON configuration compatible with the AWS Peacock extension, typically looking like this:

```json
[
  {
    "env": {
      "account": "123456789012",
      "region": "us-east-1"
    },
    "style": {
      "navigationBackgroundColor": "#123456",
      "accountMenuButtonBackgroundColor": "#abcdef"
    }
  }
]
```

## Contributing

Feel free to submit issues or pull requests to improve this configurator tool.
