# ECO BIN

![ECO BIN Header Banner](PICS/green%20bin%20close.png) *(Note: Placeholder banner)*

A Streamlit-powered smart waste disposal dashboard that uses Google Vision AI to identify waste items and recommend the correct bin.

## Overview

**ECO BIN** is a polished, interactive kiosk-style application designed for community waste sorting. Users can upload or capture a photo of a waste item, and the application instantly provides a bin recommendation (Green, Blue, Red, or Yellow). The system is designed to encourage recycling by offering live fill-level monitoring, a point-based reward system, an interactive leaderboard, and nearby bin guidance using geolocation.

## Key Features

- **Intuitive UI:** Clean Streamlit UI with a dark eco-themed dashboard, making it accessible for public kiosks or personal use.
- **AI-Powered Classification:** Integrates with Google Cloud Vision API for robust object detection and waste classification.
- **Smart Bin Recommendation:**
  - 🟢 **Green Bin:** Composting (Food, fruits, vegetables, plants)
  - 🔵 **Blue Bin:** Recycling (Plastics, glass, paper, bottles, cans)
  - 🔴 **Red Bin:** E-Waste (Electronics, laptops, batteries, devices)
  - 🟡 **Yellow Bin:** Landfill (General waste and unknown items)
- **Live Fill Tracking:** Admin dashboard allows monitoring and management of bin capacities. Simulates live fill levels with near-full alerts.
- **Reward System & Leaderboard:** Users entering an `Eco-ID` earn points for sorting waste. The leaderboard tracks top contributors in the community.
- **Find a Bin:** Utilizes geolocation to find and suggest the nearest available bins.
- **Lightweight State Management:** Uses TinyDB (`db.json`) for persistent and fast app-state across sessions.

## Working of the Project

The ECO BIN project is divided into several interactive modules tailored for a seamless user and admin experience:

1. **Kiosk Interface:**
   - The user approaches the kiosk screen and navigates to the **Kiosk** tab.
   - They enter their unique **Eco-ID** (to earn points).
   - They can either **Take a Picture** using the local camera or **Upload an Image** of the waste item.
   - Upon clicking **Process Item**, the image is sent to the **Google Cloud Vision API**.
2. **AI Classification & Routing:**
   - The Vision API returns descriptive labels for the object in the image.
   - The application scans these labels against predefined keyword sets for Green, Blue, and Red bins.
   - If a match is found, the system assigns the item to the specific bin. If no match is found, it defaults to the Yellow bin (Landfill).
3. **Bin Actuation (Simulation):**
   - The UI simulates the opening of the corresponding bin while leaving others closed.
   - The chosen bin's capacity increases slightly, and the user's score increases in the database seamlessly.
4. **Admin Dashboard:**
   - Administrators can monitor the real-time capacity of all four bins.
   - When a bin reaches maximum capacity (e.g., > 95%), an alert is shown, indicating it requires emptying. Admins can reset the fill level back to 0% once physically emptied.
5. **Leaderboard & Find a Bin:**
   - The **Leaderboard** tab ranks users by points accumulated, incentivizing correct sorting.
   - The **Find a Bin** tab uses the user's current GPS location (via `streamlit-js-eval`) to simulate finding nearby bins with available capacity.

## Repository Structure

```text
├── app.py                  # Main Streamlit application and core logic
├── style.css               # Optional supplementary CSS styling
├── PICS/                   # Static bin images used for UI
├── db.json                 # TinyDB state storage file (auto-generated)
├── firstpic.webp           # Landing image used in the intro section
├── gcp-key.json            # Google Cloud credentials (NOT to be committed)
├── yolov8n.pt              # Optional local YOLO weights (if used)
├── weights/                # Directory for model weights
├── samples/                # Sample images and assets for testing
└── README.md               # Detailed documentation (this file)
```

## Requirements

- **Python:** 3.10 or higher
- **PackageManager:** `pip`

## Setup & Installation

**1. Clone the repository:**
```bash
git clone https://github.com/DarshanPavithra/ecobin.git
cd ecobin
```

**2. Set up a virtual environment (Optional but Recommended):**
```bash
python -m venv venv
source venv/bin/activate       # On Linux/Mac
venv\Scripts\activate          # On Windows
```

**3. Install dependencies:**
```bash
pip install streamlit pandas tinydb google-cloud-vision streamlit-js-eval
```
> *Note:* `streamlit-js-eval` is used for geolocation support when available.

**4. Google Vision API Setup:**
- Go to the [Google Cloud Console](https://console.cloud.google.com/).
- Create a new project and enable the **Cloud Vision API**.
- Create a Service Account, generate a JSON key, and download it.
- Rename the downloaded file to `gcp-key.json` and place it in the root directory of this project.
- *The application is configured to automatically pick up `gcp-key.json` to authenticate API calls.*

## Running the App

Launch the application using the Streamlit cli:

```bash
streamlit run app.py
```

The application will launch and be accessible at `http://localhost:8501` in your web browser.

## Notes & Troubleshooting

- `db.json` will be automatically created upon the first run and will start storing user points and bin fill states.
- Ensure your `gcp-key.json` file is ignored in `.gitignore` to prevent leaking sensitive API keys.
- If geolocation features are not working, ensure your browser allows location access to `localhost`.

## License

This project is created as a project submission for the BUILD WITH AI Hackathon.
