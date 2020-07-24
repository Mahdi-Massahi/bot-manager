import sys
import argparse
from argparse import RawTextHelpFormatter

from nebixbot.other.tcolors import Tcolors
from nebixbot.command_center.strategy_manager import StrategyManager


def main():
    """Project entry point function"""

    argparser = argparse.ArgumentParser(
        description=f""" «{Tcolors.HEADER} Nebix Trading Bot‌ {Tcolors.ENDC}»""",
        epilog=f"""{Tcolors.WARNING} proudly developed by """ +
         f"""Nebix team{Tcolors.ENDC}\n\r""",
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
            sm.print_running_strategies()
            sm.print_available_strategies()

        elif args.terminate:
            id = args.terminate
            if sm.strategy_id_exists(id):
                if sm.terminate(id):
                    print(
                        f'{Tcolors.OKGREEN}' +
                        f'Successfully terminated strategy{Tcolors.ENDC}'
                    )
                else:
                    print(
                        f'{Tcolors.FAIL}' +
                        f'Failed to terminate strategy{Tcolors.ENDC}'
                    )

        elif args.run:
            name = args.run
            if name in sm.strategies:
                sm.run(name)
            else:
                print('Enter a valid strategy name')

        else:
            argparser.print_help()

    except argparse.ArgumentTypeError as arge:
        print('\n\nan argument error occured:', arge)
        print('enter "nebixbot -h" for help')
        sys.exit(1)


if __name__ == "__main__":
    main()
