### Layout-Generator-Assignment
========================================================------------===================================================
img width="1919" height="1077" alt="Screenshot 2026-01-15 025416" src="https://github.com/user-attachments/assets/fe700f18-5d2e-4f25-989a-ba1554aa167c" 
------------------============---------------------------------------------------
### 📋 Features
---------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------
* **Procedural Generation:** Generates random layouts of **Type A** (30x20m) and **Type B** (20x20m) buildings.
* **Constraint Logic:**
    * **Overlap Detection:** Ensures buildings do not overlap with each other or the central Plaza.
    * **Proximity Rules:** Enforces "Rule 4" (Type A buildings must be within 60m of a Type B building).
* **Evolutionary Learning:**
    * **Mutation:** Uses previously successful layouts ("parents") to generate new variations.
    * **Negative Reinforcement:** Tracks "Bad Spots" (coordinates where placement frequently fails) to optimize future generation speeds.
* **Blueprint Visualization:** Uses `Matplotlib` to render professional-grade architectural diagrams with dimension lines, gap measurements, and error indicators.
* **Interactive GUI:**
    * Infinite panning and zooming canvas.
    * Searchable batch history.
    * Right-click context menu to save high-resolution blueprint images.
------------------------------------------------------------------------------------
=====================================================================================
### Deployment
Install Python on your system.
Install the required libraries: Tkinter, Matplotlib, and Pillow.
-----------------------------------------------------------------------------
------------------------------------------------------------------------------
## Usage
Launch the App: The application will immediately generate the first batch of 4 layouts.
Generate New: Click the GENERATE NEW button in the top toolbar to create a new batch. The system attempts to create valid layouts; if a layout fails constraints, it is marked as INVALID in red.
**Navigation:**
**Pan:** Click and drag anywhere on the canvas.
**Zoom:** Use the Mouse Wheel (or trackpad scroll) to zoom in and out.
**Saving Images:**
Select a batch from the sidebar list.
Right-click on the list item and select "Save as Image..." to export the high-res PNG.
Data Persistence: The app automatically creates a data/ directory to store JSON logs of correct and failed attempts, which allows the algorithm to "learn" over time.
---------------------------------------=============--------------------------============--------------------------==========------------------------===============---------
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
### Performance & Optimization
**Note: This application was developed and tested on a personal computer where it runs smoothly. However, the code has not yet been fully optimized.**
As the "Infinite Canvas" and the layout generation algorithm (which involves heavy iterative constraint checking) can be resource-intensive, performance may vary on systems with lower specifications.
**Test System Configuration: The application was verified to run without issues on the following hardware:**
Processor: AMD Ryzen 9
Memory: 32 GB RAM
Storage: 1 TB SSD

=============================----------------=================================================---------------------------------======================-----------=============--------------------------------================-----------------------------------------------================================-----------------------=============------------
## File Structure
├── main.py              # The core application script
├── data/                # Auto-generated data folder
│   ├── correct/         # JSON files of valid layouts
│   ├── failed/          # JSON files of invalid layouts
│   └── bad_spots.json   # Learned coordinates of difficult areas
└── README.md
