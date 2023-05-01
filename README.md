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
Here's an updated version with better readability:

### (~Estimated) Under $20
- Zip ties: $4 - $6
- Wire stripper: $6 - $10
- 12V AC adapter (2x): $6 - $10
- Raspberry Pi Cobbler: $6 - $10
- Heat shrink pack: $6 - $10
- Epoxy glue: $8 - $12
- Wood board: $8 - $12
- Mason jars: $8 - $12
- Raspberry Pi screw set: $8 - $12
- Long screws for pump attachment: $8 - $12
- Silicone tubing: $8 - $12
- Temperature sensor and circuit: $8 - $12
- Analog-to-digital converter: $10 - $12
- Protoboards: $12 - $18
- Large fresh water pump: $12 - $18
- Multistrand wire pack: $13 - $20
- Single strand wire pack: $13 - $20
- Wire crimper and crimps: $15 - $25

### (~Estimated) $20 - $50
- Clear PVC tubes (4x): $20 - $30
- 8-gallon bucket with lid: $25 - $35
- pH probe Voltage isolator: $25 - $35
- EC probe Voltage isolator: $25 - $35
- Water level sensor (E-Tape): $30 - $50
- IOT Relay: $30 - $50

### (~Estimated) Over $50
- EC probe (Atlas Scientific): $35 - $55
- pH probe (Atlas Scientific): $40 - $60
- Peristaltic pumps (7x): $60 - $90
- Soldering Iron kit: $65 - $95
- Raspberry Pi B+: $100 - $140

### Total estimated cost range: $600-$900

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

- `ph_var`: List of 3, containing times for pH up and down pumps to be on per cycle, and time between each cycle (loop) when dosing for pH.

- `WATER_LEVEL_CHANGE_THRESHOLD`: This parameter determines the minimum difference in water level (in inches) needed to trigger a fill-up, promoting stronger root growth by encouraging plants to search for water deeper in the ground. Adjust the threshold to optimize watering frequency and root strength. Consider updating this value in relation to the plant's growth stage. As the plant matures, increase the time between fill-ups to encourage deeper root growth.
- Smaller threshold -> More frequent fill-ups. Larger threshold -> Less frequent fill-ups, stronger roots. Never let the roots be too dry. I rather err on the side of caution even if the roots won't be as big.  

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
- The water level, and PPM are stored in a file to allow the system to resume its monitoring in the event of a reboot or power outage.

## 🤝 Contributing, credits and special thanks: 
Special thanks to Michael Yinka-Oke and Sean Cunneen for bringing this project and idea to from the ground to reality! 

This project uses support code from the following sources:

Adafruit Library: [Name of the library] (Link to the library)
Copyright (c) [Year(s)] Adafruit Industries. Licensed under the MIT License.

Atlas Scientific Library: [Name of the library] (Link to the library)
Copyright (c) [Year(s)] Atlas Scientific LLC. Licensed under the MIT License.

This project was developed using a variety of tools, including PyCharm as the integrated development environment, OpenAI's API and GitHub Copilot as coding assistants, and implemented on a Raspberry Pi platform.

Original contributions and unique code in this project:
Copyright © [2023] [Leon Bouramia]. All rights reserved.
This original work is licensed under the GNU Affero General Public License v3.0 (AGPLv3). The full license text can be found at https://www.gnu.org/licenses/agpl-3.0.en.html

Contributions are welcome! If you have any suggestions or improvements, feel free to submit a pull request or create an issue.
