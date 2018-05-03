import cohens_kappa_class as ckc

def main():
    
    tp = 11140
    tn = 158566
    fp = 772
    fn = 2326

    kp_obj = ckc.cohens_kappa(tp,tn,fp,fn)

    kp_obj.calc_observed_accuracy()
    kp_obj.calc_expected_accuracy()
    
    cohens_kappa = kp_obj.calc_kappa_coefficient()
    print "Cohen's kappa value is: ", cohens_kappa













if __name__=="__main__": main()
