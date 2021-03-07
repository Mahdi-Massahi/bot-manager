# Terminology  

## `ACCOUNT_BALANCE`
The amount of money that exists in the `TRADING_ACCOUNT` regardless of any open position in any given time.
`ACCOUNT_BALANCE` is in terms of `BASE_CURRENCY`  

## `BASE_CURRENCY`
Is the currency that an accounts profit and loss is calculated and paid in or deposited or withdrawn.  

## `TRADING_ACCOUNT_BYBIT`
Refers to each `CONTRACT_BYBIT` that is separately calculated across Bybit’s platform. 
Ex: `BTCUSD` contract is a contract that is settled and profit and loss is paid in `BTC` coin. So the `BASE_CURRENCY` of that `TRADING_ACCOUNT_BYBIT` is `BTC`.  

## `ZERO_EXPOSED_BALANCE_BYBIT`
Is the amount of `BASE_CURRENCY` in `TRADING_ACCOUNT_BYBIT` when there is no `OPEN_POSITION`.
In other words it is the same as `ACCOUNT_BALANCE` but in the situations that there is not open position.

## `CONTRACT_BYBIT`
Is a futures contract whether linear or inverse or inverse futures. Every contracts has its own definition and they should be referred to Bybit's own website and it is prone to change overtime.  

## `OPEN_POSITION_BYBIT`
The same definition as described in the contract detail.

## `TRADING_BALANCE_BYBIT`
Is the `ZERO_EXPOSED_BALANCE_BYBIT` minus `WITHDRAW_AMOUNT`.  

## `DEPOSIT_AMOUNT_BYBIT`
The amount of money in terms of `BASE_CURRENCY` in which is deposited or exchanged through `MOTHER_ACCOUNT_BYBIT` (that effects `ACCOUNT_BALANCE` and `ZERO_EXPOSED_BALANCE_BYBIT`)  

## `MOTHER_ACCOUNT_BYBIT`
Is the account of Bybit that is associated with an email address. It encompasses multiple coins and multiple contracts to trade and coin exchange options.
It encompasses multiple `TRADING_ACCOUNT_BYBIT`

## `ACCOUNT_MIN_TRADING_BALANCE_BYBIT`
A limit for a `TRADING_BOT` to not to trade below. In terms of `BASE_CURRENCY`

## `TRADING_BOT_BYBIT`
A trading algorithm that execute trades in a `TRADING_ACCOUNT_BYBIT`.

## `BOT_MANAGER_BYBIT`
Manages multiple `TRADING_BOT_BYBIT`s

## `WITHDRAW_AMOUNT_BYBIT`
A positive amount that intended to withdraw or have withdrawn from `TRADING_ACCOUNT_BYBIT`

## `WITHDRAW_APPLY_BYBIT`
A flag that applies `WITHDRAW_AMOUNT_BYBIT` on a `TRADING_BOT_BYBIT`

## `DEPOSIT_APPLY_BYBIT`
Is a flag that indicates we have had a deposit in between `TRADING_BOT_BYBIT`'s `BOT_SCHEDULES`

## `BOT_SCHEDULES`
`TRADING_BOT_BYBIT` runs a trading algorithm every new observation that it gets. The time between these observations is determined by the timeframe that it works in. The `TRADING_BOT_BYBIT` schedules these operations and these operations are called `BOT_SCHEDULES`  

## `PNL`
Profit and loss that is calculated after any trade or between two points in time. Its unit is in `BASE_CURRENCY`.  

## `PNLP`
PNL in terms of percent relative to `ZERO_EXPOSED_BALANCE_BYBIT` before position existence.

## `HYPO_EQUITY_CURVE`
A hypothetical equity curve that is calculated in the any trading algorithm to locate a `LOCAL_STOP_LOSS`

## `LOCAL_STOP_LOSS`
NULL