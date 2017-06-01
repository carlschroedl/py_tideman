import sys
def text_to_tuple_dict(filename):
    f = open(filename)
    dict = {}
    col_headers = []
    row_header = ''
    for line in f.readlines():
        if 0 == len(col_headers):
            col_headers = line.split('\n')[0].split('\t')[1:]
        else:
            for i, value in enumerate(line.split('\n')[0].split('\t')):
                if 0 == i:
                    row_header = value
                else:
                    col_header = col_headers[i - 1]
                    key = (col_header, row_header)
                    value = value
                    dict[key] = value
    f.close()
    return dict

if __name__ == '__main__':
     filename = sys.argv[1]    
     print(text_to_tuple_dict(filename))
