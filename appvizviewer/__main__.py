import logging
import yaml
import sys
import os
import argparse

from .context import shelley

from shelley.automata.view import automaton2dot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_parser():
    parser = argparse.ArgumentParser(description='Vizualize compiled files as state diagrams')
    parser.add_argument("-o", "--outdir", help="path to dot files")
    parser.add_argument("-f", "--outformat", help="output format (pdf, png, svg, ...)")
    parser.add_argument("-p", "--outprint", help="print output for xdot", action='store_true')
    parser.add_argument("-i", '--input', help="Path to the compiled yaml file (.scy or .scb)", required=True)
    return parser


def save_and_view_graph(infilepath, outfilepath, outformat, outprint=False):
    with open(infilepath, 'r') as f:
        d = yaml.load(f, Loader=yaml.FullLoader)
    dot = automaton2dot(d)
    if outformat is not None:
        dot.format = outformat
    dot.render(outfilepath, view=False)
    if outprint:
        print(dot)


def main(args):
    filepath = os.path.realpath(args.input)  # --device
    basedir = os.path.dirname(filepath)
    filename = os.path.basename(filepath)

    if args.outdir is None:
        outdir = basedir
    else:
        outdir = args.outdir
    outfilepath = os.path.join(outdir, '{0}.gv'.format(filename))

    save_and_view_graph(filepath, outfilepath, args.outformat, args.outprint)


if __name__ == "__main__":
    main(create_parser().parse_args())
