import sys, os, re
import cohens_kappa_class as ck

## NIST rescoring already generates the Confusion matrix, so only thing which is left to do is
## to calculate Observed and Expected accuracies.
#

def main():

    kappa_value(60, 5000, 125, 5)


















    
def kappa_value(TP, TN, FP, FN):
    calc_stat = ck.cohens_kappa(TP, TN, FP, FN)
    calc_stat.calc_observed_accuracy()
    calc_stat.calc_expected_accuracy()
    kappa_value = calc_stat.calc_kappa_coefficient()

    print kappa_value




if __name__ == "__main__": main()
