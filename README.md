# NotifyMe
A simple Python script to notify you when a new paper is posted on [ApexOnline.lk](https://apexonline.lk/) web platform.

## Installation
1. Clone this repository
2. Install the required libraries with `uv sync` (This project uses [uv package manager](https://docs.astral.sh/uv/))
3. Run `uv run main.py` and follow the prompts
4. You can use `auto-py-to-exe` to convert the project into a executable

## Configuration
After the first run, a `config.yaml` file will be created in the same directory as the script. You can edit this file to change the configuration.

## Usage
The script will ask for your login credentials and a download folder. After that, it will start checking for new essay or mcq paper for every 60 seconds. When a new paper is found, it will download the PDF to the specified folder and play a notification sound.

## Contributing
Contributions are welcome! If you want to add any new features or fix any bugs, please open a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.