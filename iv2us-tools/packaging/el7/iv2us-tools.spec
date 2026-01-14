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
BuildRequires:  python-twisted >= 16.0
BuildRequires:  python-twisted-iv-commons >= 1.3.3
BuildRequires:  python-phpserialize >= 1.3
BuildRequires:  iv-vocal-tools >= 2.9.0.0
BuildRequires:  cnx-ccc-xml-tk >= 0.0.1

Requires:       python MySQL-python
Requires:       python-twisted >= 16.0
Requires:       python-twisted-iv-commons >= 1.3.3
Requires:       python-phpserialize >= 1.3
Requires:       iv-vocal-tools >= 2.9.0.0
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

* Tue Jan 15 2019 Julien Tagneres <jtag@interact-iv.com> 1.0.0
- First attempt at packaging iv2us-tools for Cent OS 7.
