import csv

from nebixbm.log.logger import (
    create_logger,
    get_file_name,
    get_log_fname_path
)


class Trace:
    Orders = "Orders"
    Signals = "Signals"
    Wallet = "Wallet"
    CPNL = "CPNL"


class Tracer:
    def __init__(self, name, version):
        self.name = name
        self.version = version
        filename = get_file_name(self.name+"_Tracer", self.version)
        self.logger, self.log_filepath = create_logger(filename, filename)

        orders_tracer_filename = self.name + "_" + self.version + "_orders"
        self.orders_tracer_path = \
            get_log_fname_path(orders_tracer_filename).replace(".log", ".csv")

        signal_tracer_filename = self.name + "_" + self.version + "_signals"
        self.signals_tracer_path = \
            get_log_fname_path(signal_tracer_filename).replace(".log", ".csv")

        wallet_tracer_filename = self.name + "_" + self.version + "_wallet"
        self.wallet_tracer_path = \
            get_log_fname_path(wallet_tracer_filename).replace(".log", ".csv")

        cpnl_tracer_filename = self.name + "_" + self.version + "_cpnl"
        self.cpnl_tracer_path = \
            get_log_fname_path(cpnl_tracer_filename).replace(".log", ".csv")

        try:
            header = [
                    "Action",
                    "Side",
                    "Price",
                    "Quantity",
                    "Stoploss",
                    "SLTriggerBy",
                    "LeavesQuantity",
                    "ReduceOnly",
                    "TIF",
                    "OrderStatus",
                    "OrderID",
                    "CratedAt",
                    "UpdatedAt",
                    "Time",
            ]
            with open(self.orders_tracer_path, "w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(header)

            header = [
                    "LEN",
                    "LEX",
                    "SEN",
                    "SEX",
                    "PSM",
                    "SLV",
                    "CLS",
                    "TCS",
            ]
            with open(self.signals_tracer_path, "w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(header)

            header = [
                "Equity",
                "WithdrawAmount",
                "TradingBalance",
                "WithdrawApply",
                "Time",
            ]
            with open(self.wallet_tracer_path, "w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(header)

            header = [
                "Id",
                "UserId",
                "Symbol",
                "OrderId",
                "Side",
                "Quantity",
                "OrderPrice",
                "OrderType",
                "ExecType",
                "ClosedSize",
                "CumEntryValue",
                "AvgEntryPrice",
                "CumExitValue",
                "AvgExitPrice",
                "ClosedPNL",
                "FillCount",
                "Leverage",
                "CreatedAt",
            ]
            with open(self.cpnl_tracer_path, "w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(header)

            self.logger.debug(
                "Tracer initialized.\n" +
                f"Orders list path: {self.orders_tracer_path}\n" +
                f"Signals list path: {self.signals_tracer_path}" +
                f"Wallet list path: {self.wallet_tracer_path}" +
                f"CPNL list path: {self.cpnl_tracer_path}")

        except Exception as ex:
            self.logger.debug(f"Tracer initialization failed. error: {ex}")

    def log(self, trace: Trace, data):
        if trace == Trace.Orders:
            try:
                with open(self.orders_tracer_path, "a", newline="") as \
                        csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(data)
                self.logger.info("Successfully added data to orders list.")

            except Exception as ex:
                self.logger.error("Failed to add data to orders list.")

        if trace == Trace.Signals:
            try:
                with open(self.signals_tracer_path, "a",
                          newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(data)
                self.logger.info("Successfully added data to signal list.")

            except Exception as ex:
                self.logger.error("Failed to add data to signal list.")

        if trace == Trace.Wallet:
            try:
                with open(self.wallet_tracer_path, "a",
                          newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(data)
                self.logger.info("Successfully added data to wallet list.")

            except Exception as ex:
                self.logger.error("Failed to add data to wallet list.")

        if trace == Trace.CPNL:
            try:
                with open(self.cpnl_tracer_path, "a",
                          newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(data)
                self.logger.info("Successfully added data to CPNL list.")

            except Exception as ex:
                self.logger.error("Failed to add data to CPNL list.")

    def read(self, trace: Trace):
        if trace == Trace.Orders:
            raise NotImplementedError

        if trace == Trace.Signals:
            raise NotImplementedError

        if trace == Trace.Wallet:
            raise NotImplementedError

        if trace == Trace.CPNL:
            try:
                with open(self.cpnl_tracer_path, "r",
                          newline="") as csv_file:
                    reader = csv.reader(csv_file)
                    data = list(reader)
                self.logger.info("Successfully red data from CPNL csv file.")
                return data

            except Exception as ex:
                self.logger.error("Failed to read data from CPNL csv file.")
