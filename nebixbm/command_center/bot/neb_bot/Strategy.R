SS <- function(x, aData, tData) {
  # Variables
  ATRL <- ceiling(x[1])   # ATR Length (14)
  SLTP <- x[2]            # Stoploss Tolerance Percent (0.1)
  RMRule <- x[3]          # Risk Management Rule (10)
  PSML <- 5               # Position Size Multiplier Limit
  Com <- x[4]             # Also its input for Neb.STD

  # Strategy
  ATR <- Neb.ATR(high = aData$High,
                 low = aData$Low,
                 close = aData$Close,
                 ATRL)

  tData$LongEntry <-
    aData$HAC > aData$HAO
  # & Neb.Previous(aData$HAC, 1) < Neb.Previous(aData$HAO, 1)

  tData$ShortEntry <-
    aData$HAC < aData$HAO
  # & Neb.Previous(aData$HAC, 1) > Neb.Previous(aData$HAO, 1)

  # Position Exit Rules
  tData$LongExit <- tData$ShortEntry
  tData$ShortExit <- tData$LongEntry

  # remove NAs
  tData$LongEntry[is.na(tData$LongEntry)] <- F
  tData$LongEntry[is.na(tData$LongEntry)] <- F
  tData$ShortEntry[is.na(tData$ShortEntry)] <- F
  tData$LongExit[is.na(tData$LongExit)] <- F
  tData$ShortExit[is.na(tData$ShortExit)] <- F

  # Next Open
  tData$PSM <- NA

  # Stoploss price
  tData$SL <- NA
  tData$SL[tData$LongEntry] <- tData$Low[tData$LongEntry] - 15
  tData$SL[tData$ShortEntry] <- tData$High[tData$ShortEntry] + 15

  # Check NAs
  tData$SL[is.na(tData$SL) & tData$LongEntry] <-
    tData$Low[is.na(tData$SL) & tData$LongEntry]
  tData$SL[is.na(tData$SL) & tData$ShortEntry] <-
    tData$High[is.na(tData$SL) & tData$ShortEntry]

  # Position sizing
  tData$PSM[tData$LongEntry] <-
    (RMRule - Com * 2) / abs((tData$Close[tData$LongEntry] - tData$SL[tData$LongEntry]) / tData$Close[tData$LongEntry] * 100)
  tData$PSM[tData$ShortEntry] <-
    (RMRule - Com * 2) / abs((tData$SL[tData$ShortEntry] - tData$Close[tData$ShortEntry]) / tData$Close[tData$ShortEntry] * 100)
  tData$PSM[tData$PSM > PSML] <- PSML

  return(tData)
}