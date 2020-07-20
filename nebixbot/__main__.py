import sys
import argparse
from argparse import RawTextHelpFormatter

from nebixbot.command_center.strategy_manager import StrategyManager


def main():
    """Project entry point function"""

    argparser = argparse.ArgumentParser(
        description="""\t« Nebix Trading Bot‌ »""",
        epilog="""    proudly developed by Nebix Team!\n\r""",
        prog='nebixbot',
        usage="""%(prog)s <command>""",
        formatter_class=RawTextHelpFormatter,
    )

    argparser.add_argument(
        '-sh',
        '--show-strategies',
        action='store_true',
    )

    argparser.add_argument(
        '-t',
        '--terminate',
        metavar='<strategy id>',
        action='store',
        type=str,
    )

    argparser.add_argument(
        '-r',
        '--run',
        metavar='<strategy id>',
        action='store',
        type=str,
    )

    try:
        args = argparser.parse_args()
        sm = StrategyManager()

        if args.show_strategies:
            sm.get_running_strategies()

        elif args.terminate:
            sm.terminate()

        elif args.run:
            sm.run()

    except argparse.ArgumentTypeError as arge:
        print('\n\nan argument error occured:', arge)
        print('enter "nebixbot -h" for help')
        sys.exit(1)


if __name__ == "__main__":
    main()
