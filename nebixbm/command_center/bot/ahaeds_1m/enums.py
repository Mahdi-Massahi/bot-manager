name = "ahaeds_1m"


class StrategyVariables:
    PP_Done = name + ":[R]-PP-Done"
    EX_Done = name + ":[R]-EX-Done"
    LongEntry = name + ":[R]-Strategy-LEn"
    ShortEntry = name + ":[R]-Strategy-SEn"
    LongExit = name + ":[R]-Strategy-LEx"
    ShortExit = name + ":[R]-Strategy-SEx"
    StopLossValue = name + ":[R]-Strategy-SLV"
    PositionSizeMultiplier = name + ":[R]-Strategy-PSM"
    TimeCalculated = name + ":[R]-Strategy-TIM"
    Close = name + ":[R]-Strategy-CLS"
    NextOpen = name + ":[R]-Strategy-NOP"
    StrategyVals = name + ":[R]-StrategyVals"


class StrategySettings:
    Liquidity_Slippage = name + ":[S]-Liquidity-Slippage"
    Withdraw_Amount = name + ":[S]-Withdraw-Amount"
    Withdraw_Apply = name + ":[S]-Withdraw-Apply"
    Deposit_Amount = name + ":[S]-Deposit-Amount"
    Deposit_Apply = name + ":[S]-Deposit-Apply"
    BybitTakerFee = name + ":[S]-Bybit-Taker-Fee"
    RMRule = name + ":[S]-RMRule"
    GetKlineRetryDelay = name + ":[S]-Get-Kline-Retry-Delay"
    RunRStrategyTimeout = name + ":[S]-Run-R-Strategy-Timeout"
    GetOPDRetryDelay = name + ":[S]-Get-OPD-Retry-Delay"
    GetOBRetryDelay = name + ":[S]-Get-OB-Retry-Delay"
    WaitCloseLiquidity = name + ":[S]-Wait-Close-Liquidity"
    ClosePositionDelay = name + ":[S]-Close-Position-Delay"
    GetBLRetryDelay = name + ":[S]-Get-BLRetry-Delay"
    WaitOpenLiquidity = name + ":[S]-Wait-Open-Liquidity"
    OpenPositionDelay = name + ":[S]-Open-Position-Delay"
    ChangeLeverageDelay = name + ":[S]-Change-Leverage-Delay"
    MinimumTradingBalance = name + ":[S]-Minimum-Trading-Balance"
    ChangeTriggerPriceRetries = name + ":[S]-Change-Trigger-Price-Retries"
    ChangeTriggerPriceDelay = name + ":[S]-Change-Trigger-Price-Delay"
    ResetLocalStop = name + ":[S]-Reset-Local-Stop"
    AllowedDrawdown = name + ":[S]-Allowed-Drawdown"
    TradeID = name + ":[S]-Trade-ID"


class RInterface:
    NA = "NA"
    FALSE = "FALSE"
    TRUE = "TRUE"


class Side:
    Long = "Long"
    Short = "Short"
    NA = RInterface.NA
