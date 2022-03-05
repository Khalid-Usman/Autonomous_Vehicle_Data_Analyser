import os
import sys
import shutil
import argparse
import pandas as pd
import plotly.express as px
from typing import Dict, List


def get_line_chart(data: Dict, x_legend: str, y_legend: str, title: str, height: int):
    """
    This function will plot a line graph using keys of dictionary (data) as x-axis and values as y-axis

    :param data: dictionary where keys are x-axis and values are y-axis
    :param x_legend: label of x-axis
    :param y_legend: label of y-axis
    :param title: title of figure
    :param height: height of figure
    """
    df = pd.DataFrame()
    df[x_legend] = list(data.keys())
    df[y_legend] = list(data.values())
    fig = px.line(df, x=x_legend, y=y_legend, template='plotly_dark', title=title, height=height)
    return fig


def get_bar_chart(data: Dict, x_legend: str, y_legend: str, title: str, height: int, width: float):
    """
    This function will plot a bar chart using keys of dictionary (data) as x-axis and values as y-axis

    :param data: dictionary where keys are x-axis and values are y-axis
    :param x_legend: label of x-axis
    :param y_legend: label of y-axis
    :param title: title of figure
    :param height: height of figure
    :param width: custom width of bar
    """
    df = pd.DataFrame()
    df[x_legend] = list(data.keys())
    df[y_legend] = list(data.values())
    fig = px.bar(df, x=x_legend, y=y_legend, template='plotly_dark', title=title, height=height)
    if width > 0:
        data["width"] = [width for _ in fig.data]
    return fig


def compute_threshold_based_frame_count(path: str):
    """
    This function will read scores from a file and generate dictionary, where keys are thresholds and values are number
    of frames against those thresholds.

    :param path: path of csv file
    """
    with open(path) as file:
        lines = file.readlines()
        x = [int(line.split(' ')[3]) for line in lines]
    maximum, data = max(x), {}
    for i in range(0, maximum + 2):
        y = list(filter(lambda score: score >= i, x))
        data[i] = len(y)
    line_chart = get_line_chart(data, x_legend='Threshold', y_legend='Number of Selected Frames',
                                title='Number of Selected Frames by Varying Threshold', height=500)
    return line_chart


def save_frames(pdp: str, frame_names: List, top: bool):
    """
    This function will move the selected frames to the relevant directories

    :param pdp: path of pdp folder
    :param frame_names: the dictionary where keys are frame numbers and values are frame names
    :param top: if true return frames with respect to top scores else bottom scores
    """
    for frame in frame_names:
        source_path = pdp + "/image_color/" + frame + ".png"
        target_path = pdp + "/Top/" if top else pdp + "/Bottom/"
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        if os.path.exists(target_path):
            shutil.copy(source_path, target_path)


def compute_top(target_path: str, path: str, top: int, ascending: bool):
    """
    This function will read scores from a file and generate dictionary, where keys are frame number and values are
    respective score.

    :param target_path: path of folder where you want to store images with highest/lowest score
    :param path: path of csv file, the out of data_selection pipeline
    :param top: top rank frames with respect to their score
    :param ascending: ascending True will return the bottom and ascending False will return top
    """
    df = pd.read_csv(path, sep=' ', header=None, usecols=[0, 2, 3])
    assert 0 < top < len(df.index), "enter a valid number"
    df.columns = ['frame_number', 'frame_name', 'frame_score']
    sub_df = df.sort_values('frame_score', ascending=ascending).head(top)
    data = dict(zip(sub_df['frame_number'], sub_df['frame_score']))
    frame_names = sub_df['frame_name'].to_list()
    save_frames(target_path, frame_names, True)
    bar_chart = get_bar_chart(data, x_legend='Selected Frame Number', y_legend='Score',
                              title='Top Ranked Frame'""'s Number and their corresponding Scores', height=500,
                              width=0.2)
    return bar_chart


def parse_args(sys_args: List[str]) -> argparse.Namespace:
    """
    This function parses the command line arguments.
    Parameters

    :param sys_args: Command line arguments
    :returns argparse namespace
    """
    parser = argparse.ArgumentParser(description='Execute data_analyses for showing data')
    parser.add_argument('--target_path', '-p', required=False, type=str, help='path to a target directory where you '
                                                                              'want to store Top/Bottom ranked images')
    parser.add_argument('--source_path', '-s', required=True, type=str, help='path of csv file that contains frames and'
                                                                             ' corresponding scores')
    parser.add_argument('--top', '-t', required=False, type=int, help='number of frames you want to see those having '
                                                                      'highest scores')
    parser.add_argument('--bottom', '-b', required=False, type=int, help='number of frames you want to see those having'
                                                                         ' lowest score')
    parser.add_argument('--output', '-o', required=True, type=str, help='path, where you want to save html file that '
                                                                        'contains all the graphs')
    return parser.parse_args(sys_args)


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    figs = []
    assert len(args.source_path) > 0 and os.path.exists(args.source_path), "source csv file not found!"
    assert len(args.output) > 0, "output path not found!"
    fig1 = compute_threshold_based_frame_count(args.source_path)
    fig2 = compute_top(args.target_path, args.source_path, args.top, ascending=False)
    fig3 = compute_top(args.target_path, args.source_path, args.bottom, ascending=True)
    figs.append(fig1)
    figs.append(fig2)
    figs.append(fig3)
    with open(args.output, 'a') as f:
        [f.write(fig.to_html(full_html=False, include_plotlyjs='cdn')) for fig in figs]
