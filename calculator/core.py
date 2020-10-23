import pandas as pd
import json
import logging
import time


def read_file(dir: [None, str], filename: str):
    """
    Read json file from local folder or with absolute path into pandas dataframe
    """
    if dir:
        filename = dir + filename
    try:
        return pd.read_json(filename)
    except ValueError as ve:
        logging.exception(ve.__repr__())
        raise FileNotFoundError(f"cannot read file {filename}")


def write_output(df: pd.DataFrame, dir: str, filename: str):
    """
    Write pandas dataframe into json file with given filename
    """
    if dir:
        filename = dir + filename
    try:
        df.to_json(filename, orient="index")
    except ValueError as ve:
        logging.exception(ve.__repr__())
        raise ValueError(f"can not write file {filename}")


def generate_summary(data: pd.DataFrame, input_filename):
    category_count = data.value_counts("BMI_Category").to_dict()

    return dict(
        input_file=input_filename,
        created_time=pd.Timestamp.now(),
        bmi_category_counts=category_count,
    )


def write_summary(summary: dict, dir: str, filename: str = "summary.json"):
    if dir:
        filename = dir + filename
    with open(filename, "w") as file:
        file.write(json.dumps(summary, indent=4, default=str))


def validate_config(config: pd.DataFrame) -> pd.DataFrame:
    """
    End must be smaller then next start for all values
    """
    if not ((config["start"].shift(-1).iloc[:-1] - config["end"].iloc[:-1]) > 0).all():
        raise ValueError("configuration: start and end limits are not correct")

    """
    Assumption: first value of start and last value of end are withing (0, 1000000) 
    """
    if not (config["start"].iloc[0] > 0 and config["end"].iloc[-1] < 1000000):
        raise ValueError(
            f"configuration: first and last limit must be between {0} and {1000}"
        )

    return config


def calculate_bmi(config: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    pdf = df.copy(deep=True)
    config = validate_config(config.sort_values("start"))

    cols = ["WeightKg", "HeightCm"]
    pdf[cols] = pd.to_numeric(pdf[cols].stack(), errors="coerce").unstack().fillna(0)
    pdf["BMI"] = pdf["WeightKg"] / (pdf["HeightCm"] / 100) ** 2

    bins = list(config["start"].values) + [config["end"].iloc[-1]]
    categories_risks = list(zip(config.bmi_category, config.health_risk))
    pdf["categories_risks"] = pd.cut(pdf["BMI"], bins=bins, labels=categories_risks)

    pdf.loc[
        (pdf["BMI"].isin([float("Inf"), float("-Inf")]) & pdf["BMI"] < 0), "BMI"
    ] = 0
    df[["BMI"]] = pdf[["BMI"]]
    df[["BMI_Category", "Health_Risk"]] = pd.DataFrame(
        pdf["categories_risks"].values.tolist(), index=pdf.index
    ).fillna("Not Applicable")

    return df


if __name__ == "__main__":
    """filenames to read and write"""
    data_dir = "../data/"
    config_filename = "config.json"
    input_filename = "input_benchmark.json"
    output_filename = "output.json"
    summary_filename = "summary.json"

    start = time.time()

    config = read_file(dir=None, filename=config_filename)
    input_data = read_file(dir=data_dir, filename=input_filename)
    df = calculate_bmi(config=config, df=input_data)
    summary = generate_summary(data=df, input_filename=input_filename)
    write_summary(summary=summary, dir=data_dir, filename=summary_filename)
    write_output(df=df, dir=data_dir, filename=output_filename)

    print(f"Total time: {time.time() - start} seconds")
