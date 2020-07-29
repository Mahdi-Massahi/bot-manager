"""Nebixbot entrypoint"""

import sys
import argparse
from argparse import RawTextHelpFormatter
import threading
import time
import os

from nebixbot.other.tcolors import Tcolors
from nebixbot.command_center.strategy_manager import StrategyManager
from nebixbot.log.logger import delete_all_logs, get_logs_dir


def main():
    """Project entry point function"""

    argparser = argparse.ArgumentParser(
        description=f" «{Tcolors.HEADER} Nebix Trading Bot‌ {Tcolors.ENDC}»",
        epilog=(
            f"{Tcolors.WARNING} proudly developed by"
            f" Nebix team{Tcolors.ENDC}\n\r"
        ),
        prog="nebixbot",
        usage="%(prog)s <command(s)>",
        formatter_class=RawTextHelpFormatter,
    )

    argparser.add_argument(
        "-sh", "--show-strategies", action="store_true",
    )

    argparser.add_argument(
        "-shr", "--show-running-strategies", action="store_true",
    )

    argparser.add_argument(
        "-sht", "--show-terminated-strategies", action="store_true",
    )

    argparser.add_argument(
        "-r", "--run", metavar="<strategy name>", action="store", type=str,
    )

    argparser.add_argument(
        "-t", "--terminate", metavar="<strategy id>", action="store", type=str,
    )

    argparser.add_argument(
        "-oo",
        "--only-output",
        action="store_true",
        help="only return results (no sugar-coating)",
    )

    argparser.add_argument(
        "-shld",
        "--show-logs-dir",
        action="store_true",
        help="show logfiles directory",
    )

    argparser.add_argument(
        "--delete-all-logs", action="store_true", help="delete all logfiles"
    )

    try:
        args = argparser.parse_args()
        strategy_manager = StrategyManager()

        if args.show_strategies:
            strategies = strategy_manager.return_available_strategies()
            if strategies:
                if args.only_output:
                    print(strategies)
                else:
                    print(
                        f"{Tcolors.HEADER}Available Strategies:"
                        + f"{Tcolors.ENDC}"
                    )
                    for strategy_name in strategies:
                        print(
                            f"\t- {Tcolors.BOLD}{strategy_name}"
                            + f"{Tcolors.ENDC}:",
                            strategies[strategy_name],
                        )
            else:
                if args.only_output:
                    print(strategies)
                else:
                    print(
                        f"\t{Tcolors.BOLD}No available strategies"
                        + f"{Tcolors.ENDC}"
                    )

        elif args.show_running_strategies:
            running, _ = strategy_manager.return_running_strategies()
            if not args.only_output:
                print(f"{Tcolors.HEADER}Running Strategies:{Tcolors.ENDC}")
            if running:
                if args.only_output:
                    print(running)
                else:
                    print(
                        "\tformat: <unique id>:"
                        + "[<pid>, <strategy name>, <start date/time>]"
                    )
                    for strategy in running:
                        details = strategy[1]
                        print(
                            f"\t{Tcolors.BOLD}* {strategy[0]}{Tcolors.ENDC}:"
                            + f"{details}"
                        )
                        print(
                            f"\t\t{Tcolors.OKGREEN}is running"
                            + f"{Tcolors.ENDC}\n"
                        )
            else:
                if args.only_output:
                    print(running)
                else:
                    print(
                        f"\t{Tcolors.BOLD}No running strategies"
                        + f"{Tcolors.ENDC}"
                    )

        elif args.show_terminated_strategies:
            _, dead = strategy_manager.return_running_strategies()
            if not args.only_output:
                print(f"{Tcolors.HEADER}Terminated Strategies:{Tcolors.ENDC}")
            if dead:
                if args.only_output:
                    print(dead)
                else:
                    print(
                        "\tformat: <unique id>:"
                        + "[<pid>, <strategy name>, <start date/time>]"
                    )
                    for strategy in dead:
                        details = strategy[1]
                        print(
                            f"\t{Tcolors.BOLD}* {strategy[0]}{Tcolors.ENDC}:"
                            + f"{details}"
                        )
                        print(
                            f"\t\t{Tcolors.FAIL}is terminated"
                            + f"{Tcolors.ENDC}\n"
                        )
            else:
                if args.only_output:
                    print(dead)
                else:
                    print(
                        f"\t{Tcolors.BOLD}No terminated strategies"
                        + f"{Tcolors.ENDC}"
                    )

        elif args.terminate:
            id_to_terminate = args.terminate
            if strategy_manager.strategy_id_exists(id_to_terminate):
                if not args.only_output:
                    print(f"Terminating {id_to_terminate}...", end=" ")
                    spinner_thread = SpinnerThread()
                    spinner_thread.start()

                result = strategy_manager.terminate(id_to_terminate)

                if not args.only_output and spinner_thread:
                    spinner_thread.stop()
                if args.only_output:
                    print(result)
                else:
                    if result:
                        print(
                            f"{Tcolors.OKGREEN}"
                            + f"Successfully terminated strategy{Tcolors.ENDC}"
                        )
                    else:
                        print(
                            f"{Tcolors.FAIL}"
                            + f"Failed to terminate strategy{Tcolors.ENDC}"
                        )
            else:
                if args.only_output:
                    print(False)
                else:
                    print((f"Failed to terminate -"
                           f"id:{id_to_terminate} not found"))

        elif args.run:
            name = args.run
            if name in strategy_manager.strategies:
                result = strategy_manager.run(name)
                if args.only_output:
                    print(result)
                else:
                    if result:
                        print(
                            f"{Tcolors.OKGREEN}Successfully ran {name}"
                            + f"{Tcolors.ENDC}"
                        )
                    else:
                        print(
                            f"{Tcolors.FAIL}Failed to ran {name}"
                            + f"{Tcolors.ENDC}"
                        )
            else:
                print("Error: enter a valid strategy name")

        elif args.show_logs_dir:
            logpath = get_logs_dir()
            if not args.only_output:
                print("Logfiles directory is:")
            print(logpath)
        elif args.delete_all_logs:
            result = delete_all_logs()
            if args.only_output:
                print(result)
            else:
                if result:
                    print(
                        f"{Tcolors.OKGREEN}Successfully deleted all logfiles"
                        + f"{Tcolors.ENDC}"
                    )
                else:
                    print(
                        f"{Tcolors.FAIL}Failed to delete logfiles"
                        + f"{Tcolors.ENDC}"
                    )

        else:
            argparser.print_help()

        if args.only_output:  # for piping reasons
            sys.stdout.flush()

    except BrokenPipeError:  # for piping to other commands
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)
    except argparse.ArgumentTypeError as arge:
        print(
            f"\n\n{Tcolors.FAIL}an argument error occured:{Tcolors.ENDC}",
            arge,
        )
        print('enter "nebixbot -h" for help')
        sys.exit(1)


class SpinnerThread(threading.Thread):
    """Spinner thread for long tasks"""

    def __init__(self):
        super().__init__(target=self._spin)
        self._stopevent = threading.Event()

    def stop(self):
        """Stops the spinner"""
        self._stopevent.set()
        sys.stdout.write("\n")
        sys.stdout.flush()

    def _spin(self):
        while not self._stopevent.isSet():
            for char in "|/-\\":
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.10)
                sys.stdout.write("\b")


if __name__ == "__main__":
    main()
