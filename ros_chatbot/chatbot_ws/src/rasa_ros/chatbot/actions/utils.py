def correct_time(original_time):
    # tomorrow at 8pm --> 2020–09–28T20:00:00.000–07:00
    tmp = original_time.split('T')
    data, time = tmp[0], tmp[1]
    # data = 2020–09–28 
    # time 20:00:00.000–07:00
    tmp = time.split('-')
    time = tmp[0]
    gmt = tmp[1]
    tmp = time.split(':')
    time = tmp[0] + ':' + tmp[1]
    return data, time, gmt

def correct_category(original_cat):
    return original_cat.split('-')[-1]