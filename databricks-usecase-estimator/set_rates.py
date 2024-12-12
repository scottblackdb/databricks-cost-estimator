#storage is per gb per month, includes storage plus I/O per gb
#dbus are priced per hour 
#compute defaults to serverless except for ML

rates = {
  "storage": .15,
  "dw": .70,
  "job": .45,
  "ap": .95,
  "ml": .55
}

csp_modifier = 0