## This class calculates cohen's kappa (pairwise) coefficient for interrater agreement
#


class cohens_kappa(object):

    def __init__(self, true_positives, true_negatives, false_positives, false_negatives ):

        self.true_positives = float(true_positives)
        self.true_negatives = float(true_negatives)
        self.false_positives = float(false_positives)
        self.false_negatives = float(false_negatives)
        self.total_events = self.true_positives + self.true_negatives + self.false_positives + self.false_negatives

        
    def calc_observed_accuracy(self):

        self.observed_accuracy = (self.true_positives + self.true_negatives)/self.total_events

        
    def calc_expected_accuracy(self):

        self.true_marginal_freq_of_first_class = self.true_positives + self.false_negatives
        self.detected_marginal_freq_of_first_class = self.true_positives + self.false_positives
        self.true_marginal_freq_of_second_class = self.true_negatives + self.false_positives
        self.detected_marginal_freq_of_second_class = self.true_negatives + self.false_negatives

        self.first_class_results = (self.true_marginal_freq_of_first_class/self.total_events) * (self.detected_marginal_freq_of_first_class/ self.total_events)

        self.second_class_results = (self.true_marginal_freq_of_second_class/self.total_events) * (self.detected_marginal_freq_of_second_class/ self.total_events)

        self.expected_accuracy = (self.first_class_results + self.second_class_results) #/ self.total_events

        
    def calc_kappa_coefficient(self):
        kappa = (self.observed_accuracy - self.expected_accuracy) / (1 - self.expected_accuracy)

        return kappa
