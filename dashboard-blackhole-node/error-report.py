#!/usr/bin/python

import sys
import json
import urllib2
import pdb
import time
import optparse

class InvalidOptionError(Exception): pass

# This list of sites was taken from SiteDB on January 10, 2014 
# There is an api for SiteDB that we could use to query directly, but then the person running this script would have
# to have their cert setup on that machine.
CMS_Sites = ['T0_CH_CERN', 'T1_CH_CERN', 'T1_DE_KIT', 'T1_ES_PIC', 'T1_FR_CCIN2P3', 'T1_IT_CNAF', 'T1_RU_JINR',
             'T1_RU_JINR_Disk', 'T1_TW_ASGC', 'T1_UK_RAL', 'T1_UK_RAL_Disk', 'T1_US_FNAL', 'T1_US_FNAL_Disk',
             'T2_AT_Vienna', 'T2_BE_IIHE', 'T2_BE_UCL', 'T2_BR_SPRACE', 'T2_BR_UERJ', 'T2_CH_CERN', 'T2_CH_CERN_AI',
             'T2_CH_CERN_HLT', 'T2_CH_CSCS', 'T2_CN_Beijing', 'T2_DE_DESY', 'T2_DE_RWTH', 'T2_EE_Estonia',
             'T2_ES_CIEMAT', 'T2_ES_IFCA', 'T2_FI_HIP', 'T2_FR_CCIN2P3', 'T2_FR_GRIF_IRFU', 'T2_FR_GRIF_LLR',
             'T2_FR_IPHC', 'T2_GR_Ioannina', 'T2_HU_Budapest', 'T2_IN_TIFR', 'T2_IT_Bari', 'T2_IT_Legnaro',
             'T2_IT_Pisa', 'T2_IT_Rome', 'T2_KR_KNU', 'T2_MY_UPM_BIRUNI', 'T2_PK_NCP', 'T2_PL_Warsaw',
             'T2_PT_NCG_Lisbon', 'T2_RU_IHEP', 'T2_RU_INR', 'T2_RU_ITEP', 'T2_RU_JINR', 'T2_RU_PNPI', 'T2_RU_RRC_KI',
             'T2_RU_SINP', 'T2_TH_CUNSTDA', 'T2_TR_METU', 'T2_TW_Taiwan', 'T2_UA_KIPT', 'T2_UK_London_Brunel',
             'T2_UK_London_IC', 'T2_UK_SGrid_Bristol', 'T2_UK_SGrid_RALPP', 'T2_US_Caltech', 'T2_US_Florida',
             'T2_US_MIT', 'T2_US_Nebraska', 'T2_US_Purdue', 'T2_US_UCSD', 'T2_US_Vanderbilt', 'T2_US_Wisconsin',
             'T3_BY_NCPHEP', 'T3_CH_PSI', 'T3_CN_PKU', 'T3_CO_Uniandes', 'T3_ES_Oviedo', 'T3_EU_Parrot', 'T3_FR_IPNL',
             'T3_GR_Demokritos', 'T3_GR_IASA', 'T3_HR_IRB', 'T3_IN_PUHEP', 'T3_IR_IPM', 'T3_IT_Bologna',
             'T3_IT_Firenze', 'T3_IT_MIB', 'T3_IT_Napoli', 'T3_IT_Perugia', 'T3_IT_Trieste', 'T3_KR_KNU', 'T3_KR_UOS',
             'T3_MX_Cinvestav', 'T3_NZ_UOA', 'T3_RU_FIAN', 'T3_TW_NCU', 'T3_TW_NTU_HEP', 'T3_UK_London_QMUL',
             'T3_UK_London_RHUL', 'T3_UK_London_UCL', 'T3_UK_SGrid_Oxford', 'T3_UK_ScotGrid_ECDF', 'T3_UK_ScotGrid_GLA',
             'T3_US_Baylor', 'T3_US_Brown', 'T3_US_Colorado', 'T3_US_Cornell', 'T3_US_FIT', 'T3_US_FIU',
             'T3_US_FNALLPC', 'T3_US_FSU', 'T3_US_JHU', 'T3_US_Kansas', 'T3_US_MIT', 'T3_US_Minnesota', 'T3_US_NU',
             'T3_US_NotreDame', 'T3_US_OSU', 'T3_US_Omaha', 'T3_US_Princeton', 'T3_US_Princeton_ICSE',
             'T3_US_PuertoRico', 'T3_US_Rice', 'T3_US_Rutgers', 'T3_US_TAMU', 'T3_US_TTU', 'T3_US_UCD', 'T3_US_UCR',
             'T3_US_UIowa', 'T3_US_UMD', 'T3_US_UMiss', 'T3_US_UTENN', 'T3_US_UVA', 'T3_US_Vanderbilt_EC2']

class Options(optparse.OptionParser):
    def __init__(self):
        optparse.OptionParser.__init__(self)

        self.usage = """ %prog [options]

This script queries the CMS dashboard for failed jobs and correlates the job 
failures to node names.  Using some basic statistics, we can detect possible
"black hole" nodes.

"""
        opt_help_str = "hours offset: time zone offset. Defaults to 9 [optional]"
        self.add_option("-o", "--hours-offset", dest="hoursOffset", default=9, help=opt_help_str)
	
        self.add_option("-a", "--activity", dest="activity", default="", help="specify activity, default = all")

        self.options = None
        self.args = None

    def validate_options(self):
        pass

    def validate_args(self):
        if len(self.args) <= 0:
            msg = "Must provide a site name"
            raise InvalidOptionError, msg
        if self.args[0] not in CMS_Sites:
            msg = "Not a valid site name.  No data will be returned from the dashboard."
            raise InvalidOptionError, msg

    def parse(self):
        """
        Parses the command line and validates the options and arguments passed in
        """
        (options, args) = self.parse_args()
        self.options = options
        self.args = args

        self.validate_options()
        self.validate_args()

def failDistLast(site_name, activity, offset):

    #FIXME: The delta T algorithm doesn't work if the difference between the current hour and the offset is smaller 
    #       than 0. (midnight)
    finalTime = time.strftime("%Y-%m-%d+%H") + "%3A" + time.strftime("%M")
    initTime = time.strftime("%Y-%m-%d+") + str(int(time.strftime("%H")) - int(offset)) + "%3A" + time.strftime("%M")

    dashbUrl = "http://dashb-cms-job.cern.ch/dashboard/request.py/jobstatus2?" \
               "user=&site=%s&"\
               "submissiontool=&application=&activity=%s&status=app-failed&check=terminated&"\
               "tier=&sortby=activity&ce=&rb=&grid=&jobtype=&submissionui=&dataset=&submissiontype=&"\
               "task=&subtoolver=&genactivity=&outputse=&appexitcode=&accesstype=&"\
               "date1=%s&date2=%s&"\
               "count=9999&offset=0&exitcode=all&fail=all&cat=&len=5000&"\
               "prettyprint" % (site_name, activity, initTime, finalTime)
    print dashbUrl

    response = urllib2.urlopen(dashbUrl)

    # check 200 or bail
    dashbjson = json.loads(response.read())

    failureDistribution = {}
    for job in dashbjson['jobs']:
        if failureDistribution.has_key(job['WNHostName']):
            failureDistribution[job['WNHostName']] += 1
        else :
            failureDistribution[job['WNHostName']] = 1

    return failureDistribution

def findAvgFail(failDist):
    total = 0
    for node in failDist.keys():
        total += failDist[node]
    avg = total/len(failDist.keys())
    return avg

def findTotalFail(failDist):
    total = 0
    for node in failDist.keys():
        total += failDist[node]
    return total


def findBadNodes(failDist) :
    badNodes = []
    totalFail = findTotalFail(failDist)
    print "Total failures: %d" % totalFail
    print "================================="
    th = 0.1 ###### FAILURE THRESHOLD FOR BAD NODES
    for node in failDist.keys():
        failShare = float(failDist[node])/float(totalFail)
        if failShare > th:
            print "node %s is bad with %f failures" % (node, failShare)

def main():
    try:
        prog_opts = Options()
        prog_opts.parse()
        site_name = prog_opts.args[0]
        offset = prog_opts.options.hoursOffset
	activity = prog_opts.options.activity

        failDist = failDistLast(site_name, activity, offset)

        for node in failDist.keys():
            print "%s had %d failures" % (node, failDist[node])

        print "================================="
        print "average failure rate is %d" % findAvgFail(failDist)

        findBadNodes(failDist)
    except InvalidOptionError, ie:
        print str(ie)
        return 1

    # normal exit
    return 0

if __name__ == "__main__":
    sys.exit(main())

