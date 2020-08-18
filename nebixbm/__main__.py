"""Nebixbm entrypoint"""

import sys
import argparse
from argparse import RawTextHelpFormatter
import threading
import time
import os

from nebixbm.other.tcolors import Tcolors
from nebixbm.command_center.bot_manager import BotManager
from nebixbm.log.logger import delete_all_logs, get_logs_dir


def main():
    """Project entry point function"""

    argparser = argparse.ArgumentParser(
        description=f" «{Tcolors.HEADER} Nebix Bot Manager‌ {Tcolors.ENDC}»",
        epilog=(
            f"{Tcolors.WARNING} proudly developed by"
            f" Nebix team{Tcolors.ENDC}\n\r"
        ),
        prog="nebixbm",
        usage="%(prog)s <command(s)>",
        formatter_class=RawTextHelpFormatter,
    )

    argparser.add_argument(
        "-sh", "--show-bots", action="store_true",
    )

    argparser.add_argument(
        "-shr", "--show-running-bots", action="store_true",
    )

    argparser.add_argument(
        "-sht", "--show-terminated-bots", action="store_true",
    )

    argparser.add_argument(
        "-r", "--run", metavar="<bot name>", action="store", type=str,
    )

    argparser.add_argument(
        "-t",
        "--terminate",
        metavar="<bot id>",
        action="store",
        type=str,
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
        bot_manager = BotManager()

        if args.show_bots:
            bots = bot_manager.return_available_bots()
            if bots:
                if args.only_output:
                    print(bots)
                else:
                    print(
                        f"{Tcolors.HEADER}Available Bots:"
                        + f"{Tcolors.ENDC}"
                    )
                    for bot_name in bots:
                        print(
                            f"\t- {Tcolors.BOLD}{bot_name}"
                            + f"{Tcolors.ENDC}:",
                            bots[bot_name],
                        )
            else:
                if args.only_output:
                    print(bots)
                else:
                    print(
                        f"\t{Tcolors.BOLD}No available bots"
                        + f"{Tcolors.ENDC}"
                    )

        elif args.show_running_bots:
            running, _ = bot_manager.return_running_bots()
            if not args.only_output:
                print(f"{Tcolors.HEADER}Running Bots:{Tcolors.ENDC}")
            if running:
                if args.only_output:
                    print(running)
                else:
                    print(
                        "\tformat: <unique id>:"
                        + "[<pid>, <bot name>, <start date/time>]"
                    )
                    for bot in running:
                        details = bot[1]
                        print(
                            f"\t{Tcolors.BOLD}* {bot[0]}{Tcolors.ENDC}:"
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
                        f"\t{Tcolors.BOLD}No running bots"
                        + f"{Tcolors.ENDC}"
                    )

        elif args.show_terminated_bots:
            _, dead = bot_manager.return_running_bots()
            if not args.only_output:
                print(f"{Tcolors.HEADER}Terminated Bots:{Tcolors.ENDC}")
            if dead:
                if args.only_output:
                    print(dead)
                else:
                    print(
                        "\tformat: <unique id>:"
                        + "[<pid>, <bot name>, <start date/time>]"
                    )
                    for bot in dead:
                        details = bot[1]
                        print(
                            f"\t{Tcolors.BOLD}* {bot[0]}{Tcolors.ENDC}:"
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
                        f"\t{Tcolors.BOLD}No terminated bots"
                        + f"{Tcolors.ENDC}"
                    )

        elif args.terminate:
            id_to_terminate = args.terminate
            if bot_manager.bot_id_exists(id_to_terminate):
                if not args.only_output:
                    print(f"Terminating {id_to_terminate}...", end=" ")
                    spinner_thread = SpinnerThread()
                    spinner_thread.start()

                result = bot_manager.terminate(id_to_terminate)

                if not args.only_output and spinner_thread:
                    spinner_thread.stop()
                if args.only_output:
                    print(result)
                else:
                    if result:
                        print(
                            f"{Tcolors.OKGREEN}"
                            + f"Successfully terminated bot{Tcolors.ENDC}"
                        )
                    else:
                        print(
                            f"{Tcolors.FAIL}"
                            + f"Failed to terminate bot{Tcolors.ENDC}"
                        )
            else:
                if args.only_output:
                    print(False)
                else:
                    print(
                        (
                            f"Failed to terminate -"
                            f"id:{id_to_terminate} not found"
                        )
                    )

        elif args.run:
            name = args.run
            if name in bot_manager.bots:
                result = bot_manager.run(name)
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
                print("Error: enter a valid bot name")

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
        print('enter "nebixbm -h" for help')
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
