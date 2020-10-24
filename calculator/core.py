import pandas as pd
import numpy as np
import json
import logging
import time
from pathlib import Path
import traceback

MIN_BMI = 0
MAX_BMI = 1000


class BaseCalculatorError(Exception):
    def __init__(self, *args, **kwargs):
        super(Exception, self).__init__(*args)
        self.ctx = kwargs
        logging.error(self.ctx.get("filepath"))
        logging.exception(traceback.format_exc())


class FileIOError(BaseCalculatorError):
    pass


class InvalidConfigError(BaseCalculatorError):
    pass


def read_file(filepath: str):
    """
    Read json file from local folder or with absolute path into pandas dataframe
    """
    file = Path(filepath)
    if not file.is_file():
        raise FileIOError("File does not exists.", filepath=filepath)

    try:
        return pd.read_json(filepath)
    except ValueError:
        raise FileIOError("Unable to read file.", filepath=filepath)


def generate_summary(data: pd.DataFrame, input_filename):
    category_count = data.value_counts("BMI_Category").to_dict()

    return dict(
        input_file=input_filename,
        created_time=str(pd.Timestamp.now()),
        bmi_category_counts=category_count,
    )


def write_output(df: pd.DataFrame, filepath: str):
    """
    Write pandas dataframe into json file with given filename
    """
    try:
        df.to_json(filepath, orient="index")
    except:
        raise FileIOError("Unable to write file.", filepath=filepath)


def write_summary(summary: dict, filepath: str):
    try:
        with open(filepath, "w") as file:
            file.write(json.dumps(summary, indent=4))
    except:
        raise FileIOError("Unable to write file.", filepath=filepath)


def validate_config(config: pd.DataFrame) -> pd.DataFrame:
    config = config.sort_values("start")
    config["current_start"] = config["start"].shift(-1)
    _config = config.dropna()
    """
    first value of start and last value validation
    """
    if not (config["start"].min() >= MIN_BMI and config["end"].max() < MAX_BMI):
        raise InvalidConfigError(
            f"start and end values must be within {MIN_BMI}, {MAX_BMI}."
        )

    if not _config["current_start"].eq(_config["end"]).all():
        raise InvalidConfigError("BMI ranges must be sequential.")

    return config.drop(columns=["current_start"])


def calculate_bmi(config: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    pdf = df.copy(deep=True)
    config = validate_config(config)

    cols = ["WeightKg", "HeightCm"]
    pdf[cols] = pd.to_numeric(pdf[cols].stack(), errors="coerce").unstack().fillna(0)
    pdf["BMI"] = (pdf["WeightKg"] / ((pdf["HeightCm"] / 100) ** 2)).round(2)

    bins = config["start"].values.tolist() + [config["end"].iloc[-1]]
    categories_risks = list(zip(config.bmi_category, config.health_risk))
    pdf["categories_risks"] = pd.cut(pdf["BMI"], bins=bins, labels=categories_risks)

    df[["BMI"]] = pdf[["BMI"]]

    df[["BMI_Category", "Health_Risk"]] = pd.DataFrame(
        pdf["categories_risks"].values.tolist(), index=pdf.index
    ).fillna("Not Applicable")
    df.loc[df["BMI"].isin([float("Inf"), float("-Inf"), np.nan]), "BMI"] = None

    return df
