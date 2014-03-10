#!/usr/bin/perl -w
# $Author: Carl Lundstedt
# ARG[0] (optional, defaults to 2 weeks)  should be the time window for starting the stale, e.g. "1 month ago", "2 days ago"
# ARG[1] (optional, defaults to Nebraska) Specify the SiteName e.g. T2_US_Nebraska, T2_US_Caltech

use strict;
use warnings;
use App::Rad;
use WWW::Mechanize;
use Data::Dumper;
use JSON -support_by_pp;
use Date::Manip;
use Date::Calc;
use namespace::autoclean;

App::Rad->run();


sub run {
    
    #This is to get options easier
    my $rad = shift;

    #set here your site if you like it:
    my $default_site = "T2_BR_UERJ";

    my $phedex_ref        = WWW::Mechanize->new();
    my %datasets          = ();
    my %subscribed_blocks = ();
    my $datasets_ref      = {};
    my $site_name         = $rad->options->{site} or $rad->options->{s};
    my @datasetName       = "";
    my $char              = "#";
    my $blocksize         = 0;
    my $setsize           = 0;

    $site_name = $default_site if ( not $site_name );

    sub _fetch_json_page {
        my ($json_url) = @_;
        my $browser = WWW::Mechanize->new();

        # download the json page:
        print "Getting json $json_url\n";
        $browser->get($json_url);
        my $content = $browser->content();
        my $json    = new JSON;

        my $json_text =
          $json->allow_nonref->utf8->relaxed->escape_slash->loose
          ->allow_singlequote->allow_barekey->decode($content);
        my @temp = ();
        foreach my $dataset ( @{ $json_text->{inputcollections} } ) {
            push( @temp, $dataset->{inputcollection} );
        }
        return ( \@temp );

        # catch crashes:
        if ($@) {
            print "[[JSON ERROR]] JSON parser crashed! $@\n";
        }
    }

    my $date_range =  $rad->options->{'date'} or $rad->options->{'d'};

    $date_range = "2 weeks ago" if ( not $date_range );

    my $today     = &ParseDate("today");
    my $startdate = &ParseDate($date_range);
    $today     = UnixDate( $today,     "%d-%m-%Y" );
    $startdate = UnixDate( $startdate, "%d-%m-%Y" );
    print "date = $today ,  Starting Date = $startdate  \n";

    my $collections_ref = _fetch_json_page(
"http://dashb-datasets.cern.ch/dashboard/request.py/inputCollectionsTable_JSON?collec_name=&sites=$site_name&date1=$startdate&date2=$today"
    );
    my @collections = @$collections_ref;

    $phedex_ref->get(
        (
"http://cmsweb.cern.ch/phedex/datasvc/perl/prod/blockreplicas?node=$site_name;dataset=*"
        )
    );
    my $phedex = $phedex_ref->content();
    $phedex =~ s{\A\$VAR\d+\s*=\s*}{};
    my $phedex_values = eval $phedex;
    for my $block ( @{ $phedex_values->{PHEDEX}->{BLOCK} } ) {

        @datasetName = split( /#/, $block->{NAME} );

        $blocksize = $block->{BYTES};
        for my $replica ( @{ $block->{REPLICA} } ) {
            if ( $replica->{GROUP} ) {
                $datasets{ $datasetName[0] }{GROUP} = $replica->{GROUP};
            }
            else {
                $datasets{ $datasetName[0] }{GROUP} = "undef";
            }
            if ( !exists $datasets{ $datasetName[0] }{setsize} ) {
                $datasets{ $datasetName[0] }{setsize} = 0;
                $setsize = 0;
            }
            $setsize = $blocksize + $datasets{ $datasetName[0] }{setsize};
            $datasets{ $datasetName[0] }{setsize} = $setsize;

        }
    }

    my %original = ();
    my @diff     = ();
    my @dataset  = ();

    for my $key ( keys %datasets ) {
        push( @dataset, $key );
    }
    map { $original{$_} = 1 } @collections;
    @diff = grep { !defined $original{$_} } @dataset;
    my $wasted = 0;

    print "Datasets idle since $startdate  \n";
    my %ownerSpace = ();

    foreach my $stale (@diff) {

        my $Size  = $datasets{$stale}{setsize} / 1000000000;
        my $owner = $datasets{$stale}{GROUP};
        $ownerSpace{$owner} += $Size / 1000;
        print "$stale ,   $Size GB ,  Owned by $owner \n";
        $wasted += $Size;

    }

    #$wasted = $wasted/1000000000000;
    print "Space taken by stale datasets = ", $wasted / 1000, "  TB \n";
    print "Broken down by group: \n";
    for my $newkey ( keys %ownerSpace ) {
        my $value = $ownerSpace{$newkey};
        print " \t $newkey => $value\n";
    }

}
