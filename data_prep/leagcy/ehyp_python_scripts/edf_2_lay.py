import sys

## Provide full list of edf list as a first argument and full list of lay list as 
#  a second one to see the relevant lay file list.



def lay_ad_2_edf_ad(edf_list,lay_list):
    listfile = open(edf_list,'r').read()
    listcontent = listfile.split('\n')
    for filename in listcontent:
        if filename=="":
            break
        filename = filename.split(r'/')
        filename[-1]=filename[-1].split('.')[0]+".lay"
        #print filename[-1]
        relative_address = r"/".join([filename[-3],filename[-2],filename[-1]])
        #print relative_address

        ## This section finds all the relative files from TUH_EEG database
        lays = open(lay_list,'r').read()
        lay_files = lays.split('\n')
        for lay_file in lay_files:
            if lay_file=='':
                break
            if relative_address in lay_file:
                print lay_file


if __name__=="__main__":lay_ad_2_edf_ad(sys.argv[1],sys.argv[2])
