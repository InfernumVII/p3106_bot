#Mb make async
def parse_group():
    out = {}
    check = False
    with open('isu_group_list.csv', encoding='utf-8') as f:
        for i in f.read().splitlines():
            if i == ';;':
                check = False
            if check is True:
                user = i.split(';')
                out[user[1].strip()] = user[2].strip()
            if i == '№ п/п;Таб. номер;Ф.И.О.':
                check = True
            
    return out

if __name__ == '__main__':
    print(parse_group())
