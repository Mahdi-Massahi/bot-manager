
vals <- c(
  paste0(bot_name, ":[R]-Strategy-LEn"),
  paste0(bot_name, ":[R]-Strategy-SEn"),
  paste0(bot_name, ":[R]-Strategy-LEx"),
  paste0(bot_name, ":[R]-Strategy-SEx"),
  paste0(bot_name, ":[R]-Strategy-SLP"),
  paste0(bot_name, ":[R]-Strategy-PSM"),
  paste0(bot_name, ":[R]-Strategy-CLS"),
  paste0(bot_name, ":[R]-Strategy-NOP"),
  paste0(bot_name, ":[R]-Strategy-TIM")
)
for (val in vals){
  message(paste(val, ':\t', redisGet(val)))
}
