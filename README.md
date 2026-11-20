# Python_Final_module_Project
## Solar Yield Estimator
A web app that estimates monthly and yearly solar energy output for any place, from its name. current version active from: November 20, 2026
Created By Roselyne Makau

## Description

Solar Yield Estimator helps you find out how much electricity a solar panel system is likely to produce. You type a place name (a town, school, or landmark), enter the system size, panel tilt, direction and expected losses, and the app does the rest:

- It converts the place name into latitude and longitude using OpenStreetMap's Nominatim service.
- It sends the location and system details to PVGIS, a free solar estimation service, and receives the estimated energy output.
- It saves the inputs and results to a local SQLite database, so every calculation can be viewed, updated, deleted, or downloaded later.

The app is built with Streamlit and has four tabs: New system, View results, Update, and Delete.

## Features
- Search by place name.No need to look up coordinates by hand.
- Solar yield estimates from PVGIS. Get the estimated energy per year, the average per day, the best and weakest months, and a month-by-month table.
- Saved history. Every calculation is stored in SQLite, with the inputs and the 12 monthly results kept in two linked tables.
- View inputs and full results. Choose any saved system to see everything about it in one place.
- Update a system. Change the place, size, tilt, direction, or losses and the results are recalculated automatically. T
- Delete with confirmation. Removing a system also removes its monthly results, and needs a tick in a confirmation box first.
- Export to JSON or CSV. Download any system's inputs and results as a file.
- Friendly error handling. An unknown location, a lost connection, or an unexpected reply from a service shows a clear message instead of crashing the app.

## Setup/Installation Requirements

You do not need to run a separate server or set up the database by hand. The app starts its own local web server, and the database file is created automatically the first time it runs.

Requirements: Python 3.10 or newer, and an internet connection (the app calls two free online services).

1. Get the project (clone it or download the folder) and open a terminal inside it.
2. Create a virtual environment :python -m venv .venv
3. Activate the virtual environment  :source .venv/Scripts/activate
4. Install the dependencies : pip install -r requirements.txt
5. Run the app : streamlit run UI.py


## Using the app
1. New system: enter your name, a location, the system size, tilt, direction, and losses, then select Calculate and save.
2. View results: choose a saved system to see its inputs, results, and monthly table. Use the download buttons for JSON or CSV.
3. Update: change any input and select Recalculate and update. If you leave the place text unchanged, the saved coordinates are reused.
4. Delete: choose a system, tick the confirmation box, and select Delete.

## Troubleshooting
- Lots of missing ScriptRunContext warnings and no page opens: run the app with streamlit run UI.py, not python app.py.
- ModuleNotFoundError: activate the virtual environment, then run the install command again.
- SyntaxError: source code string cannot contain null bytes inside numpy: the virtual environment is corrupted. Delete .venv, create a new one, and reinstall. Keeping the project outside synced folders such as OneDrive or the Desktop helps prevent this.
- 400 Bad Request from Nominatim: check the User-Agent line in api.py. The header name needs a hyphen and the email should be real.

## Known Bugs
- Small or unmapped places may not be found. Nominatim can only find places listed in OpenStreetMap, and a school or landmark may not be there under the exact name you type. Workaround: add the town and country, or search for a nearby town.
- The page may return to the first tab after some actions. Streamlit sometimes resets the selected tab when the page refreshes. Workaround: click the tab you want again. After saving a new system, the other tabs already open on it.
- Saving does not switch tabs automatically. After a calculation is saved, select View results yourself.
- Results are estimates, not guarantees. They come from historical solar radiation data for a fixed-tilt system. - Real output depends on shading, equipment and weather.
- Nominatim is a shared free service. Avoid sending many searches in quick succession, or it may refuse requests for a while.
- The username is only a label. There are no accounts or passwords, and anyone who opens the app can view, update, or delete any saved system.
- The database is a local file, so data is not shared between computers.

## Technologies Used
Python 3 for all of the application code
Streamlit for the web interface (tabs, forms, and download buttons)
SQLite (through Python's built-in sqlite3 module) for storing systems and monthly results
pandas for organising the monthly results into tables and building the CSV export
requests for calling the web services
PVGIS API (European Commission Joint Research Centre) for solar energy estimates
Nominatim API (OpenStreetMap) for turning place names into coordinates
JSON and CSV for exporting results
## Support and contact details

If you run into a problem, have a question, or want to suggest an improvement, please get in touch at makaurozy@gmail.com or MakauRozy GitHub profile. Contributions are welcome: fork the project, make your change, and open a pull request. Ideas for future work include charts for the monthly output, a tab to compare systems side by side, PDF or Excel reports, and support for batteries and electricity costs.

Place search data is © OpenStreetMap contributors. Solar estimates come from PVGIS, a service of the European Commission Joint Research Centre.

## License

This project is licensed under the MIT License.

Copyright (c) 2026 Roselyne Makau
