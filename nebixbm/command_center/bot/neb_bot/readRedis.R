vals <- c(
  # "[R]-PP-Done",
  # "[R]-EX-Done",
  "[R]-Strategy-LEn",
  "[R]-Strategy-SEn",
  "[R]-Strategy-LEx",
  "[R]-Strategy-SEx",
  "[R]-Strategy-SLP",
  "[R]-Strategy-PSM",
  "[R]-Strategy-TIM"
)
for (val in vals){
  message(paste(val, ':\t', redisGet(val)))
}
