from .core import (
    read_file,
    calculate_bmi,
    write_output,
    write_summary,
    generate_summary,
)
import argparse


def run(
    input_filename: str,
    output_filename: str,
    summary_filename: str,
    config_filename: str,
):
    if config_filename is None:
        config_filename = "config.json"

    config = read_file(filepath=config_filename)
    input_data = read_file(filepath=input_filename)
    df = calculate_bmi(config=config, df=input_data)
    summary = generate_summary(data=df, input_filename=input_filename)
    write_summary(summary=summary, filepath=summary_filename)
    write_output(df=df, filepath=output_filename)


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="PROG",
        usage="%(prog)s [OPTION] [FILE]...",
        description="Calculate body mass index",
    )
    parser.add_argument("-cf", "--config_filepath", type=str, required=False)
    parser.add_argument("-input", "--input_filepath", type=str, required=True)
    parser.add_argument("-output", "--output_filepath", type=str, required=True)
    parser.add_argument("-summary", "--summary_filepath", type=str, required=True)
    return parser


def main():
    args = init_argparse().parse_args()
    input_filename = args.input_filepath
    output_filename = args.output_filepath
    summary_filename = args.summary_filepath
    if "config_filepath" in args:
        config_filename = args.config_filepath
    else:
        config_filename = None
    run(
        input_filename=input_filename,
        output_filename=output_filename,
        summary_filename=summary_filename,
        config_filename=config_filename,
    )
