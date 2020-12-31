vals <- c(
  # "neb_bot:[R]-PP-Done",
  # "neb_bot:[R]-EX-Done",
  "neb_bot:[R]-Strategy-LEn",
  "neb_bot:[R]-Strategy-SEn",
  "neb_bot:[R]-Strategy-LEx",
  "neb_bot:[R]-Strategy-SEx",
  "neb_bot:[R]-Strategy-SLP",
  "neb_bot:[R]-Strategy-PSM",
  "neb_bot:[R]-Strategy-TIM",
  "neb_bot:[R]-Strategy-CLS"
)
for (val in vals){
  message(paste(val, ':\t', redisGet(val)))
}
