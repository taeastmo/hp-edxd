def read_mca_header( file):
    
    file_text = open(file, "r")

    a = True
    comment_rows = 0
    first_data_line = 0
    line_n = 0
    nelem = [0,0]
    while a:
        file_line = file_text.readline().strip()
        
        if not file_line:
            #print("End Of File")
            a = False
        else:
            if file_line.startswith("#"):
                par, val = parse_mca_header_line(file_line)
                if par == 'rows':
                    nelem[0] = int(val)
                elif par == 'columns':
                    nelem[1] = int(val)
                comment_rows +=1
            else:
                a = False
    first_data_line = comment_rows
    return nelem, first_data_line

def parse_mca_header_line( line):
    tokens = line.split(':')
    par = tokens[0].strip()[1:]
    val = tokens[1].strip()
    return par, val