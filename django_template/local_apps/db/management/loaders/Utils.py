from db.models import Cvterm, Cv, Dbxref, Db
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
import gzip
import re
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

'''
Create CV and cvterms
'''
def create_cvterms(cvName, cvDefn, termList):
        try:
            cv = Cv.objects.get(name=cvName)
            logger.warn("WARNING:: "+cvName+" CV EXISTS")
        except ObjectDoesNotExist as e:
            logger.warn("WARNING:: ADD "+cvName+" CV")
            cv = Cv(name=cvName, definition=cvDefn)
            cv.save()
        
        db = Db.objects.get(name='null')
        for term in termList:
            try:
                dbxref = Dbxref(db_id=db.db_id, accession=term.name)
                dbxref.save()
                cvterm = Cvterm(dbxref_id=dbxref.dbxref_id, cv_id=cv.cv_id, name=term.name, definition=term.definition, is_obsolete=0, is_relationshiptype=0)
                cvterm.save()
            except IntegrityError as ee:
                logger.warn("WARNING:: "+term.name+" FAILED TO LOAD")
        return cv
