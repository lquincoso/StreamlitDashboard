Capstone 1 - Group 8 Summer 2024

Project Title: L.A. Crime Streamlit Dashboard

Team 8 Members:
	- Lorena A. Quincoso Lugones
	- Niccholas Tim Reiz
	- Ariel Ramos Perez
	- Mauricio Piedra
	- Gabriel Andres Prieto

Code Directory Structure:

	+ Folder: LACrimeDashbooard
		+ Folder: jupyter notebook - ML training and testing
			+ Current ML Model.ipynb
		+ Folder: models 
			+ feature_columns.pkl
			+ knn_model.pkl
		+ Crime_Data_from_2020_to_Present.csv
		+ dashboard.py
		+ style.css
		+ requirements.txt

Explanation:

- "Folder: jupyter notebook - ML training and testing":

	- "Current ML Model.ipynb": Contains comprehensive code for training and saving the model and column features for display.

- "Folder: models": The folder containing the necessary Machine Learning algorithms that run for the "Predictive Model" dashboard feature.

	- "feature_columns.pkl"

	- "knn_model.pkl"

- "Crime_Data_from_2020_to_Present.csv": The csv file that contains the crime data in L.A. from 2020-2024.

- "dashboard.py":  The python file contains the code for the program to run.

- "style.css": The CSS file that is used to change the font of the Streamlit dashboard.

- "requirements.txt": The txt file entailing the necessary imports for the python file.


User Guide:

1. Import the files from the LACrimeDashboard into any prefered code editor like VSC or PyCharm.
2. Ensure that all the necessary imports in "dashboard.py" are installed. Most importantly, ensure the following by typing on the terminal: 'pip install streamlit-folium' and 'pip install streamlit-option-menu'.
3. Follow the Model Instructions (found below).
4. To run the Streamlit app, open the IDE terminal and enter: "streamlit run dashboard.py". This will open a local host website in your browser.
5. Since there is a lot of data, the program will take some time to load. Notably, the predictive model will take some time since it is a strenuous process. 
6. Interact with the data!


Model Instructions:

3.1: Run the Jupyter Notebook under 'jupyter notebook - ML training and testing' folder in order to see the training/testing model on the dataset, and also to save the model. Save it under the folder 'models' (the streamlit app will crash otherwise).
3.2: Access if possible to the Command Prompt (Commander from Anaconda Navigator is recommended), and type: 'pip install streamlit-folium' if you don't have the package installed already on your system.
3.3: Through the same Prompt, 'cd' to the downloaded folder.
3.4: Ensure the dependencies are installed by typing on the Prompt: 'pip install -r requirements.txt'.


================================================================================================

Python Packages:

streamlit
pandas
joblib
scikit-learn
imblearn
StringIO
requests
altair
dask.dataframe
plotly.express

