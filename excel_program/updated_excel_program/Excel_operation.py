import sys,os,re, openpyxl
import Annotator_class as AClass
from tabulate import tabulate

def xlop(filename):
    ## load the excel workbook
    #
    wb = openpyxl.load_workbook(filename)

    # print the type of workbook
    print (type(wb))

    ## A Single spreadsheet can have multiple sheets
    ## Collect all the sheet names
    #
    ws = wb.get_sheet_names()

    # open the very first workbook sheet ( which usually always opens as defaust)
    # We just have to work with the first sheet we open,
    # put that sheet to a variable name
    sheet = wb.get_sheet_by_name(ws[0])
    print sheet['A1'].value

    ## calculate total number of rows available in the spreadsheet
    ## here we do calculation in advance so that we can later save
    #  memory during allocation of lists where we will save all the
    #  information about each line
    rows_num = 0
    for rows in sheet.iter_rows():
        rows_num += 1
        #print rows_num

    total_spreadsheet_lines = rows_num
    

    
    ## Loop through rows and columns of the sheet and try to retrieve values
    row_num = 2           ## skipping header lines which are first two lines of spreadsheet
    sub_list = []
    main_list = [[]] * total_spreadsheet_lines

    Vinits_list = []
    Evas_list = []
    Noahs_list = []
    Tameems_list = []
    Steves_list = []
    Nijas_list = []
#    Adebolas_list = []
    
    for row in sheet.iter_rows():
        # row should be incremented last because so it is outside of the nested loop.
        row_num += 1        
        List_per_line = Excel_row_details(row, row_num)
        print List_per_line, "************"

        ## Algorithm from here should be --> take first element of list and associate it with
        ## an annotator name variable using if-else loop
        ## define a method in class called "scott's line" for scott name,
        ## This way we will add all the lists for individuals and
        ## Finally define a method inside a class to calculate individual's performance
        #

        if List_per_line[0].strip() == 'Eva':
            Eva = AClass.Annotator('Eva')
            Eva_lines = Eva.add_annotators_lines(List_per_line)
            Evas_list.append(Eva_lines)
            #Eva.calculate_seizure_files(Eva_lines)


        if List_per_line[0].strip() == 'Noah':
            Noah = AClass.Annotator('Noah')
            Noah_lines = Noah.add_annotators_lines(List_per_line)
            Noahs_list.append(Noah_lines)
            
        if List_per_line[0].strip() == 'Tameem':
            Tameem = AClass.Annotator('Tameem')
            Tameem_lines = Tameem.add_annotators_lines(List_per_line)
            Tameems_list.append(Tameem_lines)
            
        if List_per_line[0].strip() == 'Steve':
            Steve = AClass.Annotator('Steve')
            Steve_lines = Steve.add_annotators_lines(List_per_line)
            Steves_list.append(Steve_lines)
            
        if List_per_line[0].strip() == 'Nija':
            Nija = AClass.Annotator('Nija')
            Nija_lines = Nija.add_annotators_lines(List_per_line)
            Nijas_list.append(Nija_lines)
            
#        if List_per_line[0].strip() == 'Adebola':
#            Adebola= AClass.Annotator('Adebola')
#            Adebola_lines = Adebola.add_annotators_lines(List_per_line)
#            Adebolas_list.append(Adebola_lines)
            
        if List_per_line[0].strip() == 'Vinit':

            Vinit = AClass.Annotator('Vinit')
            Vinit_lines = Vinit.add_annotators_lines(List_per_line)
            Vinits_list.append(Vinit_lines)
        
            
    ## End of Information retrieval for individual annotator
    #
    

### Temporary operation to note down the number of annotators so far...
     


    
    ## change names if someone is not annotating
    #
    try:
        Vinit_seizure_files = Vinit.calculate_seizure_files(Vinits_list)
    except:
        pass
#    print Vinit_seizure_files, ' vinit seiz'
    Eva_seizure_files = Eva.calculate_seizure_files(Evas_list)
#    print Eva_seizure_files, ' eva seiz'
    Noah_seizure_files = Noah.calculate_seizure_files(Noahs_list)
#    print Noah_seizure_files, ' noah seiz'
    Tameem_seizure_files = Tameem.calculate_seizure_files(Tameems_list)
#    print Tameem_seizure_files, ' tameem seiz '
    try:
        Steve_seizure_files = Steve.calculate_seizure_files(Steves_list)
    except:
        pass
#    print Steve_seizure_files, ' steve seiz '
    try:
        Nija_seizure_files = Nija.calculate_seizure_files(Nijas_list)
    except:
        pass
#    print Nija_seizure_files, ' nija seiz '
#    Adebola_seizure_files = Adebola.calculate_seizure_files(Adebolas_list)
#    print Adebola_seizure_files, ' adebola seiz '
    
    ## 

    try:
        Vinit_total_files = Vinit.calculate_total_files(Vinits_list, Vinit_seizure_files)
    except:
        pass
#    print Vinit_total_files, " vinit total files "
    Eva_total_files = Eva.calculate_total_files(Evas_list, Eva_seizure_files)
#    print Eva_total_files, " Eva total files "
    Noah_total_files = Noah.calculate_total_files(Noahs_list, Noah_seizure_files)
#    print Noah_total_files, " Noah total files "
    Tameem_total_files = Tameem.calculate_total_files(Tameems_list, Tameem_seizure_files)
#    print Tameem_total_files, " Tameem total files "
    try:
        Steve_total_files = Steve.calculate_total_files(Steves_list, Steve_seizure_files)
    except:
        pass
#    print Steve_total_files, " Steve total files " 
    try:
        Nija_total_files = Nija.calculate_total_files(Nijas_list, Nija_seizure_files)
    except:
        pass
#    print Nija_total_files,  " Nija total files "
#    Adebola_total_files = Adebola.calculate_total_files(Adebolas_list, Adebola_seizure_files)
#    print Adebola_total_files, " Adebola total files "


    try:
        vinit_sessions, vinit_patients = Vinit.calculate_session_w_patients(Vinits_list)
        print "\n Vinit:  ", Vinit_total_files, " total files ", Vinit_seizure_files, " seiz files" , vinit_sessions, " sessions " , vinit_patients, " patients "
    except:
        pass
    
    try:
        nija_sessions, nija_patients = Nija.calculate_session_w_patients(Nijas_list)
        print " Nija:  ", Nija_total_files, " total files " , Nija_seizure_files, " seiz files", nija_sessions, " sessions ", nija_patients, " patients "
    except:
        pass

    try:
        steve_sessions, steve_patients = Steve.calculate_session_w_patients(Steves_list)
        print " Steve:  ", Steve_total_files, " total files " ,Steve_seizure_files, " seiz files", steve_sessions, " sessions " , steve_patients, " patients "
    except:
        pass
        
    print " \n"

    eva_sessions, eva_patients = Eva.calculate_session_w_patients(Evas_list)
    noah_sessions, noah_patients = Noah.calculate_session_w_patients(Noahs_list)
    tameem_sessions, tameem_patients = Tameem.calculate_session_w_patients(Tameems_list)

    print tabulate([["Eva:",Eva_total_files,Eva_seizure_files,eva_sessions,eva_patients],["Noah: ", Noah_total_files, Noah_seizure_files, noah_sessions, noah_patients], ["Tameem: ", Tameem_total_files, Tameem_seizure_files, tameem_sessions, tameem_patients]],headers=["Annotator","Total files", "Seizure files", "Sessions", "Patients"],tablefmt="orgtbl")
    


    
def Excel_row_details(row, row_num):
    ## This function loops through all the column for given row and
    ## extracts all the information from spreadsheet acc. to coumns
    #
    col = 0;

    ## loop through 
    for cell in row:
        col += 1
        if row_num > 2:


            if col == 1:
                Annotator_name = hundred_percent_sure = eighty_percent_sure = \
                         no_seiz = No_events = locality_seiz = type_seiz \
                                   = seiz_name = acc_2_report = \
                                                 reliability_of_seizure = \
                                                            str(-1);
                filename = cell.value
    


            ## column 2 is for Annotators name
            if col == 2 and cell.value != None:
                Annotator_name = cell.value
        
            ## 
            elif(col == 3) and cell.value != None:
                cell.value = cell.value.rstrip(' ')
                if cell.value.lower() == 'y':
                    hundred_percent_sure = True
                else:
                    hundred_percent_sure = False
        
            elif (col == 4) and cell.value != None:
                cell.value = cell.value.rstrip(' ')
                if cell.value.lower() == 'y':
                    eighty_percent_sure = True
                    #print ' eightuy percent sure at : ',col,row
                else:
                    eighty_percent_sure = False
                
                    
            elif (col == 5) and cell.value != None:
                cell.value = cell.value.rstrip(' ')
                if cell.value.lower() == 'y':
                    no_seiz = True
                else:
                    no_seiz = False
                    #print ' column and row number respectively are: ', col, row,
                #print no_seiz
                    
            elif (col == 6) and cell.value != None:
                No_Events = cell.value
                #print No_Events
        
            elif col == 7 and cell.value != None:
                locality_seiz = cell.value
                #print locality_seiz
        
            elif col == 8 and cell.value != None:
                type_seiz = cell.value
                #print type_seiz
        
            elif col == 9 and cell.value != None:
                seiz_name = cell.value
                #print seiz_name
                    
            elif col == 11 and cell.value != None:
                acc_2_report = cell.value
                #print acc_2_report
        
            elif col == 12 and cell.value != None:
                reliability_report = cell.value
                #print reliability_report
                    
                    

    if row_num > 2:
        Excel_variables = [ Annotator_name, hundred_percent_sure, eighty_percent_sure, no_seiz, No_events, locality_seiz, type_seiz, seiz_name, acc_2_report, reliability_of_seizure, filename ];

        return Excel_variables
            
    
if __name__=="__main__": xlop(sys.argv[1])
