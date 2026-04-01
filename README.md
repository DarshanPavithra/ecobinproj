# ECO BIN

## Problem Statement

Waste mismanagement is a global crisis, often stemming from a lack of knowledge at the point of disposal. Many people want to recycle or compost but are frequently confused by which item goes into which bin, leading to contaminated recycling streams and overflowing landfills. Furthermore, there is often no immediate incentive or feedback for individuals to practice proper waste segregation.

---

## Project Description

**ECO BIN** is a polished, interactive kiosk-style application designed to revolutionize community waste sorting. By combining computer vision with a gamified user experience, it removes the guesswork from disposal and encourages sustainable habits through engagement.

### How it Works:
Users capture or upload a photo of their waste item at the kiosk. The system instantly analyzes the object and identifies the correct bin: 
* 🟢 **Green Bin:** Composting (Food, fruits, vegetables, plants)
* 🔵 **Blue Bin:** Recycling (Plastics, glass, paper, bottles, cans)
* 🔴 **Red Bin:** E-Waste (Electronics, batteries, devices)
* 🟡 **Yellow Bin:** Landfill (General waste and unknown items)

### Why it’s Useful:
The application features a **point-based reward system** and an **interactive leaderboard** to incentivize users. For administrators, a live dashboard monitors bin capacities and provides alerts when a bin is near full, optimizing the waste collection process and preventing overflow.

---

## Google AI Usage

### Tools / Models Used
* **Google Cloud Vision API**

### How Google AI Was Used
The core intelligence of ECO BIN is powered by the **Google Cloud Vision API**. When a user submits an image, the application sends the data to Google’s vision models, which return descriptive labels for the object. The application then scans these labels against predefined keyword sets for Green, Blue, and Red bins to determine the classification. This allows for robust, real-time object detection without the need for a complex, locally-trained model.

---

## Proof of Google AI Usage

Attach screenshots in a `/proof` folder:
* [AI Proof](proof/ai_vision_results.png)

---

## Screenshots

Add project screenshots:
![Screenshot1](PICS/dashboard_preview.png)
![Screenshot2](PICS/bin_actuation.png)

---

## Demo Video

Upload your demo video to Google Drive and paste the shareable link here(max 3 minutes). [Watch Demo](https://your-google-drive-link-here)

---

## Installation Steps

```bash
# Clone the repository
git clone [https://github.com/DarshanPavithra/ecobin.git](https://github.com/DarshanPavithra/ecobin.git)

# Go to project folder
cd ecobin

# Install dependencies
pip install streamlit pandas tinydb google-cloud-vision streamlit-js-eval

# Run the project
streamlit run app.py
