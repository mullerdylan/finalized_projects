import os
import datetime
date = datetime.datetime.now().date()
# print(os.path.exists(F'Logs/log_{date}.csv'))
if os.path.isdir('Logs2') ==False:
    os.makedirs('Logs2')
print('isfine')
# print(os.path.exists(F'log_{date}.csv'))
# import datetime
# def frame_count(start,end,refresh_rate_min):
#     delta = (datetime.datetime.strptime(end,'%H:%M:%S') - datetime.datetime.strptime(start,'%H:%M:%S')).total_seconds()
#     frames = round(delta/(refresh_rate_min*60))
#     return frames

# a = datetime.datetime.strptime('7:00:38','%H:%M:%S')
# b = datetime.datetime.strptime('18:35:38','%H:%M:%S')
# delta = (b-a).total_seconds()

# refresh_rate_min = 5

# frames = round(delta/(refresh_rate_min*60))
# print(frames)
# print(frame_count('7:00:38','18:35:38',5))

# from event_logger import frame_count
# inerval_min = 5
# print(frame_count('7:00:00','7:01:00',inerval_min))
