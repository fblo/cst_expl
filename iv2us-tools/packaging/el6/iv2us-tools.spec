%define     company interact-iv

Name:       iv2us-tools
Version:    %{_iv_pkg_version}
Release:    %{_iv_pkg_release}%{?dist}
Summary:    Interact-IV's IV2US Tools

%define     _package_ %{name}-%{version}

Group:      Applications/System
License:    Proprietary
URL:        http://github.com/%{company}/iv2us-tools
Source0:    %{_package_}.tar.gz
BuildRoot:  %{_tmppath}/%{_package_}-%{release}-root-%(%{__id_u} -n)

BuildArch:  noarch

BuildRequires:  python-setuptools
BuildRequires:  python MySQL-python
BuildRequires:  python-twisted >= 13.2.0-1
BuildRequires:  python-twisted-iv-commons >= 1.3.3
BuildRequires:  python-argparse >= 1.2.1-2
BuildRequires:  python-phpserialize >= 1.3-1
BuildRequires:  iv-vocal-tools >= 2.9.0.1
BuildRequires:  cnx-ccc-xml-tk >= 0.0.1

Requires:       python MySQL-python
Requires:       python-twisted >= 13.2.0-1
Requires:       python-twisted-iv-commons >= 1.3.3
Requires:       python-argparse >= 1.2.1-2
Requires:       python-phpserialize >= 1.3-1
Requires:       iv-vocal-tools >= 2.9.0.1
Requires:       cnx-ccc-xml-tk >= 0.0.1


%description
TBA


%prep
%setup -q


%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build


%install
# Ensure root is clean
rm -rf %{buildroot}

# Install script
%{__python} setup.py install \
	--skip-build \
	--root $RPM_BUILD_ROOT \
	--prefix /usr


%clean
rm -rf $RPM_BUILD_ROOT


%files
/usr/bin/iv-banners-migrate
/usr/bin/iv-clean-entrypoints
/usr/bin/iv-fix-1713
/usr/bin/iv-force-no-anonymous
/usr/bin/iv-import-records
/usr/bin/iv-sync
/usr/bin/iv-new-project
/usr/bin/iv-remove-project
/usr/bin/iv-restart-modules
/usr/bin/iv-static-ports
/usr/bin/iv-sounds-settings
/usr/bin/iv-toggle-scheduler
/usr/bin/iv-vocal-project-values
/usr/bin/sync-vocal-entrypoints
/usr/bin/replay_records

%{python_sitelib}/ivsync
%{python_sitelib}/iv2us_tools*.egg-info


%changelog
* Tue May 28 2020 Guilhem Richard <gric@interact-iv.com> 1.1.13
- #1061.

* Mon May 18 2020 Guilhem Richard <gric@interact-iv.com> 1.1.12
- #1056.

* Mon Apr 27 2020 Guilhem Richard <gric@interact-iv.com> 1.1.11
- #1042.

* Tue Feb 18 2020 Guilhem Richard <gric@interact-iv.com> 1.1.9
- #983, #878.

* Mon Dec 09 2019 Guilhem Richard <gric@interact-iv.com> 1.1.8
- #893.

* Wed Dec 04 2019 Guilhem Richard <gric@interact-iv.com> 1.1.7
- #881, #893, #890.

* Wed Nov 27 2019 Guilhem Richard <gric@interact-iv.com> 1.1.6
- Somes fixes #914.

* Tue Jul 30 2019 Guilhem Richard <gric@interact-iv.com> 1.1.5
- Sync profiles #858.
- Sync queues #859.
- Sync scenarios/folders #857.
- Sync soundfilesfolders/files #852.
- Sync entrypoints #854.

* Tue Jul 30 2019 Guilhem Richard <gric@interact-iv.com> 1.1.4
- Fix sync on supervised profiles/folders.

* Wed Jul 17 2019 Guilhem Richard <gric@interact-iv.com> 1.1.3
- Fix some errors due observed during delivery.

* Wed Jul 17 2019 Guilhem Richard <gric@interact-iv.com> 1.1.2
- Sync agents, agents sup and supervisors #834

* Wed Jun 19 2019 Julien Tagneres <jtag@interact-iv.com> 1.1.1
- Removed 'billing' prefix from unrelated values.
- Updated iv-vocal-tools required version to 2.9.0.1.

* Tue Apr 30 2019 Julien Tagneres <jtag@interact-iv.com> 1.1.0-2
- Updated iv-vocal-tools required version to 2.9.0.0.

* Mon Apr 29 2019 Julien Tagneres <jtag@interact-iv.com> 1.1.0
- Added cnx-ccc-xml-tk dependency.
- Added iv-vocal-project-values script.

* Wed Apr 03 2019 Julien Tagneres <jtag@interact-iv.com> 1.0.5
- Fixed missing quotes.

* Wed Apr 03 2019 Julien Tagneres <jtag@interact-iv.com> 1.0.4
- Fixed read being used instead of read_all in ivsync.

* Tue Apr 02 2019 Julien Tagneres <jtag@interact-iv.com> 1.0.3
- Added "apionly" option on ivsync for testing purpose #811.

* Thu Mar 14 2019 Julien Tagneres <jtag@interact-iv.com> 1.0.2
- Fixed encoding issue for migrations #806.

* Thu Feb 07 2019 Julien Tagneres <jtag@interact-iv.com> 1.0.1
- Fixes for special days migration #747.

* Thu Jan 10 2019 Julien Tagneres <jtag@interact-iv.com> 1.0.0
- iv-migrate becomes iv-sync (can be used to resynchronise after first migration) #628.
- Implemented profiles directories synchronisation #741.
- Implemented positions directories synchronisation #743.
- Implemented positions synchronisation #742.
- Implemented queues directories synchronisation #744.
- Implemented agents and supervisors directories synchronisation #746.
- Implemented 'one time' special days migration #747.
- Implemented 'one time' calendars migration #748.
- Implemented update of scenarios calendar objects to use new API #752.
- Updated iv-commons required version to 1.3.0.

* Thu Mar 15 2018 Julien Tagneres <jtag@interact-iv.com> 0.12.6
- Ignore resources with 'N;' configuration in iv-migrate. (#670).
- Added return value to iv-migrate script. (#671).

* Mon Mar 12 2018 Julien Tagneres <jtag@interact-iv.com> 0.12.5
- Made the script more resilient to webadmin's incomplete profiles (#663).

* Fri Mar 09 2018 Julien Tagneres <jtag@interact-iv.com> 0.12.4
- Updated vocal queues migration (#658).
- Implemented client side rate limit to prevent flood (#659).

* Tue Feb 27 2018 Guilhem Richard <gric@interact-iv.com> 0.12.3
- Fixed an issue with iv-migrate script.

* Mon Feb 26 2018 Guilhem Richard <gric@interact-iv.com> 0.12.2
- Improved iv-migrate script (forgotten commit from 0.12.1 branch).

* Wed Feb 14 2018 Julien Tagneres <jtag@interact-iv.com> 0.12.1
- Improved iv-migrate script (#649).

* Fri Feb 09 2018 Julien Tagneres <jtag@interact-iv.com> 0.12.0
- Updated iv-vocal-tools required version to 2.8.1.0
- Updated iv-migrate script to integrate transfer targets (#636).

* Wed Aug 24 2016 Julien Tagneres <jtag@interact-iv.com> 0.10.1
- Updated iv-vocal-tools required version to 2.7.9.1
- Added phone-login.xml to list of copied files in iv-new-project
(#13 for IV2US#191).

* Mon Aug 22 2016 Julien Tagneres <jtag@interact-iv.com> 0.10.0-2
- Updated iv-vocal-tools required version to 2.7.9.0.

* Mon Jul 11 2016 Julien Tagneres <jtag@interact-iv.com> 0.10.0
- Implemented store cleanup in iv-remove-project (#12 for IV2US#255).

* Tue May 03 2016 Julien Tagneres <jtag@interact-iv.com> 0.9.0
- Implemented iv-sounds-settings script (#9 for IV2US#88).
- Bumped iv-vocal-tools required version to 2.7.7.0.

* Tue Apr 19 2016 Julien Tagneres <jtag@interact-iv.com> 0.8.2
- Implemented import for records post upgrade 2.3 (#8 for IV2US#156).

* Wed Apr 13 2016 Julien Tagneres <jtag@interact-iv.com> 0.8.1
- Prevent project creation if dynamic ports are detected (#7 for IV2US#138).

* Mon Apr 11 2016 Julien Tagneres <jtag@interact-iv.com> 0.8.0
- Added iv-restart-modules script.

* Mon Mar 07 2016 Julien Tagneres <jtag@interact-iv.com> 0.7.1
- Some fixes to iv-import-records script.

* Tue Dec 08 2015 Julien Tagneres <jtag@interact-iv.com> 0.7.0
- Added iv-import-records script.

* Thu Nov 19 2015 Julien Tagneres <jtag@interact-iv.com> 0.6.2
- Fixed null config issue (found on CNED) in iv-migrate.
- Updated iv-commons required version.

* Tue Nov 17 2015 Julien Tagneres <jtag@interact-iv.com> 0.6.1
- Fixed Not Modified issue in iv-migrate.
- Updated plague dependency.

* Thu Nov 12 2015 Julien Tagneres <jtag@interact-iv.com> 0.6.0
- Added script to force displayed number to agent's position on agent's leg
during outgoing calls (for Italy).

* Mon Oct 12 2015 Julien Tagneres <jtag@interact-iv.com> 0.5.0
- Added banners migration script.

* Mon Aug 31 2015 Julien Tagneres <jtag@interact-iv.com> 0.4.0
- Added vocal queues syncing in iv-migrate (IV2US-2031).

* Thu Mar 19 2015 Julien Tagneres <jtag@interact-iv.com> 0.3.0
- Added confirmation step before project creation.
- Created iv-remove-project script which removes a project on iv-vocal-server.

* Thu Feb 12 2015 Julien Tagneres <jtag@interact-iv.com> 0.2.1-34
- Fixed issue iv-fix-1713 where an agentsup could be updated with an empty name.

* Wed Feb 11 2015 Julien Tagneres <jtag@interact-iv.com> 0.2.0-29
- Created iv-toggle-scheduler script to enable or disable the scheduler process
of a project.

* Fri Jan 23 2015 Julien Tagneres <jtag@interact-iv.com> 0.1.1-1
- iv-fix-1713 script now checks for duplicates and fixes supagent's ppid.
It also checks if supagent needs to be created.

* Thu Jan 15 2015 Julien Tagneres <jtag@interact-iv.com> 0.1.0-1
- Added iv-fix-1713 script.

* Mon Sep 15 2014 Sebastian Lauwers <slau@interact-iv.com> 0.0.1-1
- Initial packaging script.
