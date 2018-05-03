import sys, os, re

def file_processing(filename):
    file_open = open(filename,'r').read()
    header_parts = file_open.split(" ")
    
    fields = []
    
    for parts in header_parts:
        if parts != '':
            fields.append(parts)
    
    #print file_parts.index("1795")
    print fields[13], "********"



if __name__ == "__main__": file_processing(sys.argv[1])