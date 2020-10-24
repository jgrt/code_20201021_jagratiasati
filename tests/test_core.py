from calculator.core import (
    calculate_bmi,
    read_file,
    write_summary,
    write_output,
    validate_config,
    generate_summary,
    FileIOError,
    InvalidConfigError,
    MIN_BMI,
    MAX_BMI,
)
import pytest
import json
import pandas as pd
import os


@pytest.fixture
def base_path():
    print("f")
    return f"{os.path.dirname(os.path.realpath(__file__))}/data"


@pytest.fixture
def config(base_path):
    return pd.read_json(os.path.join(base_path, "config.json"))


def test_read_file_valid(base_path):
    filepath = os.path.join(base_path, "config.json")

    df = read_file(filepath=filepath)

    assert not df.empty
    assert df.shape == (6, 4)


def test_read_file_non_existing(base_path):
    filepath = os.path.join(base_path, "test.json")

    with pytest.raises(FileIOError) as fe:
        read_file(filepath=filepath)

    assert fe.value.ctx.get("filepath") == filepath
    assert fe.value.args[0] == "File does not exists."


def test_read_file_incorrect_format(base_path):
    filepath = os.path.join(base_path, "testcases.csv")

    with pytest.raises(FileIOError) as fe:
        read_file(filepath=filepath)

    assert fe.value.ctx.get("filepath") == filepath
    assert fe.value.args[0] == "Unable to read file."


def test_generate_summary(base_path, config):
    input_filename = "input.json"
    input_data = pd.read_json(os.path.join(base_path, input_filename))

    df = calculate_bmi(config=config, df=input_data)
    summary = generate_summary(data=df, input_filename=input_filename)
    category_count = df.value_counts("BMI_Category").to_dict()

    assert summary, "Empty summary."
    assert summary.get("input_file") == input_filename
    assert "bmi_category_counts" in summary
    assert summary.get("bmi_category_counts")
    assert summary.get("bmi_category_counts") == category_count


def test_write_output_invalid_format():
    data = dict(a=[1, 2, 3], b=["a", "b", "c"])

    with pytest.raises(FileIOError) as fe:
        write_output(data, "test.json")

    assert fe.value.args[0] == "Unable to write file."


def test_write_summary_invalid_format():
    data = pd.DataFrame([[1, 2, 3], ["a", "b", "c"]])

    with pytest.raises(FileIOError) as fe:
        write_summary(data, "test.json")

    assert fe.value.args[0] == "Unable to write file."


def test_validate_config_invalid_limits(base_path):
    config = pd.read_json(os.path.join(base_path, "config_test_limit.json"))

    with pytest.raises(InvalidConfigError) as ice:
        validate_config(config)

    assert (
        ice.value.args[0]
        == f"start and end values must be within {MIN_BMI}, {MAX_BMI}."
    )


def test_validate_config_discontinues_ranges(base_path):
    config = pd.read_json(os.path.join(base_path, "config_break_ranges.json"))

    with pytest.raises(InvalidConfigError) as ice:
        validate_config(config)

    assert ice.value.args[0] == "BMI ranges must be sequential."


def pipeline(base_path, config, input_filename, output_filename):
    input_data = pd.read_json(os.path.join(base_path, input_filename))
    df = calculate_bmi(config, input_data[["Gender", "WeightKg", "HeightCm"]])
    df.to_json(output_filename, orient="records")


def test_create_file(base_path, config, tmpdir):
    p = tmpdir.mkdir("temp").join("output.json")
    input_filename = "testcase.json"
    pipeline(base_path, config, input_filename, p)

    with open(os.path.join(base_path, input_filename)) as f:
        input_data = json.load(f)

    with open(p) as f:
        output_data = json.load(f)

    assert len(input_data) == len(output_data), "Mismatch patients"

    for inp, out in zip(input_data, output_data):
        description = inp.pop("Description")
        assert inp == out, description
