# 🌱 Raspberry Pi Automatic Hydroponic System 

This repository contains a Python script to manage and monitor an automatic hydroponic system using a Raspberry Pi 4. The code takes care of various tasks, such as priming pumps, filling water, dosing nutrients, and balancing pH levels.

## Features

-  Automatic water management with user-inputted target water level, and dry-back function using a water level change threshold
-  Nutrient dosing with target PPM (parts per million) and safety margin
    - There are three commonly used conversion factors for TDS meters: 500, 640, and 700
    - These all convert the EC value and the choice depends on the source of the nutrient solution
    - The 500 scale is the most common conversion factor and is typically used for nutrient solutions made with reverse osmosis or distilled water (Default for this system)
- pH management with up pump and down pump control 
- Logging system to keep track of the hydroponic system's status
- Storage of different plant customization of settings, including pH, max water level, dryback (how low can the water get before a refill), starting ppm, etc to easily switch control from one plant to another 
- Error handling and pump stopping in case of exceptions

## Requirements

- Python 3.7 or higher

### (~Estimated) Parts under $20
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
- pH probe Voltage isolator (Atlas Scientific): $25 - $35
- EC probe Voltage isolator(Atlas Scientific): $25 - $35
- Water level sensor (E-Tape): $30 - $50
- IOT Relay (RPI-controlled power strip): $30 - $50

### (~Estimated) Over $50
- EC probe (Atlas Scientific): $35 - $55
- pH probe (Atlas Scientific): $40 - $60
- Peristaltic pumps (7x): $60 - $90
- Soldering Iron kit: $65 - $95
- Raspberry Pi B+: $100 - $140

### Total estimated cost range: $600-$900

## Installation

1. Clone this repository to your Raspberry Pi:
```bash
git clone https://github.com/HydroLB/automatic-hydroponic-system.git
```

2. Navigate to the project folder:
```bash
cd RPI_Auto_Hydroponics
```

3. Install all required project dependencies (Adafruit motorkit, Atlas Scientific, ADC, etc)

## ⚙️ Configuration

You will need to configure the following variables in the `user_configurator` file

## 🚀 Usage

1. Run the main script to start the automatic hydroponic system when your in the entire project folder:
```bash
python3 main.py
```

2. Follow the prompts to reset and prime the pumps and input the target PPM and water level for your system.

3. The script will continuously monitor the hydroponic system and make adjustments as necessary based on the plants response.

## Notes

- Ensure that your pumps and sensors are properly connected to the Raspberry Pi before running the script.
- The code is designed to work with a specific set of pumps and sensors. You may need to modify the code to work with different hardware.
- The water level, and PPM are stored in a file to allow the system to resume its monitoring in the event of a reboot or power outage.

## Contributing, credits and special thanks: 
Special thanks to Michael Yinka-Oke and Sean Cunneen for bringing this project and idea to from the ground to prototype! 

This project was developed using a variety of tools, including PyCharm as the integrated development environment and implemented on a Raspberry Pi platform.

## 🌟 Ideas to Add in the Future:

1. Multiple Plants: Control Multiple plants each with their own customizations using a single bucket.

2. Alerts and Notifications: Add a feature for sending alerts and notifications when certain conditions are met or thresholds are exceeded, such as low water levels, pH imbalances, or high nutrient concentrations. This will help to inform about your system's status and to react promptly to any issues.

3. Light Management: Incorporate a light management system to control light intensity and duration, simulating day-night cycles and optimizing plant growth.

4. Temperature Control: Implement a new temperature sensor to control a heater or cooler to maintain optimal temperature levels in the hydroponic environment. Temperature is a very important aspect to increased plant growth. 

5. Humidity Control: Implement a humidity sensor and control system (fans) to maintain optimal humidity levels in the hydroponic environment. Humidity is also a big factor in plant growth speeds. 
