import numpy as np
import re, sys, os
import openpyxl
import pickle


class Annotator(object):
    

    overall_seiz_files = 0;
    overall_no_seiz_files = 0;
    overall_seiz_events = 0;
    sessions = []
    patients = []
    def __init__(self, name):
        self.name = name;
        self.Annotators_lines = []


    def add_annotators_lines(self,List_per_line):
        self.Annotators_lines.append(List_per_line)
        return self.Annotators_lines

    def calculate_seizure_files(self,Annotators_sublists):
        ## This class accepts all the sublists of individual annotator and calculates the total number
        ## of seizure events they found..
        #
        self.i = 0
        for sublists in Annotators_sublists:
            
            if sublists[0][1] == True or sublists[0][2] == True:
                self.i += 1;

        return self.i


    def calculate_total_files(self, Annotators_list, Annotator_seizure_files = 0):
        self.i = 0
        for sublists in Annotators_list:
            if sublists[0][3] == True:
                self.i += 1;
        return self.i+Annotator_seizure_files



    def calculate_session_w_patients(self, Annotators_list):

        session_list = []
        patient_list = []
        for sublists in Annotators_list:
            if sublists[0][-1] != None:
                filename_w_address = sublists[0][-1]
                ## we have files here (per annotator)
                ## seperate sessions and patients from these files
                #
                session_list = self.calc_sessions(filename_w_address, session_list)
                patient_list = self.calc_patients(filename_w_address, patient_list)
                
            self.sessions = len(session_list)
            self.patients = len(patient_list)
    

        return self.sessions, self.patients

    
    def calc_sessions(self, filename, session_list):
        
        file_parts = filename.split(r'/')
        session_name = file_parts[2] + r'/' + file_parts[3]
        if session_name not in session_list:
            session_list.append(session_name)

        ## here one can also collect name of sessions but we are only interested in
        ## number of sessions, so just send the length of sessions list
    
        return session_list

    def calc_patients(self, filename, patient_list):
        
        file_parts = filename.split(r'/')
        if file_parts[2] not in patient_list:
            patient_list.append(file_parts[2])

        ## here one can also collect name of sessions but we are only interested in
        ## number of sessions, so just send the length of sessions list
    
        return patient_list
    
            

    ########   THIS MESS IS UNNECESSARY    #########
    ########   MAY GET UPDATED IN FUTURE   ######### 
    def calculate_overall_seiz_files(self, seiz_flag):
        if self.seiz_flag == True:
            Annotator.overall_seiz_files += 1;
        elif self.seiz_flag == False:
            Annotator.overall_no_seiz_files += 1;
        
        print "Total seiz files from annotator %s: "%self.name, Annotator.overall_seiz_files
            
    def calculate_overall_seiz_events(self, num_events):
        Annotator.overall_seiz_events += num_events
        return Annotator.overall_seiz_events
       
    def append_lists(self, annotator, hundred_seiz, eighty_seiz, no_seiz, No_events, \
                           locality_seiz, type_seiz, seiz_name, Acc_2_report, \
                           relia_report, assesed_by):
        
        pass

        


#class Performance:
#    pass

class Details:
    def __init__(self,name, num_events, locality_seiz, type_seiz, name_seiz, Acc_2_report, Assesser_name, seiz_flag ):
        self.name = name;
        self.num_events = num_events;
        self.locality_seiz = locality_seiz;
        self.type_seiz = type_seiz;
        self.name_seiz = name_seiz;
        self.Acc_2_report = Acc_2_report;
        self.Assesser_name = Assesser_name;
        self.seiz_flag = seiz_flag

        #####   MESS ENDS HERE   ######
        ###############################
