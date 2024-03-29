import argparse
import os
import sys
from typing import Dict, List
import pandas as pd
import plotly.express as px


def get_combine_line_chart(data: Dict, x_legend: str, y_legend: str, target_class: str, title: str, height: int):
    """
    This function will plot a line graph using keys of dictionary (data) as x-axis and values as y-axis

    :param data: a list of dictionaries where keys are x-axis and values are y-axis
    :param x_legend: label of x-axis
    :param y_legend: label of y-axis
    :param target_class: class for distribution
    :param title: title of figure
    :param height: height of figure
    """
    df = pd.DataFrame(columns=[x_legend, y_legend, target_class])
    for k, v in data.items():
        x, y = list(v.keys()), list(v.values())
        target = [k[:-4]] * len(x)
        temp_df = pd.DataFrame({x_legend: x, y_legend: y, target_class: target})
        df = pd.concat([df, temp_df], axis=0)
    fig = px.line(df, x=x_legend, y=y_legend, color=target_class, template='plotly_dark', title=title, height=height)
    return fig


def combine_multiple_line_graphs(path: str) -> Dict:
    """
    This function will read scores from a file and generate a dictionary of dictionaries, where keys are csv names and
    values are dictionaries, where keys are thresholds and values are number of frames against those thresholds.

    :param path: path of csv file
    :return pdp_data: a dictionary of dictionaries
    """
    pdp_data = {}
    assert len(os.listdir(path)) > 1, "This function requires at-least two csv to compare!"
    for sub_csv in os.listdir(path):
        df = pd.read_csv(os.path.join(path, sub_csv), sep=' ', header=None, usecols=range(0, 4))
        df.columns = ['frame_number', 'pdp_name', 'frame_name', 'score']
        x = df['score'].tolist()
        maximum, data = max(x), {}
        for i in range(0, maximum + 2):
            y = list(filter(lambda score: score >= i, x))
            data[i] = len(y)
        pdp_data[sub_csv] = data
    return pdp_data


def parse_args(sys_args: List[str]) -> argparse.Namespace:
    """
    This function parses the command line arguments.
    Parameters

    :param sys_args: Command line arguments
    :returns argparse namespace
    """
    parser = argparse.ArgumentParser(description='Execute data_visualization for showing data')
    parser.add_argument('-path', '-p', required=True, type=str, help='path of folder that contains more than 1 csv '
                                                                     'files generated by data_selection pipeline')
    return parser.parse_args(sys_args)


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    combine_data = combine_multiple_line_graphs(args.path)
    combine_fig = get_combine_line_chart(combine_data, x_legend='Threshold', y_legend='Number of Selected Frames',
                                         target_class="pdps", title='Number of Selected Frames by Varying Threshold for'
                                                                    ' Multiple Pdps', height=500)
    combine_fig.show()
