"""Module for scoring incoming inference requests."""
import json
import numpy as np
from sklearn.externals import joblib
from azureml.core.model import Model
from dateutil.parser import parse
from collections import OrderedDict
import traceback


def init():
    """Initialize the model in memory."""
    global model
    model_path = Model.get_model_path(model_name="Automl64103b10548245")
    # model_path = "model.pkl"
    model = joblib.load(model_path)


def run(rawdata):
    """Generate an inference for the request."""
    feature_dict = OrderedDict()
    features = [
        "start_month_int",
        "start_weekday_int",
        "floor_15",
        "floor_16",
        "floor_17",
        "floor_19",
        "start_month_str_April",
        "start_month_str_August",
        "start_month_str_December",
        "start_month_str_February",
        "start_month_str_January",
        "start_month_str_July",
        "start_month_str_June",
        "start_month_str_March",
        "start_month_str_May",
        "start_month_str_November",
        "start_month_str_October",
        "start_month_str_September",
        "start_weekday_str_Friday",
        "start_weekday_str_Monday",
        "start_weekday_str_Saturday",
        "start_weekday_str_Sunday",
        "start_weekday_str_Thursday",
        "start_weekday_str_Tuesday",
        "start_weekday_str_Wednesday",
        "half_of_month_first",
        "half_of_month_second",
        "quarter_Q1",
        "quarter_Q2",
        "quarter_Q3",
        "quarter_Q4",
    ]
    for f in features:
        feature_dict[f] = ""

    try:
        data = json.loads(rawdata)["data"]
        day = parse(data["day"])
        floor = data["floor"]

        feature_dict["start_month_int"] = day.month
        feature_dict["start_weekday_int"] = day.weekday()

        for fl in [f for f in feature_dict.keys() if "floor_" in f]:
            if int(fl.split("_")[-1]) == floor:
                feature_dict[fl] = 1
            else:
                feature_dict[fl] = 0

        month_name = day.strftime("%B")
        for mn in [f for f in feature_dict.keys() if "start_month_str_" in f]:
            if mn.split("_")[-1] == month_name:
                feature_dict[mn] = 1
            else:
                feature_dict[mn] = 0

        weekday_name = day.strftime("%A")
        for wdn in [f for f in feature_dict.keys() if "start_weekday_str_" in f]:
            if wdn.split("_")[-1] == weekday_name:
                feature_dict[wdn] = 1
            else:
                feature_dict[wdn] = 0

        month_half = "first" if day.day < 16 else "second"
        for mh in [f for f in feature_dict.keys() if "half_of_month_" in f]:
            if mh.split("_")[-1] == month_half:
                feature_dict[mh] = 1
            else:
                feature_dict[mh] = 0

        quarter = "Q{}".format(((day.month - 1) // 3) + 1)
        for q in [f for f in feature_dict.keys() if "quarter_" in f]:
            if q.split("_")[-1] == quarter:
                feature_dict[q] = 1
            else:
                feature_dict[q] = 0

        data = np.array([list(feature_dict.values())])
        result = model.predict(data)[0]
    except Exception as e:
        result = str(e)
        traceback.print_exc()
        return json.dumps({"error": result})
    return json.dumps({"result": result.tolist()})
