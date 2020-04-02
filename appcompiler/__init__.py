import argparse


# def create_parser():
#     parser = argparse.ArgumentParser(description='Compile shelley files')
#     parser.add_argument("src", metavar='source', help="Path to the input example yaml file")
#     parser.add_argument("name", metavar='name', help="Device name", nargs='?')
#     parser.add_argument("-u", "--uses", action='append', nargs=2, help="path to used device")
#     parser.add_argument("-o", "--outdir", nargs=1, help="path to store compiled files")
#     parser.add_argument("-b", "--binary", help="generate binary files", action='store_true')
#     return parser

def create_parser():
    parser = argparse.ArgumentParser(description='Compile shelley files')
    parser.add_argument("-v", "--verbosity", help="increase output verbosity",  action='store_true')
    parser.add_argument("-u", "--uses", nargs='*', default=[], help="path to used device")
    parser.add_argument("-o", "--outdir", help="path to store compiled files")
    parser.add_argument("-b", "--binary", help="generate binary files", action='store_true')
    parser.add_argument("-s", '--source', help="Path to the input example yaml file", required=True)
    return parser


def get_args() -> argparse.Namespace:
    return create_parser().parse_args()
