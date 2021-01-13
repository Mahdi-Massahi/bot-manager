import csv

from nebixbm.log.logger import (
    create_logger,
    get_file_name,
    get_log_fname_path
)


class Trace:
    Trades = "Tardes"
    Signals = "Sygnals"


class Tracer:
    def __init__(self, name, version):
        self.name = name
        self.version = version
        filename = get_file_name(self.name+"_Tracer", self.version)
        self.logger, self.log_filepath = create_logger(filename, filename)

        trade_tracer_filename = self.name + "_" + self.version + "_trades"
        self.trades_tracer_path = \
            get_log_fname_path(trade_tracer_filename).replace(".log", ".csv")
        signal_tracer_filename = self.name + "_" + self.version + "_signals"
        self.signals_tracer_path = \
            get_log_fname_path(signal_tracer_filename).replace(".log", ".csv")

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
            with open(self.trades_tracer_path, "w", newline="") as csv_file:
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

            self.logger.debug("Tracer initialized.\n" +
                              f"Trades list path: {self.trades_tracer_path}\n" +
                              f"Signals list path: {self.signals_tracer_path}")

        except Exception as ex:
            self.logger.debug(f"Tracer initialization failed. error: {ex}")

    def log(self, trace: Trace, data):
        if trace == Trace.Trades:
            try:
                with open(self.trades_tracer_path, "a", newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(data)
                self.logger.info("Successfully added data to trade list.")

            except Exception as ex:
                self.logger.error("Failed to add data to trade list.")

        if trace == Trace.Signals:
            try:
                with open(self.signals_tracer_path, "a",
                          newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(data)
                self.logger.info("Successfully added data to signal list.")

            except Exception as ex:
                self.logger.error("Failed to add data to signal list.")
