import httplib
import subprocess
import json


def GetProtected():
   url = "cmst2.web.cern.ch"
   conn = httplib.HTTPSConnection(url)
  
   try:
      r1=conn.request("GET",'/cmst2/unified/listProtectedLFN.txt')
      r2=conn.getresponse()
      result=json.loads(r2.read())
   except:
      print "Cannot read Protected LFNs. Have to stop..."
      exit(1)

   # Testing:
   #result=json.loads(open('listProtectedLFN.txt').read())

   protected=result['protected']

   return protected

def GetOldUnmergedFiles():
   #
   # This needs to be customized.
   #  - at least the path is different
   findCMD='find /pnfs/desy.de/cms/tier2/unmerged -type f -ctime +14 -print'
   out = subprocess.Popen(findCMD,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   (stdout, stderr) = out.communicate()
   return stdout.decode().split()
   # Testing
   #f=open('old_unmerged.txt')
   #return f.readlines() 
   

def lfn2pfn(lfn):
   #
   # That implements only one lfn-2-pfn rule.
   # It needs to be customized! One can also employ the local TFC (storage.xml) or use Phedex API 
   pfn=lfn.replace("/store/unmerged/","/pnfs/desy.de/cms/tier2/unmerged/")
   return pfn

def DoDelete(pfn):
   #
   # Implement the actual deletion command here. This can vary by storage technology.
   print "Would delete %s"%pfn

def FilterProtected(OldUnmergedFiles, Protected):
   print "Got %i deletion candidates" %len(OldUnmergedFiles)
   print "Have %i protcted dirs" %len(Protected)
   n_protect=0
   n_delete=0
   for file in OldUnmergedFiles:
      # print "Checking file %s" %file
      protect=False
      for lfn in Protected:
         pfn=lfn2pfn(lfn)
         #pfn='/'.join(lfn.split('/')[2:])
         if pfn in file:
            print "%s is protected by path %s" %(file,pfn)
            protect=True
            break
      if not protect:
         DoDelete(file)


FilterProtected(GetOldUnmergedFiles(),GetProtected())
