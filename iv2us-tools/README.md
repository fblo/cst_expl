# IV2US Tools
This repository provides some scripts and tools that aim to help in the
administration, configuration and management of the IV2US infrastructure. These
tools do not concern a specific subset of the environment (for example, only
the vocal server, or only the API server).

# Dependencies
* MySQL-python
* iv-commons >= 0.1.5
* python-argparse >= 1.2.1
* python-phpserialize >= 1.3
* python-setuptools
* iv-vocal-tools (only `ccenter_update` is required)

# Installing
As usual, it is recommended to install this package through the RPM that is
provided by SOFTeam. Please ask softeam@interact-iv.com for more details on
where to find said RPM. If an RPM is not available for the version you require,
it is always possible to install everything from source, however, dependencies
will have to managed manually.

# Scripts
#### iv-banners-migrate (obsolete)
This obsolete script was used to switch a project from vintage mode to mcanal mode.

#### iv-clean-entrypoints (migrate on cst-admin)
This script deletes obsolete entrypoints from Voip Configuration.

It would be best to migrate this on a script called cst-admin that would be installed/updated alongside iv-vocal-server-applib and would therefore always match the version of the server it's aimed at.

#### iv-fix-1713 (obsolete)
This script was used to fix supervisors desynchronisation on a webadmin (missing agentsup and stuff like that).

It is totally obsolete as these have been migrated to API Server.

#### iv-force-no-anonymous (migrate on iap-admin and find a better name for this command)
This script updates all webadmin profiles configurations to enforce pure outgoing calls agent's leg is not anonymous.

It has been used in Italy (legal issue about pricing being dependant of source and destination). It is obsolete in its actual form and needs to be migrated on iap-admin.

#### iv-import-records (obsolete with Records API update)
This script was used to import records from WebAdmin to records-api. It is obsolete as soon as Records API update hits production.

I don't think migrating it anywhere would be worth it considering records api update is almost out.

#### iv-new-project (migrate on cst-admin)
This script creates a new project on a vocal server using a static ports configuration.

It would be best to migrate this on a script called cst-admin that would be installed/updated alongside iv-vocal-server-applib and would therefore always match the version of the server it's aimed at.

#### iv-remove-project (migrate on cst-admin)
This script removes a project from a vocal server.

It also removes all references to this project:
 - references in voip process configuration (to its store),
 - references in voip configuration (entrypoints),
 - its store directory,

It would be best to migrate this on a script called cst-admin that would be installed/updated alongside iv-vocal-server-applib and would therefore always match the version of the server it's aimed at.

#### iv-restart-modules (useless)
This script:
 - stops the middleware
 - stops the mail
 - restarts api server
 - starts the mail
 - starts the middleware

It is unused (I hope) and totally useless. A jenkins / ansible job can do that just fine.

#### iv-sounds-settings (migrate on cst-admin)
This script allows editing of 'sounds_country_cfg' and 'sounds_language_cfg' values.

It would be best to migrate this on a script called cst-admin that would be installed/updated alongside iv-vocal-server-applib and would therefore always match the version of the server it's aimed at.

#### iv-static-ports (migrate on cst-admin)
This is both a script and a library used by most other bash scripts aimed at iv-vocal-server.

It has been used to enforce static ports on a project and is now mainly used as a library.

It would be best to migrate this on a script called cst-admin that would be installed/updated alongside iv-vocal-server-applib and would therefore always match the version of the server it's aimed at.

#### iv-sync (migrate on iap-admin)
This script synchronizes data between API Server and Web Admin.

It would be best to migrate this script to iap-admin to make sure that its version matches the server it's aimed at.

#### iv-toggle-scheduler (migrate on cst-admin)
This script toggles scheduler process on a project.

It would be best to migrate this on a script called cst-admin that would be installed/updated alongside iv-vocal-server-applib and would therefore always match the version of the server it's aimed at.

#### iv-upgrade-mcanal (obsolete)
This script was used to upgrade a project from IV2US 2.1 to IV2US 2.3+ architecture.

It hasn't been upgraded in 2 years and is probably totally obsolete by now. It might be an inspiration to improve the current procedure for projects upgrade from callflow to callcontact.

#### iv-vocal-project-values (migrate on cst-admin /!\ but python 2.7 dependent)
This script allows editing SIP oriented configuration values in Ccxml.xml configuration:
 - country_cfg
 - whitelabel_cfg
 - project_cfg
 - p_asserted_identity_cfg

It's a python script based on cnx_ccc_xml_tk python library.

It would be best to migrate this on a script called cst-admin that would be installed/updated alongside iv-vocal-server-applib and would therefore always match the version of the server it's aimed at. But it's python 2.7 dependent.
