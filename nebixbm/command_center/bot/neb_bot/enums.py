class StrategyVariables:
    PP_Done = "neb_bot:[R]-PP-Done"
    EX_Done = "neb_bot:[R]-EX-Done"
    LongEntry = "neb_bot:[R]-Strategy-LEn"
    ShortEntry = "neb_bot:[R]-Strategy-SEn"
    LongExit = "neb_bot:[R]-Strategy-LEx"
    ShortExit = "neb_bot:[R]-Strategy-SEx"
    StopLossValue = "neb_bot:[R]-Strategy-SLP"
    PositionSizeMultiplier = "neb_bot:[R]-Strategy-PSM"
    TimeCalculated = "neb_bot:[R]-Strategy-TIM"
    Close = "neb_bot:[R]-Strategy-CLS"


class StrategySettings:
    Liquidity_Slippage = "neb_bot:[S]-Liquidity-Slippage"
    Withdraw_Amount = "neb_bot:[S]-Withdraw-Amount"
    Withdraw_Apply = "neb_bot:[S]-Withdraw-Apply"
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


class Side:
    Long = "Long"
    Short = "Short"
    NA = "NA"