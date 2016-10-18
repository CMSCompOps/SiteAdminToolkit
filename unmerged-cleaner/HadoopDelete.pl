#!/usr/bin/perl -w

#
# $Id$
#

use strict;

my @remfiles = ();
my $tfile = "/root/files2delete.txt";
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
