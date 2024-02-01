"""Command line interface."""

import argparse

from . import __version__


def main(argv=None):
    """Parse arguments and execute commands."""
    create_parser().parse_args(argv)


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-V",
        "--version",
        help="Show version number and exit",
        action="version",
        version=__version__,
    )
    return parser


if __name__ == "__main__":
    main()
