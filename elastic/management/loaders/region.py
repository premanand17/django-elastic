'''
Created on 28 Jan 2016

@author: ellen
'''
import csv


class RegionManager(object):
    '''
    classdocs
    '''

    def add_study_data(self, **options):
        ''' add gwas stats from a study '''
        study = options['study_id']
        file = options['addStudyData']
        print(study)
        with open(file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                if row[0] == 'Marker':
                    continue
                ''' Marker
                    disease ID
                    Chromosome
                    Region Start
                    Region End
                    Position
                    Strand
                    Major Allele
                    Minor allele
                    Minor allele frequency
                    Discovery P value
                    Discovery Odds ratio
                    Discovery 95% confidence interval lower limit
                    Discovery 95% confidence interval upper limit
                    Replication P value
                    Replication Odds ratio
                    Replication 95% confidence interval lower limit
                    Replication 95% confidence interval upper limit
                    Combined P value
                    Combined Odds ratio
                    Combined 95% confidence interval lower limit
                    Combined 95% confidence interval upper limit
                    PP Colocalisation
                    Gene
                    PubMed ID
                    Other Signal
                    Notes
                    Curation status/ failed quality control
                '''
                print(row[0])
