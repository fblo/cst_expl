Script help:
```
$ iv-vocal-project-values -h
usage: iv-vocal-project-values [-h] [--country COUNTRY_CFG]
                               [--whitelabel WHITELABEL_CFG]
                               [--project PROJECT_CFG]
                               [--pai P_ASSERTED_IDENTITY_CFG]
                               [--backup_directory BACKUP_DIRECTORY] [-d]
                               host project

Set project common values.

positional arguments:
  host                  Target vocal host
  project               Target project

optional arguments:
  -h, --help            show this help message and exit
  --country COUNTRY_CFG
                        Country. Ex: FR, PT, UK, ...
  --whitelabel WHITELABEL_CFG
                        Whitelabel. Ex: COLT, CONNECTICS, ...
  --project PROJECT_CFG
                        Project. Ex: INT101, INTERACTIVSUPPORTMC, ...
  --pai P_ASSERTED_IDENTITY_CFG
                        P-Asserted-Identity. Ex:
                        <sip:0544332211@cnxtestsuite.com>
  --backup_directory BACKUP_DIRECTORY
                        Backup directory used for local copy of current and
                        updated Ccxml configurations. Default: /tmp
  -d, --debug           Debug mode. File won't be pushed back to vocal server.
```

Usage examples:
- On a project already configured. Without any option (which will read current values but not update any of those). Debug mode enabled to prevent pushing back anything.
```
$ iv-vocal-project-values 10.199.30.200 IVMID -d
Retrieving file [/db/projects/IVMID/Ccxml.xml] -> [/tmp/IVMID_old_Ccxml.xml]... done
Cleaning file...done
Updating local file...
Handling users_values:
 - country_cfg     : FR
 - whitelabel_cfg  : COLT
 - project_cfg     : IVMID
 - p_asserted_identity_cfg : <sip:0123456789@10.199.30.200>
Handling entries_values:
 - country_cfg     : FR
 - whitelabel_cfg  : COLT
 - project_cfg     : IVMID
 - p_asserted_identity_cfg : <sip:0123456789@10.199.30.200>
Done
Debug mode. File has not been pushed back to server.
Old ccxml file: /tmp/IVMID_old_Ccxml.xml
New ccxml file: /tmp/IVMID_new_Ccxml.xml
```

- On a project not configured. Without any option. Debug mode enabledWithout any option (which will read current values but not update any of those). Debug mode enabled to prevent pushing back anything.
```
$ iv-vocal-project-values 10.199.30.170 INT101 -d
Retrieving file [/db/projects/INT101/Ccxml.xml] -> [/tmp/INT101_old_Ccxml.xml]... done
Cleaning file...done
Updating local file...
Handling users_values:
 - country_cfg     : None
 - whitelabel_cfg  : None
 - project_cfg     : None
 - p_asserted_identity_cfg : None
Handling entries_values:
 - country_cfg     : None
 - whitelabel_cfg  : None
 - project_cfg     : None
 - p_asserted_identity_cfg : None
Done
Debug mode. File has not been pushed back to server.
Old ccxml file: /tmp/INT101_old_Ccxml.xml
New ccxml file: /tmp/INT101_new_Ccxml.xml
```

- On a project already configured. With all options. Debug mode enabled to prevent pushing back anything.
```
$ iv-vocal-project-values 10.199.30.200 IVMID --country "DE" --whitelabel "HUBONE" --project "TOTO" --pai "<sip:0123456789@test.com>" -d
Retrieving file [/db/projects/IVMID/Ccxml.xml] -> [/tmp/IVMID_old_Ccxml.xml]... done
Cleaning file...done
Updating local file...
Handling users_values:
 - country_cfg     : FR -> DE
 - whitelabel_cfg  : COLT -> HUBONE
 - project_cfg     : IVMID -> TOTO
 - p_asserted_identity_cfg : <sip:0123456789@10.199.30.200> -> <sip:0123456789@test.com>
Handling entries_values:
 - country_cfg     : FR -> DE
 - whitelabel_cfg  : COLT -> HUBONE
 - project_cfg     : IVMID -> TOTO
 - p_asserted_identity_cfg : <sip:0123456789@10.199.30.200> -> <sip:0123456789@test.com>
Done
Debug mode. File has not been pushed back to server.
Old ccxml file: /tmp/IVMID_old_Ccxml.xml
New ccxml file: /tmp/IVMID_new_Ccxml.xml
```

- On a project not configured. With all options. Debug mode enabled to prevent pushing back anything.
```
$ iv-vocal-project-values 10.199.30.170 INT101 --country "DE" --whitelabel "HUBONE" --project "TOTO" --pai "<sip:0123456789@test.com>" -d
Retrieving file [/db/projects/INT101/Ccxml.xml] -> [/tmp/INT101_old_Ccxml.xml]... done
Cleaning file...done
Updating local file...
Handling users_values:
 - country_cfg     : None -> DE
 - whitelabel_cfg  : None -> HUBONE
 - project_cfg     : None -> TOTO
 - p_asserted_identity_cfg : None -> <sip:0123456789@test.com>
Handling entries_values:
 - country_cfg     : None -> DE
 - whitelabel_cfg  : None -> HUBONE
 - project_cfg     : None -> TOTO
 - p_asserted_identity_cfg : None -> <sip:0123456789@test.com>
Done
Debug mode. File has not been pushed back to server.
Old ccxml file: /tmp/INT101_old_Ccxml.xml
New ccxml file: /tmp/INT101_new_Ccxml.xml
```

- On a project already configured. With all options. No debug mode.
```
$ iv-vocal-project-values 10.199.30.200 IVMID --country "DE" --whitelabel "HUBONE" --project "TOTO" --pai "<sip:0123456789@test.com>"
Retrieving file [/db/projects/IVMID/Ccxml.xml] -> [/tmp/IVMID_old_Ccxml.xml]... done
Cleaning file...done
Updating local file...
Handling users_values:
 - country_cfg     : FR -> DE
 - whitelabel_cfg  : COLT -> HUBONE
 - project_cfg     : IVMID -> TOTO
 - p_asserted_identity_cfg : <sip:0123456789@10.199.30.200> -> <sip:0123456789@test.com>
Handling entries_values:
 - country_cfg     : FR -> DE
 - whitelabel_cfg  : COLT -> HUBONE
 - project_cfg     : IVMID -> TOTO
 - p_asserted_identity_cfg : <sip:0123456789@10.199.30.200> -> <sip:0123456789@test.com>
Done
Pushing file... [/db/projects/IVMID/Ccxml.xml] -> [/tmp/IVMID_new_Ccxml.xml]... done
Old ccxml file: /tmp/IVMID_old_Ccxml.xml
New ccxml file: /tmp/IVMID_new_Ccxml.xml
```

- On a mistyped or non existing project.
```
$ iv-vocal-project-values 10.199.30.200 FAKE_PROJECT --country "DE" --whitelabel "HUBONE" --project "TOTO" --pai "<sip:0123456789@test.com>"
Retrieving file [/db/projects/FAKE_PROJECT/Ccxml.xml] -> [/tmp/FAKE_PROJECT_old_Ccxml.xml]... failed ! (return code: 6)
29/04/2019 09:19:46.898999 : 00119 : error : node not found
29/04/2019 09:19:46.899440 : 00119 : Errors

Exiting
```
