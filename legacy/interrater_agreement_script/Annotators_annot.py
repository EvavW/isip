import os
class annot_info(object):

    def __init__(self,name,annot_file):
        self.name = name
        self.annot_file = annot_file

    def __str__(self):
        return str(self.name)

class annot_array(object):
    def __init__(self,array):
        self.array = array

    def check_seiz_on_line(self,line):
        ## this method would check whether perticular line sent from .rec files
        ## contains seizure class or not, if yes then it return line 
        self.line_info = line.split(',')

        if int(self.line_info[3]) >= 7 and int(self.line_info[3]) < 18:
            return line
        else:
            return None


class compare_annotation_files(object):

    def __init__(self):

        self.total_FA = 0
        self.total_Miss = 0
        self.total_Hit = 0
        self.tolerance = 0
    ## define a function which can compare two annotation files (Lab overall files assumed)
    ## and figure out the Miss and False Alarm rate for each file
    #

    def accumulate_annotation_for_fully_annotated_files(self,ref_file):
        ## We only care about the class values from what point its value changes, and store the
        ## time stamp. That way we can 
        op_ref = open(ref_file,'r').read()
        ref_file_info = op_ref.split('\n')

        annotation_array = [0]
        
        ref_class = "bckg"            ## define a default class name as bckg
        ref_toggle_flag = False

        count = 0
        new_ref_value = None

        for ref_line in ref_file_info:
            if ref_line == '':
                annotation_array.append(start_time)
                break

            keys_ref_line = ref_line.split('\t')
            class_name = keys_ref_line[2]
            start_time = keys_ref_line[0]
            stop_time = keys_ref_line[1]

            new_ref_value = class_name.strip()

            if count == 0:
                prev_ref_value = class_name.strip()
                new_ref_value = prev_ref_value

            if new_ref_value == prev_ref_value:
                ref_toggle_flag = False
                prev_ref_value = class_name.strip()
            else:
                ref_toggle_flag = True
                prev_ref_value = class_name.strip()

            if ref_toggle_flag == True:

                annotation_array.append(start_time)

            count += 1
            

        return annotation_array

    def separate_class_fields_for_start_stop_time(self, fully_annotated_array):

        file_start_time = int(fully_annotated_array[0])
        file_stop_time = int(fully_annotated_array[-1])
        
        i = 0
        seiz_start_time_array = []
        seiz_stop_time_array = []

        while i < len(fully_annotated_array):
            
            if i % 2 == 0:
                if i == 0 or i == len(fully_annotated_array):
                    i += 1
                    continue
                seiz_stop_time_array.append(int(fully_annotated_array[i]))
                i += 1
            else:
                if i == len(fully_annotated_array)-1:
                    i += 1
                    continue
                seiz_start_time_array.append(int(fully_annotated_array[i]))
                i += 1
        
        return seiz_start_time_array, seiz_stop_time_array, file_start_time, file_stop_time



    def compare_annotation_for_fully_annotated_files(self, ref_file, hyp_file):

        ref_file_annotation_array = self.accumulate_annotation_for_fully_annotated_files(ref_file)
        self.ref_seiz_start_time_array, self.ref_seiz_stop_time_array, self.ref_start_time, self.ref_stop_time = self.separate_class_fields_for_start_stop_time(ref_file_annotation_array)

        hyp_file_annotation_array = self.accumulate_annotation_for_fully_annotated_files(hyp_file)
        self.hyp_seiz_start_time_array, self.hyp_seiz_stop_time_array, self.hyp_start_time, self.hyp_stop_time = self.separate_class_fields_for_start_stop_time(hyp_file_annotation_array)

        self.ref_index = 0
        self.hyp_index = 0

        hit = 0
        Miss = 0
        FA = 0


        i = 0

        while i < len(self.ref_seiz_start_time_array):

            
        ## The conditions here considered are:                                                                                                                           
        ##            <------------>          <---------->                                                                                                               
        ##        <----->                                                                                                                                                
        ##        <-------------------->                                                                                                                                 
        ##   <--->                                                                                                                                                       
        ##        <----------------------------------->                                                                                                                  
        ##        <------------------------------------------->                                                                                                          
                                                                                                                                                                         
        ##        <-------> <-->                                                                             
        ##        <-------> <----------->........................................................ confirm this


            if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                break
            
            print " Loop begin"

            print self.ref_seiz_start_time_array
            print self.ref_seiz_stop_time_array
            print self.hyp_seiz_start_time_array
            print self.hyp_seiz_stop_time_array
            print '\n'
    
            ## consider all the situations where start time of hyp file is prior to ref file
            #
            if self.hyp_seiz_start_time_array[self.hyp_index] <= self.ref_seiz_start_time_array[self.ref_index]:
                ## condition --> 1
                if self.hyp_seiz_stop_time_array[self.hyp_index] <= self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_start_time_array[self.ref_index]:
                    ## handle multiple hyp events inside one ref event
                    ## Loop condition --> 1
                    while self.hyp_seiz_stop_time_array[self.hyp_index] <= self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] <= self.ref_seiz_start_time_array[self.ref_index]:

                        print " loop condition --> 1"
#                        import pdb;pdb.set_trace()
                        del self.hyp_seiz_start_time_array[self.hyp_index]
                        del self.hyp_seiz_stop_time_array[self.hyp_index]

                        if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                            break
                        
                        ## Loop condition --> 2
                        if self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_stop_time_array[self.ref_index]:

                            print " loop condition --> 2"

                            if int(self.hyp_seiz_stop_time_array[self.hyp_index]) - int(self.ref_seiz_stop_time_array[self.ref_index]) > self.tolerance:
                                FA += 1
                            del self.hyp_seiz_start_time_array[self.hyp_index]
                            del self.hyp_seiz_stop_time_array[self.hyp_index]


                            ### should this indent be one less or not.. check with special condition satiesfying this..
                            if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                                break

                    del self.ref_seiz_start_time_array[self.ref_index]
                    del self.ref_seiz_stop_time_array[self.ref_index]
                    hit += 1

                    print ' condition --> 1 '
                    print self.ref_seiz_start_time_array
                    print self.ref_seiz_stop_time_array
                    print self.hyp_seiz_start_time_array
                    print self.hyp_seiz_stop_time_array
                    print '\n'

                ## in case all annotations are accurately matched up..
                #
                elif self.hyp_seiz_stop_time_array[self.hyp_index] == self.ref_seiz_stop_time_array[self.ref_index]:
                    hit += 1
                    print "elif of condition 1 "

                    del self.ref_seiz_start_time_array[self.ref_index]
                    del self.ref_seiz_stop_time_array[self.ref_index]
                    del self.hyp_seiz_start_time_array[self.hyp_index]
                    del self.hyp_seiz_stop_time_array[self.hyp_index]

                if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index :
                    break
                
                ## condition --> 2
                try:
                    if self.hyp_seiz_stop_time_array[self.hyp_index] <= self.ref_seiz_start_time_array[self.ref_index + 1] and self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_stop_time_array[self.ref_index]:
                        hit += 1
                        
                        if int(self.hyp_seiz_stop_time_array[self.hyp_index]) - int(self.ref_seiz_start_time_array[self.ref_index]) > self.tolerance:
                            FA += 1
                        
                        del self.hyp_seiz_start_time_array[self.hyp_index]
                        del self.hyp_seiz_stop_time_array[self.hyp_index]

                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]

                        print ' condition --> 2a '
                        print self.ref_seiz_start_time_array
                        print self.ref_seiz_stop_time_array
                        print self.hyp_seiz_start_time_array
                        print self.hyp_seiz_stop_time_array
                        print '\n'

                    if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index :
                        break


                except:
                    if self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] <= self.ref_stop_time:
                        hit += 1
                        
                        if int(self.hyp_seiz_stop_time_array[self.hyp_index]) - int(self.ref_seiz_start_time_array[self.ref_index]) > self.tolerance:
                            FA += 1
                        
                        del self.hyp_seiz_start_time_array[self.hyp_index]
                        del self.hyp_seiz_stop_time_array[self.hyp_index]

                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]

                        print ' condition --> 2b '
                        print self.ref_seiz_start_time_array
                        print self.ref_seiz_stop_time_array
                        print self.hyp_seiz_start_time_array
                        print self.hyp_seiz_stop_time_array
                        print '\n'

                    if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index :
                        break
                        
                        
                ## condition --> 3
                if self.hyp_seiz_stop_time_array[self.hyp_index] < self.ref_seiz_start_time_array[self.ref_index]:
                    ## skip the FA annotation of hyp file and count these entries at the end to calculate total
                    ## FA from hyp file
                    #
                    self.hyp_index += 1
                    ## When this condition is true, it means that there is more entries in hyp file than ref files
                    ## so decrement the counter by 1, to loop through all the ref entries..
                    #
                    i -= 1
                    print ' condition --> 3 '
                    print ' hyp index is ', self.hyp_index

                print self.ref_seiz_start_time_array
                print self.ref_seiz_stop_time_array
                print self.hyp_seiz_start_time_array
                print self.hyp_seiz_stop_time_array
                print '\n'



                ## condition --> 4
                try:
                    if self.hyp_seiz_stop_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index + 1] and self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_start_time_array[self.ref_index + 1]:

                        hit += 2
                        if int(self.ref_seiz_start_time_array[self.ref_index + 1]) - int(self.ref_seiz_stop_time_array[self.ref_index]) > self.tolerance:
                            FA += 1

                        del self.hyp_seiz_start_time_array[self.hyp_index]
                        del self.hyp_seiz_stop_time_array[self.hyp_index]

                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]
                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]

                        print ' condition --> 4 '
                        print self.ref_seiz_start_time_array
                        print self.ref_seiz_stop_time_array
                        print self.hyp_seiz_start_time_array
                        print self.hyp_seiz_stop_time_array
                        print '\n'

                    if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index :
                        break

                    
                except:
                    print " except 1 is called \n\n"
                    i -= 1
                    continue
                    pass

                ## condition --> 5
                try:
                    if self.hyp_seiz_stop_time_array[self.hyp_index] >= self.ref_seiz_stop_time_array[self.ref_index + 1] and self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_start_time_array[self.ref_index]:

                        hit += 2
                        if int(self.ref_seiz_start_time_array[self.ref_index + 1]) - int(self.ref_seiz_stop_time_array[self.ref_index]) > self.tolerance:
                            FA += 1

                        del self.hyp_seiz_start_time_array[self.hyp_index]
                        del self.hyp_seiz_stop_time_array[self.hyp_index]

                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]
                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]

                        print ' condition --> 5 '
                        print self.ref_seiz_start_time_array
                        print self.ref_seiz_stop_time_array
                        print self.hyp_seiz_start_time_array
                        print self.hyp_seiz_stop_time_array
                        print '\n'

                    if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index :
                        break


                except:
                    print ' except 2 is called '
                    i -= 1
                    continue
                    pass
#---------------------------------------------------------------------------------------------------------------#

         ## the condition here considered are:                                                                                                                                             
         ##          <-------------->           <---------->                                                                                                                               
         ##             <--->                                                                                                                                                              
         ##             <------------->                                                                                                                                                    
         ##                                        <-->                                                                                                                                    
         ##                       <------------------>                                                                                                                                     
         ##                     <-------------------------------->                                                                                                                        
                                                                                                                                                                                           
         ##              <->  <->  situation has not been included in the code..                                                                                                           
         ##               <-->  <--------->                                                                                                                                                


            elif self.hyp_seiz_start_time_array[self.hyp_index] > self.ref_seiz_start_time_array[self.ref_index]:
                ## condition --> 1
                if self.hyp_seiz_stop_time_array[self.hyp_index] <= self.ref_seiz_stop_time_array[self.ref_index]:
                    ## handle multiple hyp events inside one ref event
                    ## Loop condition --> 1
                    while self.hyp_seiz_stop_time_array[self.hyp_index] <= self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] > self.ref_seiz_start_time_array[self.ref_index]:
#                        import pdb;pdb.set_trace()
                        print "## inside loop --> 1"
                        del self.hyp_seiz_start_time_array[self.hyp_index]
                        del self.hyp_seiz_stop_time_array[self.hyp_index]

                        if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index :
                            break


                        ## Loop condition --> 2
                        if self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_stop_time_array[self.ref_index]:

                            print "## inside loop --> 2"

                            if int(self.hyp_seiz_stop_time_array[self.hyp_index]) - int(self.ref_seiz_stop_time_array[self.ref_index]) > self.tolerance:
                                FA += 1
                            del self.hyp_seiz_start_time_array[self.hyp_index]
                            del self.hyp_seiz_stop_time_array[self.hyp_index]

                            if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0:
                                break

                        
                    del self.ref_seiz_start_time_array[self.ref_index]
                    del self.ref_seiz_stop_time_array[self.ref_index]
                    hit += 1
                    
                    print '## condition --> 1'
                    print self.ref_seiz_start_time_array
                    print self.ref_seiz_stop_time_array
                    print self.hyp_seiz_start_time_array
                    print self.hyp_seiz_stop_time_array
                    print '\n'

                if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index :
                    break
                
                ## condition --> 2
                try:
                    if self.hyp_seiz_start_time_array[self.hyp_index] > self.ref_seiz_start_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index] and  self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] < self.ref_seiz_start_time_array[self.ref_index + 1]:
                        hit += 1

                        if int(self.hyp_seiz_stop_time_array[self.hyp_index]) - int(self.ref_seiz_stop_time_array[self.ref_index]) > self.tolerance:
                            FA += 1

                        del self.hyp_seiz_start_time_array[self.hyp_index]
                        del self.hyp_seiz_stop_time_array[self.hyp_index]
                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]

                        print '## condition --> 2a '
                        print self.ref_seiz_start_time_array
                        print self.ref_seiz_stop_time_array
                        print self.hyp_seiz_start_time_array
                        print self.hyp_seiz_stop_time_array
                        print '\n'

                    if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index :
                        break

                except:
                    if self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] < self.ref_stop_time:
                        hit += 1

                        if int(self.hyp_seiz_stop_time_array[self.hyp_index]) - int(self.ref_stop_time) > self.tolerance:
                            FA += 1

                        del self.hyp_seiz_start_time_array[self.hyp_index]
                        del self.hyp_seiz_stop_time_array[self.hyp_index]
                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]
                            
                        print '## condition --> 2b '
                        print self.ref_seiz_start_time_array
                        print self.ref_seiz_stop_time_array
                        print self.hyp_seiz_start_time_array
                        print self.hyp_seiz_stop_time_array
                        print '\n'

                    if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index :
                        break


                ## condition --> 3
                if self.hyp_seiz_start_time_array[self.hyp_index] > self.ref_seiz_stop_time_array[self.ref_index]:
                    Miss += 1

                    self.ref_index += 1

                    print '## condition --> 3'
                    print ' hyp index is ', self.hyp_index
                    print self.ref_seiz_start_time_array[self.ref_index]
#                    import pdb;pdb.set_trace()
                    continue


                ## condition --> 4
                try:
                    if self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_start_time_array[self.ref_index + 1]  and self.hyp_seiz_stop_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index + 1]:
                        hit += 2

                        if int(self.ref_seiz_start_time_array[self.ref_index + 1]) - int(self.ref_seiz_stop_time_array[self.ref_index]) > self.tolerance:
                            FA += 1

                        del self.hyp_seiz_start_time_array[self.hyp_index]
                        del self.hyp_seiz_stop_time_array[self.hyp_index]

                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]
                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]

                        print '## condition --> 4'
                        print self.ref_seiz_start_time_array
                        print self.ref_seiz_stop_time_array
                        print self.hyp_seiz_start_time_array
                        print self.hyp_seiz_stop_time_array
                        print '\n'

                    if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index :
                        break
                        

                except:
                    print "## except 1 is called.. \n\n"
#                    i -= 1
#                    continue
                    pass


                ## condition --> 5
                try:
                    if self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_stop_time_array[self.ref_index + 1]:
                        hit += 2

                        if int(self.ref_seiz_start_time_array[self.ref_index + 1]) - int(self.ref_seiz_stop_time_array[self.ref_index]) > self.tolerance:
                            FA += 1

                        del self.hyp_seiz_start_time_array[self.hyp_index]
                        del self.hyp_seiz_stop_time_array[self.hyp_index]

                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]
                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]

                        print '## condition --> 5'
                        print self.ref_seiz_start_time_array
                        print self.ref_seiz_stop_time_array
                        print self.hyp_seiz_start_time_array
                        print self.hyp_seiz_stop_time_array
                        print '\n'

                    if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index :
                        break

                except:
                    print "## except 2 is called \n\n"
#                    i -= 1
#                    continue

                    pass

            i += 1
            print "end and i value is " , i

        print 'eventually ref and hyp indexes are '
        print self.ref_seiz_start_time_array
        print self.ref_seiz_stop_time_array
        print self.hyp_seiz_start_time_array
        print self.hyp_seiz_stop_time_array

        Miss += len(self.ref_seiz_start_time_array)
        FA += len(self.hyp_seiz_start_time_array)

        return hit, Miss, FA
            

    #############################################################################################################
    # def handle_multiple_hyp_events_in_one_ref_event(self):                                                    #
    #     pass                                                                                                  #
    #     additional_hits = 0                                                                                   #
    #     additional_FA = 0                                                                                     #
    #                                                                                                           #
    #     while self.hyp_seiz_stop_time_array[self.hyp_index] <= self.ref_seiz_stop_time_array[self.ref_index]: #
    #         break                                                                                             #
    #############################################################################################################



    def prepare_annotator_filelist(self,annotator_names, annotators_filelists, reference_name ):
    ## This function prepares the list of files which includes same type of directory structure
    ## i.e. default   ( patient_ID / session_numbers / file_name.lab_ov_extension)
    ## through such structure it would become handy to compare files with other annotators
    #
    
        
        ## get the index of refenrence name w.r.t which all other annotators' annotations
        ## would be assessed/compared..
        #
        
        if reference_name in annotator_names:
            reference_name_index =  annotator_names.index(reference_name)


        ## collect name and other information(filelists) of reference annotator
        #
        
        self.reference_name = reference_name
        self.reference_filelist = annotators_filelists[reference_name_index]


        self.ref_key_pathlists = []  ## collect all similar file paths for reference (i.e. patient/sess/filename) to compare it with individual annotator
        
        for _ref_files in self.reference_filelist:
            _ref_file_keywords = self.split_filepath(_ref_files)
            self.ref_key_pathlists.append(_ref_file_keywords)

        print " ref_key_pathlists  ", self.ref_key_pathlists
        
        ## assess annotation by looping through every single annotator and compare
        ## their annotation w.r.t. reference annotator.

        ## looping through two lists at a same time using zip
        ## and collecting keypaths for each annotator
        #

        result_dictionary = {}   ## define a dictionary to send back results to the main function, this dictionary would contain information of annotators performance numerically
        
        for _annotator, _filelist in zip(annotator_names,annotators_filelists):
            print "*******  ", _annotator
            if _annotator == reference_name:
                continue

            key_pathlists = []   ## collect all similar file paths (i.e. 00000032/s01_xx_xxx/a_x.lab_ov)                        
            for _file in _filelist:
                _file_keywords = self.split_filepath(_file)

                ## check if file exists in reference list or not
                #
                if _file_keywords in self.ref_key_pathlists:
                    print " found the file for annotator and ref accordingly "
                    print _file_keywords, ', ' , self.ref_key_pathlists

                    ## find out the index of the file in ref_lists which corresponds to recent annotation file
                    compared_ref_file_index = self.ref_key_pathlists.index(_file_keywords)

                    self.calc_hits_miss_FA_from_ann_files(_file, compared_ref_file_index)
                    print self.total_Hit, " %s hits"%_annotator
                    print self.total_Miss, " %s misses"%_annotator
                    print self.total_FA, "%s FA"%_annotator

                    
                    
                ## in case if file does not exist in reference filelist then calculate FAs
                else:
                    self.handle_FA(_file)
                    pass

            ## collect individual annotators numerical performance in a dictionary
            #
            exec("result_dictionary['%s_results'] = '%s,%s,%s'"%(_annotator,self.total_Hit,self.total_Miss,self.total_FA))
                
            self.total_Hit = 0
            self.total_Miss = 0
            self.total_FA = 0
            
        return result_dictionary
            
###                key_pathlists.append(_file_keywords)
###            print key_pathlists, "  key paths for annotator:  ", _annotator



    def split_filepath(self,_files):

            ## normalize(make it raw) the path of the file, so that we can use
            ## os.split(sep) to split the path structure
            #
                _file_normpath = os.path.normpath(_files)
                _file_keywords = _file_normpath.split(os.sep)
                try:
                    key = r'/'.join([_file_keywords[-3],_file_keywords[-2],_file_keywords[-1]])
                except:
                    total_indexes = len(_file_keywords)
                    i = 1
                    key = []

                    while i < len(_file_keywords):
                        key.append(_file_keywords[i])
                        i += 1
                        
                return key

    def calc_hits_miss_FA_from_ann_files(self,filename_to_compare, *index):
        print  "inside calc_hits fuction\n"
        print filename_to_compare
   
        ref_index = index[0]

        ## send both reference and hypothesis files for comparison to the fuction
        ## called 
        Hit, Miss, FA = self.compare_annotation_for_fully_annotated_files(self.reference_filelist[ref_index],filename_to_compare)

        self.total_Hit += Hit
        self.total_Miss += Miss
        self.total_FA += FA

        print " total hits are ", self.total_Hit
        print " total miss are ", self.total_Miss
        print " total FA are ", self.total_FA

        '''
        except:
            FA = self.handle_FA(filename_to_compare)
            print "###########################################################"

        print " Hits are --->>> " , Hit
        print " Miss are --->>> " , Miss
        print " FA are   --->>> " , FA
'''            
    def handle_FA(self,FA_file):

    ## THis function is triggered when there is no reference file assigned similar to this, that means,
    ## all annotation assigned to this file are wrong and should be considered as FA.
    ## calculate total number of events from this file and return false alarm events per file
        print " this is a false alarm file--->>> ", FA_file
