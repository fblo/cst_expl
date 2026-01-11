#!/bin/bash

dispatch_port=`ccc_process_port TestAuto dispatch`

ccenter_report="/usr/bin/ccenter_report"
if [ ! -x "$ccenter_report" ]; then
	ccenter_report="/opt/consistent/bin/ccenter_report"
	if [ ! -x "$ccenter_report" ]; then
		echo "Couldn't find ccenter_report binary. Giving up."
		exit -1
	fi
fi

$ccenter_report -login admin -password admin -server localhost ${dispatch_port#*:} -list -path /dispatch -field sessions
$ccenter_report -login admin -password admin -server localhost ${dispatch_port#*:} -verbose -content -path /dispatch -object 15 -field sessions -fields "row.session_id; row.best_item; row.session_type"
