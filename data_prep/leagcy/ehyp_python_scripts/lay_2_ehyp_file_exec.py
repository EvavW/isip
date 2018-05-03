import sys,os

def file_process(filelist,edf_abs_files):
    
    files = open(filelist,'r').read()
    files = files.split('\n')
    
    for _file in files:
        if _file == "":
            break
        
        file_len = file_length_header(_file,edf_abs_files)
        #print file_len
        #print _file



        layfile = open('%s'%_file,'r')
        layfile = layfile.read()
        #layfile = layfile.rstrip()
        
        comments = layfile.split('[Comments]\r\n')
        if not comments[1] or comments[1] == "":
            only_bckg_annotation(file_len,_file)
            continue
        else:

            separate_seiz_interval(comments[1], file_len,_file)

def only_bckg_annotation(rec_time,file_):
    f = open('tmp.x','w').close()
    f = open('tmp.x','a')
    i = 0
    print "file is ", file_
    print "8****** ", rec_time

    while i < (float(rec_time)-1):
        i += 1
        print "%d %d bckg"%(i*100000, (i+1)*100000)
        str = "%d %d bckg\n"%(i*100000, (i+1)*100000)
        f.write('%s'%str)
    ehyp_file = file_.split(r'.')
    #ehyp_file = ehyp_file[-2] +
    ehyp_file[-1] = ".ehyp"
    ehyp_file = ehyp_file[0] + '.' + ehyp_file[1] + '.'  + ehyp_file[2] + ehyp_file[3]# + ehyp_file[4] + ehyp_file[5] + ehyp_file[6] + ehyp_file[7] + ehyp_file[8] + ehyp_file[9] + ehyp_file[10] + ehyp_file[11]
    #ehyp_file = ehyp_file.replace("lay","ehyp")
    

    print ehyp_file
    f.close()
    cmd = "cat tmp.x >%s"%ehyp_file
    print "for file ", file_, "  ", cmd
    cmmd = os.system('%s'%cmd)
    

def separate_seiz_interval(seiz_str, file_len,file_):
    
    seiz_events = seiz_str.split('\n')
    seiz_list = []
    for seiz_time in seiz_events:
        if seiz_time == ' ' or seiz_time == '' :
            break
        
        #print seiz_time
        
#        seiz_time= seiz_time.rstrip()
        seiz_time = seiz_time.split(',')
#        print  " cmment " , seiz_time[0], ', ', seiz_time[1]
        
        seiz_start = float(seiz_time[0])
        seiz_stop = float(seiz_time[0]) + float(seiz_time[1])
        
        seiz_list.append(seiz_start)
        seiz_list.append(seiz_stop)
    
    ## Add null element at the end of the list to indicate there is no more seizure events
    #  this null element later helps in decision making process
    seiz_list.append('\0')
    #print seiz_list
    
    ehyp_convert(seiz_list,file_len,file_)
#        print seiz_start, ' seiz_start ', seiz_stop, ' seiz_stop'


def ehyp_convert(seiz_list,file_len,file_):
    open('tmp.x','w').close()
    f = open('tmp.x','a')
    i = 0
    seiz_count = 0
    j = 0
    while i <= int(file_len):
        

        if i == 0 or i ==1:
            i +=1
            continue
        ## Look for the last element of the seizure list to terminate seizure annotation
        #  after this condition is true there is only background annotation left till the end.
        if seiz_list[ seiz_count + j] == "\0":
            print "%d %d bckg"%((i-1)*100000,(i)*100000)
            str ="%d %d bckg\n"%((i-1)*100000,(i)*100000)
            f.write('%s'%str)
            i += 1
            continue
        #print " *** ", int(file_len) , ' i value is ', i
        #if (i >= seiz_start and i <seiz_stop) :

            

        if (i >= int(seiz_list[seiz_count + j] + 1)) and (i <= int(seiz_list[seiz_count + j + 1])):
            
            print "%d %d seiz"%((i-1)*100000,(i)*100000)
            str = "%d %d seiz\n"%((i-1)*100000,(i)*100000)
            f.write('%s'%str)

            #print " if decisions ", i+1 , ' ', "seiz_list[seiz_count + j]  " ,seiz_list[seiz_count + j]
            #print " i value is ", i, " seiz[seiz_count + j] ", seiz_list[seiz_count + j], " seizcount + j + 1 " , seiz_list[seiz_count+j+1] 
            i += 1
            
            ## If there is a Last second of the seizure event, this condition will be true..
            #  j will increment by 2 in that condition to get next seizure start time
            if ((i) == seiz_list[seiz_count + j +1] + 1):
                #print "#######################"
                #print "seiz_list[seiz_count + j +1] " , seiz_list[seiz_count+j+1]
                j += 2

                #print "updated _seiz_list[seiz_count + j +1] " , seiz_list[seiz_count+j+1]
        elif (i <= int(seiz_list[seiz_count + j])): # and (i > int(seiz_list[seiz_count + j+1])):
            print "%d %d bckg"%((i-1)*100000,(i)*100000)
            str = "%d %d bckg\n"%((i-1)*100000,(i)*100000)
            f.write('%s'%str)
            #if i == seiz_list[seiz_count + 2]:
            #    j += 1
            i += 1






    ehyp_file = file_.split(r'.')
    #ehyp_file = ehyp_file[-2] + ".ehyp"
    #ehyp_file = ehyp_file.replace("lay","ehyp")
    ehyp_file[-1] = ".ehyp"
    ehyp_file = ehyp_file[0] + '.' + ehyp_file[1] + '.'  + ehyp_file[2] + ehyp_file[3]


    print ehyp_file
    f.close()
    cmd = "cat tmp.x >%s"%ehyp_file
    print "for file ", file_, "  ", cmd

    cmmd = os.system('%s'%cmd)

# remove j or seiz count later .. both are not necessary when using if for seiz increment




def file_length_header(lay_filename,edflist):
    #convert file from lay to edf
    file_tree = lay_filename.split(r'/')
    file_tree[-1] = file_tree[-1].split('.')[0]+".edf"
    relative_address = r"/".join([file_tree[-3],file_tree[-2],file_tree[-1]])
    #print relative_address
    tuh_edf = open(edflist,'r').read()
    edf_files = tuh_edf.split('\n')
    for edf_file in edf_files:
    
        if edf_file=="":
            break
        if relative_address in edf_file:
            
            cmd = "nedc_print_header %s>./tmp.xx"%edf_file
            cmd = os.system('%s'%cmd)
            readhdr = open('tmp.xx','r').read()
            hdrlines = readhdr.split('\n')
            #print hdrlines
            
            for line in hdrlines:
                #print line,"\n"
                if line=="processed 1 out of 1 files successfully":
                    #print "**********"
                    break
                if 'ghdi_num_recs' in line:
                    #print "*************************"
                    rectime = line.split()
                    rectime[2] = rectime[2].strip('[').strip(']')
                    #print rectime
            total_recording_time = rectime[2]
            #print total_recording_time
    return int(total_recording_time)

    

if __name__=="__main__":file_process(sys.argv[1],sys.argv[2])
