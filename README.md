# 🌱 Raspberry Pi Automatic Hydroponic System 🌿

This repository contains a Python script to manage and monitor an automatic hydroponic system using a Raspberry Pi 4. The code takes care of various tasks, such as priming pumps, filling water, dosing nutrients, and balancing pH levels.

## ✨ Features

- 🚰 Automatic water management with user-inputted target water level, and dry-back function using a water level change threshold
- 🌡️ Nutrient dosing with target PPM (parts per million) and safety margin
- 🧪 pH management with up and down pump control
- 📋 Logging system to keep track of the hydroponic system's status
- ⚠️ Error handling and pump stopping in case of exceptions

## 📦 Requirements

- Python 3.7 or higher
- Raspberry Pi 4
- Compatible pumps, water level, and pH sensors

## 🛠️ Installation

1. Clone this repository to your Raspberry Pi:
```bash
git clone https://github.com/your_username/automatic-hydroponic-system.git
```

2. Navigate to the project folder:
```bash
cd automatic-hydroponic-system
```

3. Install the required packages using pip:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

You will need to configure the following variables in the main function code:

- `ph_var`: List containing times for pH up and down pumps to be on per cycle, and time between each cycle (loop) .
- `WATER_LEVEL_CHANGE_THRESHOLD`: Water level change threshold in inches (activate the dry-back feature, this controls how        often a fillup to the top occurs).
- `WAIT_TIME_BETWEEN_CHECKS`: Time in seconds to wait between each water level check and ph check.
- `NUTRIENT_PPM_SAFETY_MARGIN`: Safety margin in ppm between the actual target PPM and the first nutrient dosing cycle, as the ph balancing raises ppm too.

## 🚀 Usage

1. Run the main script to start the automatic hydroponic system:
```bash
python3 main.py
```

2. Follow the prompts to reset and prime the pumps and input the target PPM and water level for your system.

3. The script will continuously monitor the hydroponic system and make adjustments as necessary based on the plants response.

## 📝 Notes

- Ensure that your pumps and sensors are properly connected to the Raspberry Pi before running the script.
- The code is designed to work with a specific set of pumps and sensors. You may need to modify the code to work with different hardware.
- The water level, PPM, and pH values are stored in a file to allow the system to continue monitoring in the event of a reboot or power outage.

## 🤝 Contributing and special thanks
Special thanks to Michael Yinka-Oke and Sean Cunneen for bringing this project and idea to from the ground to reality! 

Contributions are welcome! If you have any suggestions or improvements, feel free to submit a pull request or create an issue.
