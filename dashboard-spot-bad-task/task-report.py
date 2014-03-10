#!/usr/bin/python

import json
import urllib2
import pdb
import time

# Gets from dashboard the analysis users jobs statuses :
#http://dashb-cms-job.cern.ch/dashboard/request.py/jobsummary-plot-or-table2?user=&site=T2_US_Caltech&submissiontool=&application=&activity=analysis&status=&check=submitted&tier=&sortby=user&ce=&rb=&grid=&jobtype=&submissionui=&dataset=&submissiontype=&task=&subtoolver=&genactivity=&outputse=&appexitcode=&accesstype=&date1=2013-08-15+00%3A14&date2=2013-08-16+21%3A14&prettyprint



daysOffset = 2 

#def getUserslast(hours):
#	#FIXME: The delta T algorithm doesnt work if the difference between the current hour and the offset is smaller than 0. (midnight)
#	finalTime = time.strftime("%Y-%m-%d+%H")+"%3A"+time.strftime("%M")
#	initTime = time.strftime("%Y-%m-%d+")+str(int(time.strftime("%H"))-hoursOffset)+"%3A"+time.strftime("%M")
#	dashbUrl = "http://dashb-cms-job.cern.ch/dashboard/request.py/jobsummary-plot-or-table2?user=&site=T2_US_Caltech&submissiontool=&application=&activity=analysis&status=&check=submitted&tier=&sortby=user&ce=&rb=&grid=&jobtype=&submissionui=&dataset=&submissiontype=&task=&subtoolver=&genactivity=&outputse=&appexitcode=&accesstype=&date1=2013-08-15+00%3A14&date2=2013-08-16+21%3A14&prettyprint"

#	response = urllib2.urlopen(dashbUrl)
	
	# check 200 or bail
	
#	dashbjson = json.loads(response.read())
#	badUsers = {}
	#print dashbjson['jobs']
#	for job in dashbjson['jobs']:




def badUsersLast(days):
	#FIXME: The delta T algorithm doesnt work if the difference between the current hour and the offset is smaller than 0. (midnight)
	finalTime = time.strftime("%Y-%m-%d+%H")+"%3A"+time.strftime("%M")
	initTime = time.strftime("%Y-%m-")+str(int(time.strftime("%d"))-daysOffset)+time.strftime("+%H")+"%3A"+time.strftime("%M")
#+str(int(time.strftime("%H"))-hoursOffset)
#+"%3A"+time.strftime("%")
	
	#print "%s %s" % (initTime, finalTime)
	
	dashbUrl = "http://dashb-cms-job.cern.ch/dashboard/request.py/jobsummary-plot-or-table2?user=&site=T2_US_Caltech&submissiontool=&application=&activity=analysis&status=&check=submitted&tier=&sortby=user&ce=&rb=&grid=&jobtype=&submissionui=&dataset=&submissiontype=&task=&subtoolver=&genactivity=&outputse=&appexitcode=&accesstype=&date1=%s&date2=%s&prettyprint" % (initTime, finalTime)
	
	response = urllib2.urlopen(dashbUrl)
	
	# check 200 or bail
	
	dashbjson = json.loads(response.read())
#	pdb.set_trace()
	
	
	badUsers = {}
	#print dashbjson['summaries']
	for user in dashbjson['summaries']:
		print user['name']
		print "failed : %s , term : %s " % (user['application-failed'], user['terminated'])
		if ( int(user['application-failed']) > 0 and int(user['terminated']) > 0 ):
			if (int(user['application-failed'])/int(user['terminated']) > 0.5) :
				print "User %s is screwing up" % user['name']
	# THIS DOES NOT SEEM TO BE HELPFUL. WE'RE BETTER FINDING TASKS RATHER THAN USERS

def badTasksLastDays(daysOffset):

	#FIXME: The delta T algorithm doesnt work if the difference between the current hour and the offset is smaller than 0. (midnight)
	finalTime = time.strftime("%Y-%m-%d+%H")+"%3A"+time.strftime("%M")
	initTime = time.strftime("%Y-%m-")+str(int(time.strftime("%d"))-daysOffset)+time.strftime("+%H")+"%3A"+time.strftime("%M")

	dashbUrl = "http://dashb-cms-job.cern.ch/dashboard/request.py/jobsummary-plot-or-table2?user=&site=T2_US_Caltech&submissiontool=&application=&activity=analysis&status=&check=terminated&tier=&sortby=task&ce=&rb=&grid=&jobtype=&submissionui=&dataset=&submissiontype=&task=&subtoolver=&genactivity=&outputse=&appexitcode=&accesstype=&date1=%s&date2=%s&prettyprint" % (initTime, finalTime)

	response = urllib2.urlopen(dashbUrl)
	#FIXME: check 200 or bail
	
	dashbjson = json.loads(response.read())

	badTasks = {}
	#print dashbjson['summaries']
	for task in dashbjson['summaries']:
		#print task['name']
		#print "failed : %s , term : %s " % (task['application-failed'], task['terminated'])
		if ( int(task['application-failed']) > 0 and int(task['terminated']) > 0  and int(task['terminated']) > 60):
			if (int(task['application-failed'])/int(task['terminated']) > 0.2) :
				badTasks[task['name']] = task
				print "Task %s is bad" % task['name']
				print "failed : %s , term : %s " % (task['application-failed'], task['terminated'])
	return badTasks


def getJobExitCodeDistribution(daysOffset, task):

	#FIXME: The delta T algorithm doesnt work if the difference between the current hour and the offset is smaller than 0. (midnight)
	finalTime = time.strftime("%Y-%m-%d+%H")+"%3A"+time.strftime("%M")
	initTime = time.strftime("%Y-%m-")+str(int(time.strftime("%d"))-daysOffset)+time.strftime("+%H")+"%3A"+time.strftime("%M")

	dashbUrl = "http://dashb-cms-job.cern.ch/dashboard/request.py/jobstatus2?user=&site=T2_US_Caltech&submissiontool=&application=&activity=analysis&status=app-failed&check=terminated&tier=&sortby=task&ce=&rb=&grid=&jobtype=&submissionui=&dataset=&submissiontype=&task=%s&subtoolver=&genactivity=&outputse=&appexitcode=&accesstype=&date1=%s&date2=%s&count=69&offset=0&exitcode=application&fail=application&cat=&len=5000&prettyprint" % (task, initTime, finalTime)

	response = urllib2.urlopen(dashbUrl)
	#FIXME: check 200 or bail
	
	dashbjson = json.loads(response.read())
	
	failureDistribution = {}
	for job in dashbjson['jobs']:
		if failureDistribution.has_key(job['JobExecExitCode']):
			failureDistribution[job['JobExecExitCode']] += 1
		else :
			failureDistribution[job['JobExecExitCode']] = 1


	return failureDistribution

badTasks = badTasksLastDays(daysOffset)

#pdb.set_trace()
for task in badTasks:
	jobExitCodeDist = getJobExitCodeDistribution(daysOffset, task)

	totalJobs = 0
	for exitCode in jobExitCodeDist:
		totalJobs += jobExitCodeDist[exitCode]
	#pdb.set_trace()
	WCTimeRate = float(jobExitCodeDist[50664])/totalJobs*100
	if WCTimeRate > 50:
		print "Task %s has %f%% failed jobs due to WC Time and should be killed" % (task, WCTimeRate)
	
#	properties = badTasks[task]
#	print properties.name

#for task in badTasks.keys():
#	print task['name']


