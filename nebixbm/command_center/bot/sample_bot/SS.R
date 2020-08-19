
SS <- function(x, data) {
  # Variables
  ATRL   <- ceiling(x[1])   # ATR Length (14)
  SLTP   <- x[2]            # Stoploss Tolerance Percent (0.1)
  RMRule <- x[3]            # Risk Management Rule (10)
  PSML   <- 6               # Position Size Multiplier Limit
  Com    <- 0.075           # Also its input for Neb.STD
  
  # Strategy
  ATR   <- Neb.ATR(high  = data$High, 
                   low   = data$Low,
                   close = data$Close,
                   ATRL)
  
  data$LongEntry <-
    data$HAC > data$HAO &
    Neb.Previous(data$HAC, 1) > Neb.Previous(data$HAO, 1)
                                     
  data$ShortEntry <-
    data$HAC < data$HAO &
    Neb.Previous(data$HAC, 1) < Neb.Previous(data$HAO, 1)
  
  # Position Exit Rules
  data$LongExit  <- data$ShortEntry
  data$ShortExit <- data$LongEntry
  
  # remove NAs
  data$LongEntry[is.na(data$LongEntry)]   <- F
  data$ShortEntry[is.na(data$ShortEntry)] <- F
  data$LongExit[is.na(data$LongExit)]     <- F
  data$ShortExit[is.na(data$ShortExit)]   <- F
  
  # Next Open
  data$PSM <- NA
  
  # Stoploss price
  data$SL <- NA
  data$SL[data$LongEntry]   <- data$Low[data$LongEntry] - ATR[data$LongEntry]
  data$SL[data$ShortEntry]  <- data$High[data$ShortEntry] + ATR[data$ShortEntry]
    
  # Check NAs
  data$SL[is.na(data$SL) & data$LongEntry]  <-
    data$Low[is.na(data$SL) & data$LongEntry]
  data$SL[is.na(data$SL) & data$ShortEntry] <-
    data$High[is.na(data$SL) & data$ShortEntry]
  
  # Position sizing
  data$PSM[data$LongEntry]  <-
    (RMRule-Com*2) / abs((data$Close[data$LongEntry] - data$SL[data$LongEntry]) / data$Close[data$LongEntry] * 100)
  data$PSM[data$ShortEntry] <-
    (RMRule-Com*2) / abs((data$SL[data$ShortEntry] - data$Close[data$ShortEntry]) / data$Close[data$ShortEntry] * 100)
  data$PSM[data$PSM > PSML] <- PSML
  
  return(data)
}