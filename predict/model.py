import numpy as np
from joblib import load
import pickle
import os
import sys
import sklearn
import pandas as pd

def predict(input, loaded_model):
    result = loaded_model.predict(input)
    result = float(result)
    result = np.exp(result) - 1
    return result

# Help function
def parse_float(x):
    if (x == ''):
        return 0
    else:
        return float(x)

def parse_bedroom(bedroom, area):
    if(bedroom == ''):
        knn_bedroom = joblib.load('bathroom_model.sav')
        area = np.array(area)
        area = area.reshape(-1, 1)
        bedroom_pred = knn_bedroom.predict(area)
        bedroom = float(bedroom_pred[0])
    return bedroom

def parse_bathroom(bathroom,  area):
    if(bathroom == ''):
        knn_bathroom = joblib.load('bathroom_model.sav')
        area = np.array(area)
        area = area.reshape(-1, 1)
        bathroom_pred = knn_bathroom.predict(area)
        bathroom = float(bathroom_pred[0])
    return bathroom

# Main function
if __name__ == "__main__":
    # Get arguments
    _, pool, skyview, bedroom, bathroom, area, lat, lon, legal, feature, district, ward, project, balcony = sys.argv

    # Set folder which containt models
    MODEL_FOLDER = os.path.join(os.getcwd(), 'predict')

    # Set model 
    model_path = os.path.join(MODEL_FOLDER, 'rf.joblib')
    # model_path = os.path.join(MODEL_FOLDER, 'lgb.joblib')
    model_path = os.path.join(MODEL_FOLDER, 'gbr.joblib')
    # model_path = os.path.join(MODEL_FOLDER, 'stack_gen.joblib')
    
    # Set others
    dict_path = os.path.join(MODEL_FOLDER, 'name_dict.pickle')
    lon_sc_path = os.path.join(MODEL_FOLDER, 'lon_scaler.bin')
    lat_sc_path = os.path.join(MODEL_FOLDER, 'lat_scaler.bin')

    # Parse arguments
    area = parse_float(area)
    #bathroom = parse_float(bathroom)
    #bedroom = parse_float(bedroom)
    bedroom = parse_bedroom(bedroom, area)
    bathroom  = parse_bathroom(bathroom, area)

    # Initialize input model
    input = np.zeros((1, 450))
    # Load dictionary
    with open(dict_path, 'rb') as f:
        dictionary = pickle.load(f)
    # Convert attribute to input
    if (pool == 'Có'):
        input[:, 0] = 1
    if (skyview == 'Có'):
        input[:, 1] = 1
    input[:, 2] = bedroom
    input[:, 3] = bathroom
    input[:, 4] = np.log1p(area)
    # Load standard scaler
    input[:, 5] = float(load(lat_sc_path).transform([[lat]]))
    input[:, 6] = float(load(lon_sc_path).transform([[lon]]))

    for opt in legal:
        if opt in dictionary:
            input[:, dictionary[opt]] = 1

    for opt in feature:
        if (opt in dictionary):
            input[:, dictionary[opt]] = 1

    district = 'district_' + district
    if (district in dictionary):
        input[:, dictionary[district]] = 1

    ward = 'ward_' + ward.lower()
    if (ward in dictionary):
        input[:, dictionary[ward]] = 1

    project = 'project_‘' + project + '’'
    if (project in dictionary):
        input[:, dictionary[project]] = 1

    for opt in balcony:
        if ((opt == 'Đông') | (opt == 'Đông Nam') | (opt == 'Nam') | (opt == 'Bắc')):
            input[:, dictionary['balcony.dong_tu_trach']] = 1
        if ((opt == 'Tây') | (opt == 'Đông Bắc') | (opt == 'Tây Nam') | (opt == 'Tây Bắc')):
            input[:, dictionary['balcony.tay_tu_trach']] = 1

    # Load model
    loaded_model = load(model_path)

    # Predict
    dataToSendBack = predict(input, loaded_model)

    # Send data
    print(dataToSendBack)
    sys.stdout.flush()
