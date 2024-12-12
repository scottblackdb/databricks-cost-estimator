import math
import pandas as pd
import set_rates

def get_storage_estamite(data_size, monthly_new):
  #add %15 to the monthly to account for time in between optimize and vaccum
  #times 3x to monthly new for staging space

  total_storage = data_size * 1.15 + monthly_new * 3
  
  stg_est = total_storage * set_rates.rates['storage']

  return round(stg_est)

def get_dw_estamite(dw_hrs, dw_users, data_size):
  #get the number of dw clusters needed, 1 cluster per 20 users

  #create a mapping of gb ratio to DBSQL size. smallest size consider is X-SMALL which is 6 DBUs
  wh_sizes = {
    1:6,
    2:12,
    3:24,
    4:40,
    5:80,
    6:144,
    7:272,
    8:588
  }

  users_per_dw = 20

  dw_clusters = math.ceil(dw_users / users_per_dw)

  days_per_month = 30.5

  dw_total_hrs = dw_clusters * dw_hrs * days_per_month
  
  gb_per_dw = 200
  dw_size = math.ceil(data_size / gb_per_dw)
  if(dw_size > 8):
     dw_size = 8
  
  total_dw_dbus = wh_sizes[dw_size] * dw_total_hrs

  dw_est = round(total_dw_dbus * set_rates.rates['dw'])

  return dw_est


def get_estimate(data_size, monthly_new, dw_hrs, dw_users):
  stg_est = get_storage_estamite(data_size, monthly_new)
  dw_est = get_dw_estamite(dw_hrs, dw_users, data_size)

  data = {
    'workload': ['storage', 'data warehouse'],
    'cost': [stg_est, dw_est]
  }

  return pd.DataFrame(data)
  