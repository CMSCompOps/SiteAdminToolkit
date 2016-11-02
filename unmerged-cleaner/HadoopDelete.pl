#!/usr/bin/perl -w

##!
# This script, located in ``SiteAdminTools/unmerged-cleaner/HadoopDelete.pl``,
# is used to delete files and directories inside of a list of directories.
# In particular, it is used on the Hadoop site T2_US_MIT.
# Before running it at your site, check that ``$file`` results in
# the proper transformation between LFN and PFN.
#
# To run the script, pass the location of the **DELETION_FILE** parameter
# that is set in :ref:`unmerged-list-ref` as the arugment.
# For example, if the directories to delete are listed in
# ``/tmp/dirs_to_delete.txt``, run this script as::
#
#     ./HadoopDelete.pl /tmp/dirs_to_delete.txt
#
# :author: Max Goncharov <maxi@mit.edu>
##!

use strict;

my @remfiles = ();
my $tfile = $ARGV[0];
open(IN, "$tfile") || die "$tfile does not exist\n";
while(<IN>){
    chomp;
    print $_,"\n";
    @remfiles = (@remfiles, $_);
}
close(IN);

foreach my $file (@remfiles){
    unless(-d $file){
        print "$file does not exist, skipping\n";
        next;
    }
    #unless ($file =~/user/){
    #  print "$file not a user dir, skipping\n";
    #  next;
    #}
    $file =~ s/\/mnt\/hadoop//;
    my $file_1 = '/cksums'."$file";
    my $com = "hdfs dfs -rm -r $file";
    print "will do $com \n";
    system("$com");sleep(0.5);
    $com = "hdfs dfs -rm -r $file_1";
    print "will do $com \n";
    system("$com");sleep(0.5);
}
