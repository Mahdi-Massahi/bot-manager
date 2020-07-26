import sys
import argparse
from argparse import RawTextHelpFormatter

from nebixbot.other.tcolors import Tcolors
from nebixbot.command_center.strategy_manager import StrategyManager
from nebixbot.log.logger import delete_all_logs


def main():
    """Project entry point function"""

    argparser = argparse.ArgumentParser(
        description=f" «{Tcolors.HEADER} Nebix Trading" +
                    f"Bot‌ {Tcolors.ENDC}»",
        epilog=f"{Tcolors.WARNING} proudly developed by " +
               f"Nebix team{Tcolors.ENDC}\n\r",
        prog='nebixbot',
        usage="%(prog)s <command>",
        formatter_class=RawTextHelpFormatter,
    )

    argparser.add_argument(
        '-sh',
        '--show-strategies',
        action='store_true',
    )

    argparser.add_argument(
        '-shr',
        '--show-running-strategies',
        action='store_true',
    )

    argparser.add_argument(
        '-sht',
        '--show-terminated_strategies',
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

    argparser.add_argument(
        '-oo',
        '--only-output',
        action='store_true',
        help='only return results - no sugar-coating'
    )

    argparser.add_argument(
        '--delete-all-logs',
        action='store_true',
        help='delete all logfiles'
    )

    try:
        args = argparser.parse_args()
        sm = StrategyManager()

        only_output = False
        if args.only_output:
            only_output = True

        if args.show_strategies:
            strategies = sm.return_available_strategies()
            if strategies:
                if only_output:
                    print(strategies)
                else:
                    print(
                        f"{Tcolors.HEADER}Available Strategies:" +
                        f"{Tcolors.ENDC}"
                    )
                    for strategy_name in strategies.keys():
                        print(
                            f'\t- {Tcolors.BOLD}{strategy_name}' +
                            f'{Tcolors.ENDC}:',
                            strategies[strategy_name]
                        )
            else:
                if only_output:
                    print(strategies)
                else:
                    print(
                        f"\t{Tcolors.BOLD}No available strategies" +
                        f"{Tcolors.ENDC}"
                    )

        elif args.show_running_strategies:
            running, _ = sm.return_running_strategies()
            if not only_output:
                print(f"{Tcolors.HEADER}Running Strategies:{Tcolors.ENDC}")
            if running:
                if only_output:
                    print(running)
                else:
                    print(
                        '\tformat: <unique id>:' +
                        '[<pid>, <strategy name>, <start date/time>]'
                    )
                    for strategy in running:
                        id = strategy[0]
                        details = strategy[1]
                        print(
                            f'\t{Tcolors.BOLD}* {id}{Tcolors.ENDC}:' +
                            f'{details}'
                        )
                        print(
                            f'\t\t{Tcolors.OKGREEN}is running' +
                            f'{Tcolors.ENDC}\n'
                        )
            else:
                if only_output:
                    print(running)
                else:
                    print(
                        f"\t{Tcolors.BOLD}No running strategies" +
                        f"{Tcolors.ENDC}"
                    )

        elif args.show_terminated_strategies:
            _, dead = sm.return_running_strategies()
            if not only_output:
                print(f"{Tcolors.HEADER}Terminated Strategies:{Tcolors.ENDC}")
            if dead:
                if only_output:
                    print(dead)
                else:
                    print(
                        '\tformat: <unique id>:' +
                        '[<pid>, <strategy name>, <start date/time>]'
                    )
                    for strategy in dead:
                        id = strategy[0]
                        details = strategy[1]
                    print(
                        f'\t{Tcolors.BOLD}* {id}{Tcolors.ENDC}:' +
                        f'{details}'
                    )
                    print(f'\t\t{Tcolors.FAIL}is terminated{Tcolors.ENDC}\n')
            else:
                if only_output:
                    print(dead)
                else:
                    print(
                        f"\t{Tcolors.BOLD}No terminated strategies" +
                        f"{Tcolors.ENDC}"
                    )

        elif args.terminate:
            id = args.terminate
            if sm.strategy_id_exists(id):
                result = sm.terminate(id)
                if only_output:
                    print(result)
                else:
                    if result:
                        print(
                            f'{Tcolors.OKGREEN}' +
                            f'Successfully terminated strategy{Tcolors.ENDC}'
                        )
                    else:
                        print(
                            f'{Tcolors.FAIL}' +
                            f'Failed to terminate strategy{Tcolors.ENDC}'
                        )
            else:
                if only_output:
                    print(False)
                else:
                    print(f'Failed to terminate - id:{id} not found')

        elif args.run:
            name = args.run
            if name in sm.strategies:
                result = sm.run(name)
                if only_output:
                    print(result)
                else:
                    if result:
                        print(
                            f"{Tcolors.OKGREEN}Successfully ran {name}" +
                            f"{Tcolors.ENDC}"
                        )
                    else:
                        print(
                            f"{Tcolors.FAIL}Failed to ran {name}" +
                            f"{Tcolors.ENDC}"
                        )

            else:
                print('Error: enter a valid strategy name')

        elif args.delete_all_logs:
            result = delete_all_logs()
            if only_output:
                print(result)
            else:
                if result:
                    print(
                        f"{Tcolors.OKGREEN}Successfully deleted all logfiles" +
                        f"{Tcolors.ENDC}"
                    )
                else:
                    print(
                        f"{Tcolors.FAIL}Failed to delete logfiles" +
                        f"{Tcolors.ENDC}"
                    )

        else:
            argparser.print_help()

    except argparse.ArgumentTypeError as arge:
        print(
            f'\n\n{Tcolors.FAIL}an argument error occured:{Tcolors.ENDC}',
            arge
        )
        print('enter "nebixbot -h" for help')
        sys.exit(1)


if __name__ == "__main__":
    main()
