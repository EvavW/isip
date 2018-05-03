import numpy as np
np.set_printoptions(threshold=np.inf)
def file_operation(filename):

    # create dictionary for 21 channels, which would contain list of seizure start and stop times
    #
    channels = np.zeros((22,250))


    i = 0
    column_index = -1
    recfile = open(filename,'r').read()
    recfile_content = recfile.split('\n')




    while i < 22:
        column_index = -1
        for lines in recfile_content:
            if lines =='':
                break
            line_content = lines.split(',')

            if (int(line_content[0]) == i) and (int(line_content[3]) >= 7) and (int(line_content[3]) < 18): # editedV changed " == 7): " to " >= 7):"

                column_index += 1
                channels[i,column_index] = line_content[1]
                column_index += 1
                channels[i,column_index] = line_content[2]

        i += 1
    return channels
