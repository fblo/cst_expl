#!/usr/bin/env bash

PORTAL_DB_HOST="vs-ics-prd-web-fr-505.hostics.fr"
LOGS_STORAGE_DIRECTORY="/opt/debug"
NFS_MOUNT_DIRECTORY="$LOGS_STORAGE_DIRECTORY/NFS"
OLD_NFS_MOUNT_DIRECTORY="$LOGS_STORAGE_DIRECTORY/NFS_OLD"
BINDIR="$LOGS_STORAGE_DIRECTORY"
DISPATCH_BIN="ccenter_dispatch"
UPDATE_BIN="ccenter_update"
INTERFACE_DIR="$LOGS_STORAGE_DIRECTORY"
INTERFACE_FILE="debug_interface.xml"
PATH="$PATH:/opt/lampp/bin"

enable_debug() {
        _debug_logs=true
}

debug_activated() {
        [[ $_debug_logs == true ]] && return 0 || return 1
}

log() {
        local level="$1"
        shift
        echo "$(date -Is) - [$level] - $@"
}

debug() {
        if debug_activated; then
                log DEBUG "$@"
        fi
}

error() {
        log ERROR "$@" 1>&2;
}

die() {
        error "$@"
        exit 1
}

get_mysql_credentials() {
        if [[ $MYSQL_USERNAME == "" ]] || [[ $MYSQL_PASSWORD == "" ]]; then
                read -p "MySQL username: " _mysql_username
                read -s -p "MySQL password: " _mysql_password
                echo
        else
                _mysql_username="$MYSQL_USERNAME"
                _mysql_password="$MYSQL_PASSWORD"
        fi
}

mysql_query() {
        local host="$1"
        local query="$2"
        local database="$3"

        mysql \
                -h "$host" \
                -e "$query" \
                "$database"
}

get_address_for() {
        local vocal_node="$1"

        local query="select cccip from master_vocalnodes where vocalnode = '$vocal_node';"

        echo "$(mysql_query "$PORTAL_DB_HOST" "$query" "interactivdbmaster" | tail -1)"
}

get_vocal_node_for() {
        local project_name="$1"

        local query="select vocalnode from mig_vocalnodes_affectation where cccid = '$project_name';"

        echo "$(mysql_query "$PORTAL_DB_HOST" "$query" "interactivdbmaster" | tail -1)"
}

get_hostname_for() {
        local node="$1"
        local query="select cccip from master_vocalnodes where vocalnode = '$node';"

        # FBLO 20240313 local node_ip="$(mysql_query "$PORTAL_DB_HOST" "$query" "interactivdbmaster" | tail -1 | sed 's/svc/ps/')"
        local node_ip="$(mysql_query "$PORTAL_DB_HOST" "$query" "interactivdbmaster" | tail -1 )"

        echo "$(ssh connectics@$node_ip hostname | sed s/".hostics.fr"/""/g)"
}

get_project_configuration() {
        local project="$1"

}

get_next_available_port() {
        local range_start="$1"
        local range_end="$(($range_start + 200))"

        local netstat="$(netstat -nlt)"

        for i in $(seq "$range_start" "$range_end"); do
                if [[ $netstat =~ :$i ]]; then
                        continue
                fi

                echo $i
                return
        done
}

kill_running_dispatch() {
        local logsdir="$1"

        debug "Cleaning up existing dispatch process for the same logs."

        if pkill -f "ccenter_dispatch.*$logsdir"; then
                debug "Killed one or more dispatch processes active on the same date(s)."
        else
                if [[ $? == 1 ]]; then
                        debug "No process killed."
                else
                        die "Fatal error when trying to kill a dispatch process."
                fi
        fi
}

create_logsdir() {
        local logsdir="$1"

        pushd "$LOGS_STORAGE_DIRECTORY" >/dev/null

        if [ ! -d "$logsdir" ]; then
                debug "Creating $logsdir."
                mkdir "$logsdir"
        else
                debug "Directory $LOGS_STORAGE_DIRECTORY/$logsdir already exists."
        fi

}

retrieve_logs_from_nfs() {
        local logsdir="$1"
        local project="$2"
        local days="$3"
        local vocal_hostname="$4"

        if [[ $days == "" ]]; then
                debug "Nothing to be retrieved from NFS share."
                return
        fi

        debug "Days to be retrieved from NFS share: $days."

        local targetdir="$logsdir/Logger/$project/_/ccenter_ccxml/Ccxml/$vocal_hostname"
        local srcdir="$NFS_MOUNT_DIRECTORY/$vocal_hostname/opt/consistent/logs/$project/Logger/$project/_/ccenter_ccxml/Ccxml/$vocal_hostname*"
        mkdir -p "$targetdir"
        chown -R 777 $targetdir
        local cmd_line=""
        for pattern in $days; do
                cmd_line="$cmd_line -or -name '*$(echo "$pattern" | tr - _)*'"
        done

        local files="$(eval find "$srcdir" -name 0dummy $cmd_line)"
        debug "Downloading $(echo $files | wc -w) files... this may take a while."

        rsync -avz $files "$targetdir"
}

retrieve_logs_from_vocal_node() {
        local logsdir="$1"
        local project="$2"
        local days="$3"
        local vocal_hostname="$4"
        local vocal_host="$5"

        if [[ $days == "" ]]; then
                debug "Nothing to be retrieved from vocal node."
                return
        fi

        debug "Days to be retrieved from vocal node: $days."
        #COMMENTER la ligne suivante POUR BCA#
        local srcdir="/opt/consistent/logs/$project/Logger/$project/_/ccenter_ccxml/Ccxml/$vocal_hostname*"
        #DECOMMENTER CETTE LIGNE POUR BCA
        #local srcdir="/opt/consistent/logs/$project/Logger*/$project/_/ccenter_ccxml/Ccxml*/ps-ics-prd-cst-fr-530.hostics.fr"
        local targetdir="/opt/debug/$logsdir/Logger/$project/_/ccenter_ccxml/Ccxml/$vocal_hostname"
        mkdir -p "$targetdir"
        chmod -R 777 $targetdir

        local cmd_line="";
        for pattern in $days; do
                cmd_line="$cmd_line -or -name '*$(echo "$pattern" | tr - _)*.log'"
        done

        local files=$(eval ssh -o StrictHostKeyChecking=no "connectics@$vocal_host" find "$srcdir" -name 0dummy $cmd_line)

        debug "Downloading $(echo $files | wc -w) files... this may take a while."

        rsync_files=$(echo -n $files | tr '\n'  ' ')

#echo "eval rsync -az -e ssh connectics@\"${vocal_host}\":'$rsync_files' $targetdir"
for file in $files
do
        eval rsync -az -e ssh connectics@${vocal_host}:$file $targetdir
done
        [[ $? -ne 0 ]] && echo -e "\n\tRSYNC ERROR\n" && exit 10

}

calculate_days() {
        local begin_date="$1"
        local end_date="$2"

        local days=""
        local i=0

        if [[ $begin_date != $end_date ]]; then
                while [[ $(date --iso-8601 -d "$begin_date +$i days") != $end_date ]]; do
                        days="$days $(date --iso-8601 -d "$begin_date +$i days")"
                        let i+=1
                done

                days="$days $end_date"
        fi

        days="$(echo "$days" | sed -e 's/^[[:space:]]*//')"

        if [[ $days == "" ]]; then
                days="$begin_date"
        fi

        echo "$days"
}

calculate_hours() {
        local begin="$1"
        local end="$2"

        local tz="$(date +"%z")"
        local hours=""
        local i=0

        if [[ "$begin" != "$end" ]]; then
                while [[ "$(date -d "$begin$tz +$i hours" +"%Y-%m-%d %H:00:00")" != "$end" ]]; do
                        hours="$hours $(date -d "$begin$tz +$i hours" +"%Y_%m_%d__%H")"
                        let i+=1
                done

                echo "${hours:1}"
        else
                echo "$(date -d "$begin" +"%Y_%m_%d__%H")"
        fi
}

calculate_vocal_node_days() {
        local days="$1"
        local vocal_node_days=""

        if [[ $days =~ $(date --iso-8601) ]]; then
                vocal_node_days="$(date --iso-8601)"
        fi

        if [[ $days =~ $(date --iso-8601 -d yesterday) ]]; then
                vocal_node_days="$vocal_node_days $(date --iso-8601 -d yesterday)"
        fi

        echo "$vocal_node_days" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'
}

calculate_nfs_days() {
        local days="$1"
        local nfs_days="$(echo "$days" | sed -e "s/$(date --iso-8601)//g" -e "s/$(date --iso-8601 -d yesterday)//g")"

        echo "$nfs_days" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'
}

retrieve_logs() {
        local logsdir="$1"
        local project="$2"
        local begin_date="$3"
        local end_date="$4"
        local vocal_hostname="$5"
        local vocal_host="$6"

        if [ ${#begin_date} -le 10 ] ; then
                local all_days="$(calculate_days "$begin_date" "$end_date")"

                debug "Calculated days to be retrieved: $all_days."

                if [ $no_nfs ] ; then
                        retrieve_logs_from_vocal_node "$logsdir" "$project" "$all_days" "$vocal_hostname" "$vocal_host"
                else
                        local nfs_days="$(calculate_nfs_days "$all_days")"
                        local vocal_node_days="$(calculate_vocal_node_days "$all_days")"

                        retrieve_logs_from_nfs "$logsdir" "$project" "$nfs_days" "$vocal_hostname"
                        retrieve_logs_from_vocal_node "$logsdir" "$project" "$vocal_node_days" "$vocal_hostname" "$vocal_host"
                fi
        else
                if [ $no_nfs ] ; then
                        retrieve_logs_from_vocal_node "$logsdir" "$project" "$(calculate_hours "$begin_date" "$end_date")" "$vocal_hostname" "$vocal_host"
                else
                        retrieve_logs_from_nfs "$logsdir" "$project" "$(calculate_hours "$begin_date" "$end_date")" "$vocal_hostname"
                fi
        fi
}

decompress_logs() {
        local logsdir="$1"
        local files="$(find "$logsdir" -name '*.bz2')"
        local files_count="$(echo "$files" | wc -w)"

        if [[ $files_count > 0 ]]; then
                debug "Decompressing $files_count archived files."

                bunzip2 $(find "$logsdir" -name '*.bz2')
        fi
}

launch_dispatch() {
        local project="$1"
        local begin_date="$2"
        local end_date="$3"
        local port="$4"
        local logsdir="$5"

        debug "Launching dispatch."

        "$BINDIR/$DISPATCH_BIN" -slave "$port" -logs "$LOGS_STORAGE_DIRECTORY/$logsdir"/Logger* -interface "$INTERFACE_DIR/$INTERFACE_FILE" -stderr &

        local pid="$!"

        local days="$(calculate_days "${begin_date:0:10}" "${end_date:0:10}")"

        debug "Loading logs into dispatch. pid=$pid"

        for day in $days; do
                sleep 10

                debug "Loading day $day."

                day="$(echo "$day" | tr - _)"
                "$BINDIR/$UPDATE_BIN" -login admin -password admin -server 127.0.0.1 "$port" -event "com.consistent.ccenter.dispatch.load_day.$day" >/dev/null 2>&1
        done
}

show_banner() {
        local project="$1"
        local local_ip="$2"
        local local_port="$3"
        local begin_date="$4"
        local end_date="$5"

        echo "***********************************************************************************************************"
        echo "*  Consistent Explorer for $project between $begin_date and $end_date"
        echo "*"
        echo "*  c:\consistent_explorer.exe -login supervisor_stho -password toto -server $local_ip $local_port"
        echo "***********************************************************************************************************"
}

main() {
        local project="$1"
        local begin_date="$2"
        local end_date="$3"

        if [[ $(echo "$begin_date" | tr -d -) > $(echo "$end_date" | tr -d -) ]]; then
                begin_date="$3"
                end_date="$2"
        fi

        local logsdir="$project-${begin_date/ /T}"

        if [[ "$begin_date" != "$end_date" ]]; then
                logsdir="$logsdir-${end_date/ /T}"
        fi

        logsdir="${logsdir//:/-}"

        get_mysql_credentials

        local vocal_node="$(get_vocal_node_for "$project")"

        if [[ $vocal_node == "" ]]; then
                die "Could not find \`$project' in the central portal database."
        else
                debug "Found \`$project' in portal database."
        fi

        local vocal_host="$(get_address_for "$vocal_node")"

        if [[ $vocal_host == "" ]]; then
                die "Could not find vocal host address in the central portal database."
        else
                debug "Resolved vocal host address to \`$vocal_host'."
        fi

        local vocal_hostname="$(get_hostname_for "$vocal_node")"

        if [[ $vocal_host == "" ]]; then
                die "Could not retrieve server hostname."
        else
                [ $vocal_hostname == "ps-hub-prd-cst-fr-501" ] && vocal_hostname=vs-hub-prd-cst-fr-501
                [ $vocal_hostname == "ps-ics-prd-cst-de-501" ] && vocal_hostname=vs-ics-prd-cst-de-501
                [ $vocal_hostname == "ps-abs-prd-cst-fr-501" ] && vocal_hostname=vs-abs-prd-cst-fr-501
                [ $vocal_hostname == "ps-ics-prd-cst-be-501" ] && vocal_hostname=vs-ics-prd-cst-be-501
                [ $vocal_hostname == "ps-ics-prd-cst-at-501" ] && vocal_hostname=vs-ics-prd-cst-at-501
                [ $vocal_hostname == "ps-ics-prd-cst-nl-501" ] && vocal_hostname=vs-ics-prd-cst-nl-501
                [ $vocal_hostname == "ps-ics-prd-cst-ie-501" ] && vocal_hostname=vs-ics-prd-cst-ie-501
                [ $vocal_hostname == "ps-hub-prd-cst-fr-502" ] && vocal_hostname=vs-hub-prd-cst-fr-502
                debug "Retrieved server hostname: \`$vocal_hostname'."
        fi

        local local_ip=$(/sbin/ip route get 8.8.8.8 | awk 'NR==1 {print $NF}')

        debug "Dispatch will be started on $local_ip."

        kill_running_dispatch "$logsdir"
        create_logsdir "$logsdir"
        retrieve_logs "$logsdir" "$project" "$begin_date" "$end_date" "$vocal_hostname" "$vocal_host"
        decompress_logs "$logsdir"

        local local_port="$(get_next_available_port 35000)"

        if [[ $local_port == "" ]]; then
                rm -rf "$logsdir"
                die "Exhausted all ports when searching for available port between 35000-35200."
        fi

        launch_dispatch "$project" "$begin_date" "$end_date" "$local_port" "$logsdir" 
        show_banner "$project" "$local_ip" "$local_port" "$begin_date" "$end_date"

        debug "All done. Have a nice day, my friend."
}

show_help() {
        cat << EOF
Usage: ${0##*/} [-h] [-d] PROJECT [BEGINDATE] [ENDDATE]

Retrieve the logs from a remote IV2US vocal node and load them into a dispatch
process. If BEGINDATE (and ENDDATE) are provided, use those values instead of
\$today.

The script will look for two environment variables: MYSQL_USERNAME and
MYSQL_PASSWORD. If these are not present, the script will pause and ask the user
for input.

Positional arguments:
    PROJECT       the name of the project that should be created.
    BEGINDATE     an ISO-8601 string describing a specific day (e.g.:
                  2015-10-27).
    ENDDATE       same format as BEGINDATE.

Options:
    -h        display this help message and exit.
    -d        activate debug logs.
EOF
}

if [[ $0 =~ log-remounter.sh ]]; then
        while getopts "dhs:q" opt; do
                case "$opt" in
                        h)
                                show_help
                                exit 0
                                ;;

                        d)
                                enable_debug
                                ;;

                        s)
                                TARGET_HOST="$OPTARG"
                                ;;

                        q)
                                # QUALIF
                                PORTAL_DB_HOST="svc-int-prd-web-fr-301.hostics.fr"
                                no_nfs=true
                                ;;

                        '?')
                                show_help >&2
                                exit 1
                                ;;
                esac
        done

        project="${@:$OPTIND:1}"
        begin_date="${@:$OPTIND+1:1}"
        end_date="${@:$OPTIND+2:1}"

        if [[ $project == "" ]]; then
                show_help 2>&1
                echo 2>&1
                die "The PROJECT argument is required."
        else
                printf -v project "%q" "${@:$OPTIND:1}"
                debug "Setting project to \`$project'."
        fi

        if [[ $end_date == "" ]]; then
                end_date="$begin_date"
                debug "Setting ENDDATE to \`$end_date'."
        fi

        main "$project" "$begin_date" "$end_date"
fi
