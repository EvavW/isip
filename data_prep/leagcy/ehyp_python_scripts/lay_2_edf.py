import sys

def lay_ad_2_edf_ad(lay_list,edf_list):
    listfile = open(lay_list,'r').read()
    listcontent = listfile.split('\n')
    for filename in listcontent:
        if filename=="":
            break
        filename = filename.split(r'/')
        filename[-1]=filename[-1].split('.')[0]+".edf"
        #print filename[-1]
        relative_address = r"/".join([filename[-3],filename[-2],filename[-1]])
        #print relative_address

        ## This section finds all the relative files from TUH_EEG database
        tuh_edf = open(edf_list,'r').read()
        edf_files = tuh_edf.split('\n')
        for edf_file in edf_files:
            if edf_file=='':
                break
            if relative_address in edf_file:
                print edf_file

        
if __name__=="__main__":lay_ad_2_edf_ad(sys.argv[1],sys.argv[2])
