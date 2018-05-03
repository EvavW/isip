import sys,os

## input files should be a lab file that have information per epoch

def main(filelist):
    
    op = open(filelist,'r').read()
    files = op.split('\n')

    seiz_class_count = 0
    bckg_class_count = 0 
    chew_class_count = 0
    mcle_class_count = 0

    for filename in files:
        if filename == '':
            break
        
        op_file = open(filename,'r').read()
        file_info = op_file.split('\n')
        
        for filelines in file_info:
            if filelines == '':
                break
            
            line_info = filelines.split()
            print line_info
            

            ## count total number of seiz classes assigned
            if line_info[2].lower() == "seiz":
                seiz_class_count += 1

            if line_info[2].lower() == "bckg":
                bckg_class_count += 1

            if line_info[2].lower() == "chew":
                chew_class_count += 1

            if line_info[2].lower() == "mcle":
                mcle_class_count += 1

    print seiz_class_count , " ---->>>>> Number of Seizure Epochs"

    print bckg_class_count , " ---->>>>> Number of Background Epochs"

    print seiz_class_count + bckg_class_count, " ---->>>>> Number of Total Epochs"

if __name__=="__main__": main(sys.argv[1])
