class StrategyVariables:
    PP_Done = "neb_bot:[R]-PP-Done"
    EX_Done = "neb_bot:[R]-EX-Done"
    LongEntry = "neb_bot:[R]-Strategy-LEn"
    ShortEntry = "neb_bot:[R]-Strategy-SEn"
    LongExit = "neb_bot:[R]-Strategy-LEx"
    ShortExit = "neb_bot:[R]-Strategy-SEx"
    StopLossValue = "neb_bot:[R]-Strategy-SLV"
    PositionSizeMultiplier = "neb_bot:[R]-Strategy-PSM"
    TimeCalculated = "neb_bot:[R]-Strategy-TIM"
    Close = "neb_bot:[R]-Strategy-CLS"
    NextOpen = "neb_bot:[R]-Next-Open"
    StrategyVals = "neb_bot:[R]-StrategyVals"


class StrategySettings:
    Liquidity_Slippage = "neb_bot:[S]-Liquidity-Slippage"
    Withdraw_Amount = "neb_bot:[S]-Withdraw-Amount"
    Withdraw_Apply = "neb_bot:[S]-Withdraw-Apply"
    Deposit_Amount = "neb_bot:[S]-Deposit-Amount"
    Deposit_Apply = "neb_bot:[S]-Deposit-Apply"
    BybitTakerFee = "neb_bot:[S]-Bybit-Taker-Fee"
    RMRule = "neb_bot:[S]-RMRule"
    GetKlineRetryDelay = "neb_bot:[S]-Get-Kline-Retry-Delay"
    RunRStrategyTimeout = "neb_bot:[S]-Run-R-Strategy-Timeout"
    GetOPDRetryDelay = "neb_bot:[S]-Get-OPD-Retry-Delay"
    GetOBRetryDelay = "neb_bot:[S]-Get-OB-Retry-Delay"
    WaitCloseLiquidity = "neb_bot:[S]-Wait-Close-Liquidity"
    ClosePositionDelay = "neb_bot:[S]-Close-Position-Delay"
    GetBLRetryDelay = "neb_bot:[S]-Get-BLRetry-Delay"
    WaitOpenLiquidity = "neb_bot:[S]-Wait-Open-Liquidity"
    OpenPositionDelay = "neb_bot:[S]-Open-Position-Delay"
    ChangeLeverageDelay = "neb_bot:[S]-Change-Leverage-Delay"
    MinimumTradingBalance = "neb_bot:[S]-Minimum-Trading-Balance"
    ChangeTriggerPriceRetries = "neb_bot:[S]-Change-Trigger-Price-Retries"
    ChangeTriggerPriceDelay = "neb_bot:[S]-Change-Trigger-Price-Delay"
    ResetLocalStop = "neb_bot:[S]-Reset-Local-Stop"
    AllowedDrawdown = "neb_bot:[S]-Allowed-Drawdown"
    TradeID = "neb_bot:[S]-Trade-ID"


class RInterface:
    NA = "NA"
    FALSE = "FALSE"
    TRUE = "TRUE"


class Side:
    Long = "Long"
    Short = "Short"
    NA = RInterface.NA

