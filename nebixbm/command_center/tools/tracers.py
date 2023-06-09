import csv
import os
import sys

from nebixbm.log.logger import (
    create_logger,
    get_file_name,
    get_log_fname_path
)


class Trace:
    Orders = "Orders"
    Signals = "Signals"
    FinancialActivity = "FinancialActivity"


class Action:
    Modify = "Modify"
    Close = "Close"
    Open = "Open"


class CSVBase:
    c99_pointer = None

    def __get_full_names(self):
        params = [attr for attr in dir(self) if
                  not callable(getattr(self, attr))
                  and not attr.startswith("__")]
        params = params[0:params.index("c99_pointer")]
        return params

    def get_names(self):
        params = self.__get_full_names()
        params_name = []
        for param in params:
            params_name.append(param[4:])

        return params_name

    def get_values(self):
        params = self.__get_full_names()
        values = []
        for param in params:
            values.append(getattr(self, param))

        return values

    def set_values(self, data: [str]):
        params = self.__get_full_names()
        if len(data) != len(params):
            raise Exception("Invalid input data length.")
        i = 0
        for param in params:
            setattr(self, param, data[i])
            i += 1
        return self


class Orders(CSVBase):
    def __init__(self):
        self.name = "Orders"

        self.c00_Action = "NA"
        self.c01_Side = "NA"
        self.c02_Price = "NA"
        self.c03_Quantity = "NA"
        self.c04_Stoploss = "NA"
        self.c05_SLTriggerBy = "NA"
        self.c06_LeavesQuantity = "NA"
        self.c07_ReduceOnly = "NA"
        self.c08_TIF = "NA"
        self.c09_OrderStatus = "NA"
        self.c10_OrderID = "NA"
        self.c11_CratedAt = "NA"
        self.c12_UpdatedAt = "NA"
        self.c13_Time = "NA"


class Signals(CSVBase):
    def __init__(self):
        self.name = "Signals"

        self.c00_LEN = "NA"
        self.c01_LEX = "NA"
        self.c02_SEN = "NA"
        self.c03_SEX = "NA"
        self.c04_PSM = "NA"
        self.c05_SLV = "NA"
        self.c06_CLS = "NA"
        self.c07_NOP = "NA"
        self.c08_RMR = "NA"
        self.c09_TCS = "NA"


class FinancialActivity(CSVBase):
    def __init__(self):
        self.name = "FinancialActivity"

        self.c00_TRADING_BALANCE_BYBIT = "NA"
        self.c01_WITHDRAW_APPLY_BYBIT = "NA"
        self.c02_WITHDRAW_AMOUNT_BYBIT = "NA"
        self.c03_DEPOSIT_APPLY_BYBIT = "NA"
        self.c04_DEPOSIT_AMOUNT_BYBIT = "NA"
        self.c05_PNL = "NA"
        self.c06_PNLP = "NA"
        self.c07_HYPO_EQUITY_CURVE = "NA"
        self.c08_ACCOUNT_MIN_TRADING_BALANCE_BYBIT = "NA"
        self.c09_Time = "NA"
        self.c10_ALLOWED_DRAW_DOWN = "NA"
        self.c11_TRADE_ID = "NA"


class Tracer:
    def __init__(self, name, version, do_reset_ls):
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

        financial_activity_tracer_filename = self.name + "_financial_activity"
        self.financial_activity_tracer_path = \
            get_log_fname_path(financial_activity_tracer_filename).replace(".log", ".csv")

        try:
            # TODO: remove redundancy
            if (not os.path.isfile(self.orders_tracer_path)) or do_reset_ls:
                with open(self.orders_tracer_path, "w", newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(Orders().get_names())
                self.logger.debug("New Orders csv file has created.")
            else:
                self.logger.warning("Orders csv file already exists. "
                                    "Further datum will be appended.")

            if (not os.path.isfile(self.signals_tracer_path)) or do_reset_ls:
                with open(self.signals_tracer_path, "w", newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(Signals().get_names())
                self.logger.debug("New Signals csv file has created.")
            else:
                self.logger.warning("Signals csv file already exists. "
                                    "Further datum will be appended.")

            if (not os.path.isfile(self.financial_activity_tracer_path)) or do_reset_ls:
                with open(self.financial_activity_tracer_path, "w", newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(FinancialActivity().get_names())
                self.logger.debug("New FinancialActivity csv file has created.")
            else:
                self.logger.warning("FinancialActivity csv file already exists. "
                                    "Further datum will be appended.")

            self.logger.debug(
                "Tracer initialized.\n" +
                f"Orders list path: {self.orders_tracer_path}\n" +
                f"Signals list path: {self.signals_tracer_path}\n" +
                f"FinancialActivity list path: {self.financial_activity_tracer_path}")

        except Exception as ex:
            self.logger.debug(f"Tracer initialization failed. error: {ex}")

    def log(self, trace: Trace, data: FinancialActivity or Signals or Orders):
        if trace == Trace.Orders:
            try:
                with open(self.orders_tracer_path, "a", newline="") as \
                        csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(data.get_values())
                self.logger.info("Successfully added data to orders list.")

            except Exception as ex:
                self.logger.error("Failed to add data to orders list.")

        if trace == Trace.Signals:
            try:
                with open(self.signals_tracer_path, "a",
                          newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(data.get_values())
                self.logger.info("Successfully added data to signal list.")

            except Exception as ex:
                self.logger.error("Failed to add data to signal list.")

        if trace == Trace.FinancialActivity:
            try:
                with open(self.financial_activity_tracer_path, "a",
                          newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(data.get_values())
                self.logger.info("Successfully added data to FinancialActivity list.")

            except Exception as ex:
                self.logger.error("Failed to add data to FinancialActivity list.")

    def read(self, trace: Trace, last_row=False):
        # TODO: remove redundancy
        if trace == Trace.Orders:
            try:
                with open(self.orders_tracer_path, "r",
                          newline="") as csv_file:
                    reader = csv.reader(csv_file)
                    data = list(reader)
                self.logger.info(
                    "Successfully read data from Orders csv file.")
                if last_row:
                    if len(data) > 1:
                        record = Orders()
                        record.set_values(data[-1])
                        return record
                    else:
                        return None
                else:
                    records = []
                    data = data[1:]
                    for row in data:
                        records.append(Orders().set_values(row))
                    return records

            except Exception as ex:
                self.logger.error("Failed to read data from FinancialActivity csv file.")

        if trace == Trace.Signals:
            raise NotImplementedError

        if trace == Trace.FinancialActivity:
            try:
                with open(self.financial_activity_tracer_path, "r",
                          newline="") as csv_file:
                    reader = csv.reader(csv_file)
                    data = list(reader)
                self.logger.info("Successfully read data from FinancialActivity csv file.")
                if last_row:
                    if len(data) > 1:
                        record = FinancialActivity()
                        record.set_values(data[-1])
                        return record
                    else:
                        return None
                else:
                    records = []
                    data = data[1:]
                    for row in data:
                        records.append(FinancialActivity().set_values(row))
                    return records

            except Exception as ex:
                self.logger.error("Failed to read data from FinancialActivity csv file.")
