import os

# TODO: append data before first date as well
def append_to_file(date, value, file):
    f = open(file, "a+")
    f.write(str(date) + "," + str(value)+ "\n")
    f.close()


def read_last_date(file):
    if os.path.exists(file):
        f = open(file, "r")
        line_list = f.readlines()
        f.close()
        last_line = line_list[-1]
        date = last_line.split(',')[0]
        return int(date) + 86400
    else:
        return None