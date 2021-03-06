import os,sys
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

        pass
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

            keys_ref_line = ref_line.split()
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

        file_start_time = int(fully_annotated_array[0])/100000
        file_stop_time = int(fully_annotated_array[-1])/100000
        
        i = 0
        seiz_start_time_array = []
        seiz_stop_time_array = []

        while i < len(fully_annotated_array):
            
            if i % 2 == 0:
                if i == 0 or i == len(fully_annotated_array):
                    i += 1
                    continue
                seiz_stop_time_array.append(int(fully_annotated_array[i])/100000)
                i += 1
            else:
                if i == len(fully_annotated_array)-1:
                    i += 1
                    continue
                seiz_start_time_array.append(int(fully_annotated_array[i])/100000)
                i += 1
        
        return seiz_start_time_array, seiz_stop_time_array, file_start_time, file_stop_time



    def compare_annotation_for_fully_annotated_files(self, ref_file, hyp_file):

        ref_file_annotation_array = self.accumulate_annotation_for_fully_annotated_files(ref_file)
        self.ref_seiz_start_time_array, self.ref_seiz_stop_time_array, self.ref_start_time, self.ref_stop_time = self.separate_class_fields_for_start_stop_time(ref_file_annotation_array)
        ref_total_events = len(self.ref_seiz_start_time_array)

        ## apply delta value to the reference annotations
        #

        self.apply_delta_value_to_reference_file()

        ## seizure start and stop times have been updated according to delta value
        #
        
        
        hyp_file_annotation_array = self.accumulate_annotation_for_fully_annotated_files(hyp_file)
        self.hyp_seiz_start_time_array, self.hyp_seiz_stop_time_array, self.hyp_start_time, self.hyp_stop_time = self.separate_class_fields_for_start_stop_time(hyp_file_annotation_array)


        ## calculate total Background epochs for reference and hypothesis files for calculation of Specificity
        #

        ## for reference file
        #
        self.ref_bckg_epochs = self.calc_bckg_epochs(self.ref_seiz_start_time_array, self.ref_seiz_stop_time_array, self.ref_start_time, self.ref_stop_time)

        ## for hypothesis file
        #
        self.hyp_bckg_epochs = self.calc_bckg_epochs(self.hyp_seiz_start_time_array, self.hyp_seiz_stop_time_array, self.hyp_start_time, self.hyp_stop_time)

        ## Bckg for both ref and hyp have been collected

        self.ref_index = 0
        self.hyp_index = 0

        hit = 0
        Miss = 0
        FA = 0


        i = 0

        while 1:

            
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


                    del self.hyp_seiz_start_time_array[self.hyp_index]
                    del self.hyp_seiz_stop_time_array[self.hyp_index]
                    print ' condition --> 1 first event'
                    print self.ref_seiz_start_time_array
                    print self.ref_seiz_stop_time_array
                    print self.hyp_seiz_start_time_array
                    print self.hyp_seiz_stop_time_array
                    print '\n'

                    if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]
                        hit += 1

                        print ' condition --> 1 '
                        print self.ref_seiz_start_time_array
                        print self.ref_seiz_stop_time_array
                        print self.hyp_seiz_start_time_array
                        print self.hyp_seiz_stop_time_array
                        print '\n'
                        break


                    ## handle multiple hyp events inside one ref event
                    ## Loop condition --> 1
                    while  self.hyp_seiz_start_time_array[self.hyp_index] <= self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] <= self.ref_seiz_stop_time_array[self.ref_index]:

                        print " loop condition --> 1"

                        del self.hyp_seiz_start_time_array[self.hyp_index]
                        del self.hyp_seiz_stop_time_array[self.hyp_index]
                        
                        print ' condition --> 1 '
                        print self.ref_seiz_start_time_array
                        print self.ref_seiz_stop_time_array
                        print self.hyp_seiz_start_time_array
                        print self.hyp_seiz_stop_time_array
                        print '\n'

                        print "ref index is ", self.ref_index , " and ", " hyp index is ", self.hyp_index
                        if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                            break
                        
                        ## Loop condition --> 2
                        if self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] <= self.ref_seiz_stop_time_array[self.ref_index]:

                            print " loop condition --> 2"

                            if int(self.hyp_seiz_stop_time_array[self.hyp_index]) - int(self.ref_seiz_stop_time_array[self.ref_index]) > self.tolerance:
                                FA += 1
                            del self.hyp_seiz_start_time_array[self.hyp_index]
                            del self.hyp_seiz_stop_time_array[self.hyp_index]

                            print "ref index is ", self.ref_index , " and ", " hyp index is ", self.hyp_index
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

                if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                    break
                
                ## condition --> 2
                try:
                    if self.hyp_seiz_start_time_array[self.hyp_index] <= self.ref_seiz_start_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_start_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] <= self.ref_seiz_start_time_array[self.ref_index + 1] and self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_stop_time_array[self.ref_index]:
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


                    ################################################################################################################################################################################################################################################################################################################
                    # elif self.hyp_seiz_start_time_array[self.hyp_index] <= self.ref_seiz_start_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_start_time_array[self.ref_index]  and self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_stop_time_array[self.ref_index]: #
                    #                                                                                                                                                                                                                                                                                                              #
                    #     hit += 1                                                                                                                                                                                                                                                                                                 #
                    #     ## there should be a very rigorous penalty for this situation, update his later                                                                                                                                                                                                                          #
                    #     #                                                                                                                                                                                                                                                                                                        #
                    #     if int(self.hyp_seiz_stop_time_array[self.hyp_index]) - int(self.ref_seiz_start_time_array[self.ref_index]) > self.tolerance:                                                                                                                                                                            #
                    #         FA += 1                                                                                                                                                                                                                                                                                              #
                    #                                                                                                                                                                                                                                                                                                              #
                    #     del self.hyp_seiz_start_time_array[self.hyp_index]                                                                                                                                                                                                                                                       #
                    #     del self.hyp_seiz_stop_time_array[self.hyp_index]                                                                                                                                                                                                                                                        #
                    #                                                                                                                                                                                                                                                                                                              #
                    #     del self.ref_seiz_start_time_array[self.ref_index]                                                                                                                                                                                                                                                       #
                    #     del self.ref_seiz_stop_time_array[self.ref_index]                                                                                                                                                                                                                                                        #
                    #                                                                                                                                                                                                                                                                                                              #
                    #     print ' condition --> 2a elif'                                                                                                                                                                                                                                                                           #
                    #     print self.ref_seiz_start_time_array                                                                                                                                                                                                                                                                     #
                    #     print self.ref_seiz_stop_time_array                                                                                                                                                                                                                                                                      #
                    #     print self.hyp_seiz_start_time_array                                                                                                                                                                                                                                                                     #
                    #     print self.hyp_seiz_stop_time_array                                                                                                                                                                                                                                                                      #
                    #     print '\n'                                                                                                                                                                                                                                                                                               #
                    ################################################################################################################################################################################################################################################################################################################
                        
                    if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                        break


                except:
                    if self.hyp_seiz_start_time_array[self.hyp_index] <= self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] <= self.ref_stop_time:
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

                    if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                        break
                        
                        
                ## condition --> 3
                if self.hyp_seiz_stop_time_array[self.hyp_index] <= self.ref_seiz_start_time_array[self.ref_index]:
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

                if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                    break




                ## condition --> 4
                try:
                    if self.hyp_seiz_start_time_array[self.hyp_index] <= self.ref_seiz_start_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index] and  self.hyp_seiz_stop_time_array[self.hyp_index] >= self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] >= self.ref_seiz_start_time_array[self.ref_index + 1] and self.hyp_seiz_stop_time_array[self.hyp_index] <= self.ref_seiz_stop_time_array[self.ref_index + 1]:


                        if int(self.ref_seiz_start_time_array[self.ref_index + 1]) - int(self.ref_seiz_stop_time_array[self.ref_index]) > self.tolerance:
                            FA += 1


                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]



                        print ' condition --> 4 '
                        print self.ref_seiz_start_time_array
                        print self.ref_seiz_stop_time_array
                        print self.hyp_seiz_start_time_array
                        print self.hyp_seiz_stop_time_array
                        print '\n'
                        
                        if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                            hit += 1
                            print ' condition --> 4 only one event '
                            print self.ref_seiz_start_time_array
                            print self.ref_seiz_stop_time_array
                            print self.hyp_seiz_start_time_array
                            print self.hyp_seiz_stop_time_array
                            print '\n'
                            break

                        loop_index = 0
                        while self.hyp_seiz_stop_time_array[self.hyp_index] >= self.ref_seiz_start_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index]:
                            print " loop condition --> 4 "
                            del self.hyp_seiz_start_time_array[self.hyp_index]
                            del self.hyp_seiz_stop_time_array[self.hyp_index]
                            
                            loop_index += 1
                            print self.ref_seiz_start_time_array
                            print self.ref_seiz_stop_time_array
                            print self.hyp_seiz_start_time_array
                            print self.hyp_seiz_stop_time_array
                            print '\n'

                            if self.check_end_of_array():
                                break

                        hit = loop_index + 1

                        print self.ref_seiz_start_time_array
                        print self.ref_seiz_stop_time_array
                        print self.hyp_seiz_start_time_array
                        print self.hyp_seiz_stop_time_array
                        print '\n'

                        if self.check_end_of_array():
                            break
                        
                    
                except:
                    if self.hyp_seiz_start_time_array[self.hyp_index] <= self.ref_seiz_start_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index] and  self.hyp_seiz_stop_time_array[self.hyp_index] >= self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] <= self.ref_stop_time:
                        print "except for condition 4 is called "
                        
                        del self.hyp_seiz_start_time_array[self.hyp_index]
                        del self.hyp_seiz_stop_time_array[self.hyp_index]
                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]

                        if self.check_end_of_array():
                            break


                ## condition --> 5
                try:

                    if self.hyp_seiz_start_time_array[self.hyp_index] <= self.ref_seiz_start_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] >= self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] >= self.ref_seiz_stop_time_array[self.ref_index + 1]:


                        if int(self.ref_seiz_start_time_array[self.ref_index + 1]) - int(self.ref_seiz_stop_time_array[self.ref_index]) > self.tolerance:
                            FA += 1

                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]
                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]

                        print ' condition --> 5 first event'
                        print self.ref_seiz_start_time_array
                        print self.ref_seiz_stop_time_array
                        print self.hyp_seiz_start_time_array
                        print self.hyp_seiz_stop_time_array
                        print '\n'

                        if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                            hit += 2

                            print ' condition --> 5 first event'
                            print self.ref_seiz_start_time_array
                            print self.ref_seiz_stop_time_array
                            print self.hyp_seiz_start_time_array
                            print self.hyp_seiz_stop_time_array
                            print '\n'

                            break
                        
                        loop_index = 0
                        
                        while self.hyp_seiz_stop_time_array[self.hyp_index] >= self.ref_seiz_start_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index]:
                            print " loop condition --> 5 "

                            del self.ref_seiz_start_time_array[self.ref_index]
                            del self.ref_seiz_stop_time_array[self.ref_index]
                            loop_index += 1
                            
                            print self.ref_seiz_start_time_array
                            print self.ref_seiz_stop_time_array
                            print self.hyp_seiz_start_time_array
                            print self.hyp_seiz_stop_time_array
                            print '\n'

                            if self.check_end_of_array():
                                break

                        del self.hyp_seiz_start_time_array[self.hyp_index]
                        del self.hyp_seiz_stop_time_array[self.hyp_index]
                        hit += loop_index + 2   ## two hits from before the loop condition 5

                        print " condition 5 after loop "
                        print self.ref_seiz_start_time_array
                        print self.ref_seiz_stop_time_array
                        print self.hyp_seiz_start_time_array
                        print self.hyp_seiz_stop_time_array
                        print '\n'
                    
                        if self.check_end_of_array():
                            break

                except:
                    ## all the condition 5 excepts must be verified again.. Seems like it could create problem with condition 2s                    
                    print ' except 2 is called '


                    if self.hyp_seiz_start_time_array[self.hyp_index] <= self.ref_seiz_start_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] >= self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] >= self.ref_stop_time:


                        if int(self.ref_stop_time) - int(self.ref_seiz_stop_time_array[self.ref_index]) > self.tolerance:
                            FA += 1

                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]
                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]

                        print ' condition --> 5 first event'
                        print self.ref_seiz_start_time_array
                        print self.ref_seiz_stop_time_array
                        print self.hyp_seiz_start_time_array
                        print self.hyp_seiz_stop_time_array
                        print '\n'

                        if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                            hit += 2

                            print ' condition --> 5 first event'
                            print self.ref_seiz_start_time_array
                            print self.ref_seiz_stop_time_array
                            print self.hyp_seiz_start_time_array
                            print self.hyp_seiz_stop_time_array
                            print '\n'

                            break
                        
                        loop_index = 0
                        
                        while self.hyp_seiz_stop_time_array[self.hyp_index] >= self.ref_seiz_start_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index]:
                            print " loop condition --> 5 "

                            del self.ref_seiz_start_time_array[self.ref_index]
                            del self.ref_seiz_stop_time_array[self.ref_index]
                            loop_index += 1
                            
                            print self.ref_seiz_start_time_array
                            print self.ref_seiz_stop_time_array
                            print self.hyp_seiz_start_time_array
                            print self.hyp_seiz_stop_time_array
                            print '\n'

                            if self.check_end_of_array():
                                break

                        del self.hyp_seiz_start_time_array[self.hyp_index]
                        del self.hyp_seiz_stop_time_array[self.hyp_index]
                        hit += loop_index + 2   ## two hits from before the loop condition 5

                        print " condition 5 after loop "
                        print self.ref_seiz_start_time_array
                        print self.ref_seiz_stop_time_array
                        print self.hyp_seiz_start_time_array
                        print self.hyp_seiz_stop_time_array
                        print '\n'
                    
                        if self.check_end_of_array():
                            break



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


            elif self.hyp_seiz_start_time_array[self.hyp_index] >= self.ref_seiz_start_time_array[self.ref_index]:
                ## condition --> 1
                if self.hyp_seiz_stop_time_array[self.hyp_index] <= self.ref_seiz_stop_time_array[self.ref_index]:
                    ## handle multiple hyp events inside one ref event
                    ## Loop condition --> 1
                    while self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] > self.ref_seiz_start_time_array[self.ref_index]:

                        print "## inside loop --> 1"
                        del self.hyp_seiz_start_time_array[self.hyp_index]
                        del self.hyp_seiz_stop_time_array[self.hyp_index]

                        if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                            break

                        ## Loop condition --> 2
                        if self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_stop_time_array[self.ref_index]:

                            print "## inside loop --> 2"

                            if int(self.hyp_seiz_stop_time_array[self.hyp_index]) - int(self.ref_seiz_stop_time_array[self.ref_index]) > self.tolerance:
                                FA += 1
                            del self.hyp_seiz_start_time_array[self.hyp_index]
                            del self.hyp_seiz_stop_time_array[self.hyp_index]

                            if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
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

                if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                    break
                
                ## condition --> 2
                try:

                    if self.hyp_seiz_start_time_array[self.hyp_index] >= self.ref_seiz_start_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] <= self.ref_seiz_start_time_array[self.ref_index + 1]: ## remove the first condition section; its redundant..
                        

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
                        
                    elif self.hyp_seiz_start_time_array[self.hyp_index] >= self.ref_seiz_start_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_stop_time_array[self.ref_index] :
                        

                        hit += 1
                        ## there should be a harsh penalty for such situation
                        #
                        if int(self.hyp_seiz_stop_time_array[self.hyp_index]) - int(self.ref_seiz_stop_time_array[self.ref_index]) > self.tolerance:
                            FA += 1

                        del self.hyp_seiz_start_time_array[self.hyp_index]
                        del self.hyp_seiz_stop_time_array[self.hyp_index]
                        del self.ref_seiz_start_time_array[self.ref_index]
                        del self.ref_seiz_stop_time_array[self.ref_index]

                        print '## condition --> 2a elif'
                        print self.ref_seiz_start_time_array
                        print self.ref_seiz_stop_time_array
                        print self.hyp_seiz_start_time_array
                        print self.hyp_seiz_stop_time_array
                        print '\n'
                       
                    if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                        break

                except:
                    if self.hyp_seiz_start_time_array[self.hyp_index] >= self.ref_seiz_start_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] <= self.ref_stop_time:
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

                    if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                        break

                ## condition --> 3
                if self.hyp_seiz_start_time_array[self.hyp_index] >= self.ref_seiz_stop_time_array[self.ref_index]:
                    Miss += 1

                    self.ref_index += 1
                    i -= 1

                    print '## condition --> 3'
                    print ' ref index is ', self.ref_index


                if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                    break


                ## condition --> 4
                try:
                    if self.hyp_seiz_start_time_array[self.hyp_index] >= self.ref_seiz_start_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] > self.ref_seiz_start_time_array[self.ref_index + 1]  and self.hyp_seiz_stop_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index + 1]:

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
                        
                    if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                        break


                except:

                    pass

                ## condition --> 5
                try:
                    if self.hyp_seiz_start_time_array[self.hyp_index] >= self.ref_seiz_start_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] >= self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] >= self.ref_seiz_stop_time_array[self.ref_index + 1] and  self.hyp_seiz_stop_time_array[self.hyp_index] <= self.ref_stop_time:

                        if int(self.ref_seiz_start_time_array[self.ref_index + 1]) - int(self.ref_seiz_stop_time_array[self.ref_index]) > self.tolerance:
                            FA += 1

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

                        if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                            hit += 2
                            
                            print '## condition --> 5 first event'
                            print self.ref_seiz_start_time_array
                            print self.ref_seiz_stop_time_array
                            print self.hyp_seiz_start_time_array
                            print self.hyp_seiz_stop_time_array
                            print '\n'

                            break

                        loop_index = 0

                        while self.hyp_seiz_stop_time_array[self.hyp_index] >= self.ref_seiz_start_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index]:
                            print "## loop condition --> 5 "

                            del self.ref_seiz_start_time_array[self.ref_index]
                            del self.ref_seiz_stop_time_array[self.ref_index]
                            loop_index += 1
                            
                            print self.ref_seiz_start_time_array
                            print self.ref_seiz_stop_time_array
                            print self.hyp_seiz_start_time_array
                            print self.hyp_seiz_stop_time_array
                            print '\n'

                            if self.check_end_of_array():
                                break

                        del self.hyp_seiz_start_time_array[self.hyp_index]
                        del self.hyp_seiz_stop_time_array[self.hyp_index]
                        hit += loop_index + 2   ## two hits from before the loop condition 5

                        print "## condition 5 after loop "
                        print self.ref_seiz_start_time_array
                        print self.ref_seiz_stop_time_array
                        print self.hyp_seiz_start_time_array
                        print self.hyp_seiz_stop_time_array
                        print '\n'
                    
                        if self.check_end_of_array():
                            break
                        
                except:
                    ## all the condition 5 excepts must be verified again.. Seems like it could create problem with condition 2s
                    if self.hyp_seiz_start_time_array[self.hyp_index] >= self.ref_seiz_start_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] >= self.ref_seiz_stop_time_array[self.ref_index] and self.hyp_seiz_stop_time_array[self.hyp_index] >= self.ref_stop_time and self.hyp_seiz_stop_time_array[self.hyp_index] <= self.ref_stop_time:

                        if int(self.ref_seiz_start_time_array[self.ref_index + 1]) - int(self.ref_seiz_stop_time_array[self.ref_index]) > self.tolerance:
                            FA += 1

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

                        if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
                            hit += 2
                            
                            print '## condition --> 5 first event'
                            print self.ref_seiz_start_time_array
                            print self.ref_seiz_stop_time_array
                            print self.hyp_seiz_start_time_array
                            print self.hyp_seiz_stop_time_array
                            print '\n'

                            break

                        loop_index = 0

                        while self.hyp_seiz_stop_time_array[self.hyp_index] >= self.ref_seiz_start_time_array[self.ref_index] and self.hyp_seiz_start_time_array[self.hyp_index] < self.ref_seiz_stop_time_array[self.ref_index]:
                            print "## loop condition --> 5 "

                            del self.ref_seiz_start_time_array[self.ref_index]
                            del self.ref_seiz_stop_time_array[self.ref_index]
                            loop_index += 1
                            
                            print self.ref_seiz_start_time_array
                            print self.ref_seiz_stop_time_array
                            print self.hyp_seiz_start_time_array
                            print self.hyp_seiz_stop_time_array
                            print '\n'

                            if self.check_end_of_array():
                                break

                        del self.hyp_seiz_start_time_array[self.hyp_index]
                        del self.hyp_seiz_stop_time_array[self.hyp_index]
                        hit += loop_index + 2   ## two hits from before the loop condition 5

                        print "## condition 5 after loop "
                        print self.ref_seiz_start_time_array
                        print self.ref_seiz_stop_time_array
                        print self.hyp_seiz_start_time_array
                        print self.hyp_seiz_stop_time_array
                        print '\n'
                    
                        if self.check_end_of_array():
                            break
                        ## end of condition 5


            i += 1
            print "end and i value is " , i

        print 'eventually ref and hyp indexes are '
        print self.ref_seiz_start_time_array
        print self.ref_seiz_stop_time_array
        print self.hyp_seiz_start_time_array
        print self.hyp_seiz_stop_time_array

        print "miss value before adding length is ", Miss
        print "fa value before adding length is ", FA

        Miss = self.ref_index + (len(self.ref_seiz_start_time_array) - self.ref_index)
        FA = self.hyp_index + (len(self.hyp_seiz_start_time_array) - self.hyp_index)
        seiz_FA_epochs = self.calc_seiz_FA_epochs(self.hyp_seiz_start_time_array, self.hyp_seiz_stop_time_array)
        
        print ' hit ', hit, ' miss ', Miss, ' FA ', FA
        self.fo.write("\nhit:\t")
        self.fo.write(str(hit))
        self.fo.write("\nMiss:\t")
        self.fo.write(str(Miss))
        self.fo.write("\nFA:\t")
        self.fo.write(str(FA))
        self.fo.write("\n\n\n")

        ## write the seizure Miss for the file
        #
        self.fo.write("Seizure Miss:\n")
        if len(self.ref_seiz_start_time_array) != 0:
            
            for seiz_element_index in range(len(self.ref_seiz_start_time_array)):
                self.fo.write("\t\t\t")
                self.fo.write(str(self.ref_seiz_start_time_array[seiz_element_index]))
                self.fo.write(" -- ")
                self.fo.write(str(self.ref_seiz_stop_time_array[seiz_element_index]))
                self.fo.write("\n")

        else:
            self.fo.write("\t\t\tNone\n")

        ## write the seizure FA for the file
        #
        self.fo.write("Seizure FA:\n")
        if len(self.hyp_seiz_start_time_array) != 0:
            for seiz_element_index in range(len(self.hyp_seiz_start_time_array)):
                self.fo.write("\t\t\t")
                self.fo.write(str(self.hyp_seiz_start_time_array[seiz_element_index]))
                self.fo.write(" -- ")
                self.fo.write(str(self.hyp_seiz_stop_time_array[seiz_element_index]))
                self.fo.write("\n")

        else:
            self.fo.write("\t\t\tNone\n")

        self.fo.write("\n")
        

        
        HMF_list = [hit, Miss, FA]
        return hit, Miss, FA, ref_total_events, self.ref_bckg_epochs,self.hyp_bckg_epochs, seiz_FA_epochs
            


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
            exec("result_dictionary['%s'] = '%s,%s,%s,%s,%s,%s,%s'"%(_annotator,self.total_Hit,self.total_Miss,self.total_FA,self.total_events,self.total_ref_bckg_epochs,self.total_hyp_bckg_epochs,self.total_seiz_FA_epochs))
                
            self.total_Hit = 0
            self.total_Miss = 0
            self.total_FA = 0
            self.total_events = 0
            self.total_ref_bckg_epochs = 0
            self.total_hyp_bckg_epochs = 0
            self.total_seiz_FA_epochs = 0


            
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
                    key = r'/'.join([_file_keywords[-3],_file_keywords[-2],_file_keywords[-1].split('.')[0]])
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
        self.fo.write(filename_to_compare)
        self.fo.write("\n\t")
        
        
        
        ref_index = index[0]

        ## send both reference and hypothesis files for comparison to the fuction
        ## called 
        Hit, Miss, FA, Total_events, ref_bckg_epochs, hyp_bckg_epochs, seiz_FA_epochs = self.compare_annotation_for_fully_annotated_files(self.reference_filelist[ref_index],filename_to_compare)

        self.total_Hit += Hit
        self.total_Miss += Miss
        self.total_FA += FA
        self.total_events += Total_events
        self.total_ref_bckg_epochs += ref_bckg_epochs
        self.total_hyp_bckg_epochs += hyp_bckg_epochs
        self.total_seiz_FA_epochs += seiz_FA_epochs
        
        print " total hits are ", self.total_Hit
        print " total miss are ", self.total_Miss
        print " total FA are ", self.total_FA
        print " total seizure events are " , self.total_events
        print " total ref bckg are ", self.total_ref_bckg_epochs
        print " total hyp bckg are ", self.total_hyp_bckg_epochs
        print " total seiz fa epochs are " , self.total_seiz_FA_epochs
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


    def apply_delta_value_to_reference_file(self):

        for seiz_start_time_index in range(len(self.ref_seiz_start_time_array)):
            if self.ref_seiz_start_time_array[seiz_start_time_index] - self.delta <= self.ref_start_time:
                updated_value = self.ref_start_time
                self.ref_seiz_start_time_array[seiz_start_time_index] = updated_value

            else:
                updated_value = self.ref_seiz_start_time_array[seiz_start_time_index] - self.delta
                self.ref_seiz_start_time_array[seiz_start_time_index] = updated_value

        for seiz_stop_time_index in range(len(self.ref_seiz_stop_time_array)):
            if self.ref_seiz_stop_time_array[seiz_stop_time_index] + self.delta >= self.ref_stop_time:
                updated_value = self.ref_stop_time
                self.ref_seiz_stop_time_array[seiz_stop_time_index] = updated_value
            else:
                updated_value = self.ref_seiz_stop_time_array[seiz_stop_time_index] + self.delta
                self.ref_seiz_stop_time_array[seiz_stop_time_index] = updated_value
                
        
    def calc_bckg_epochs(self, seiz_start_time_array, seiz_stop_time_array, file_start_time, file_stop_time):

        total_seiz_epochs = 0 
        for seiz_index in range(len(seiz_start_time_array)):

            total_seiz_epochs = total_seiz_epochs + (seiz_stop_time_array[seiz_index] - seiz_start_time_array[seiz_index])

        total_bckg_epochs = file_stop_time - total_seiz_epochs 

        return total_bckg_epochs

    def calc_seiz_FA_epochs(self, hyp_seiz_start_time_array, hyp_seiz_stop_time_array):
        print " inside seiz fa epochs "
        print hyp_seiz_start_time_array
        print hyp_seiz_stop_time_array

        total_seiz_FA_epochs = 0
        for seiz_fa_index in range(len(hyp_seiz_start_time_array)):
            total_seiz_FA_epochs = total_seiz_FA_epochs + (hyp_seiz_stop_time_array[seiz_fa_index] - hyp_seiz_start_time_array[seiz_fa_index])

        return total_seiz_FA_epochs

    
    def check_end_of_array(self):
        if len(self.ref_seiz_start_time_array) == 0 or len(self.hyp_seiz_start_time_array) == 0 or len(self.ref_seiz_start_time_array) == self.ref_index or len(self.hyp_seiz_start_time_array) == self.hyp_index:
            return True
        else:
            return False
