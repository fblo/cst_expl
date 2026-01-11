%define		shortname	cccp

Name:		pypy-%{shortname}
Version:	%{_iv_pkg_version}
Release:	%{_iv_pkg_release}%{?dist}
Summary:	Interact-IV's CCCP Library

%define		_package_	%{name}-%{version}

Group:		Applications/System
License:	Proprietary
URL:		http://github.com/interact-iv/iv-cccp
Source0:	%{shortname}-%{version}.tar.gz
BuildRoot:	%{_tmppath}/%{_package_}-%{release}-root-%(%{__id_u} -n)

BuildArch:		noarch

BuildRequires:	pypy-portable

Requires:	pypy-portable
Requires:	pypy-twisted-iv-commons >= 1.1.0

%description
TBA

%prep
%setup -q -n %{shortname}-%{version}

%build
CFLAGS="$RPM_OPT_FLAGS" pypy setup.py build

%install
rm -rf %{buildroot}

pypy setup.py install \
	--skip-build \
	--root $RPM_BUILD_ROOT

%post

%clean
rm -rf $RPM_BUILD_ROOT

%files
/opt/pypy/site-packages

%changelog
* Thu Feb 20 2020 Guilhem Richard <gric@interact-iv.com> 1.4.5
- #988

* Wed Jan 29 2020 Guilhem Richard <gric@interact-iv.com> 1.4.4
- Added #961.

* Fri Nov 30 2018 Julien Tagneres <jtag@interact-iv.com> 1.4.3
- Fixed agent's disponibility indicator #777.

* Mon Nov 26 2018 Julien Tagneres <jtag@interact-iv.com> 1.4.2
- Fixed mail indicators issue #776.
- Fixed some disconnected agents appearing in indicators #761.

* Wed May 02 2018 Julien Tagneres <jtag@interact-iv.com> 1.4.1
- Implemented ignored profiles when retrieving all indicators #706.

* Mon Apr 23 2018 Julien Tagneres <jtag@interact-iv.com> 1.4.0
- Handle "undefined" values for call history and records from Dispatch #695.
- Forward indicator value for callback_url feature #692.
- Reinitialise withdrawal indicators only if necessary #685.

* Fri Mar 23 2018 Julien Tagneres <jtag@interact-iv.com> 1.3.1-2
- Fixed logic issue.

* Fri Mar 23 2018 Julien Tagneres <jtag@interact-iv.com> 1.3.1
- Fixed a typo, a log and a value not being parsed correctly (#672).

* Thu Mar 22 2018 Julien Tagneres <jtag@interact-iv.com> 1.3.0
- Now parsing true json from iv-vocal-server (#672).
- Removed demjson dependency.

* Wed Dec 13 2017 Julien Tagneres <jtag@interact-iv.com> 1.2.2
- Handle 'undefined' update on some indicators #603.

* Thu Dec 07 2017 Julien Tagneres <jtag@interact-iv.com> 1.2.1
- Fixed error message.

* Thu Nov 30 2017 Julien Tagneres <jtag@interact-iv.com> 1.2.0
- Fixed possible issue that would stop indicators update
(communications and records) #563
- Implemented indicator for target availability in address book #338.
- Implemented 'Since' indicator for supervisors #298.
- Improved connexion mode indicator (phone / api / banner ...) #290.

* Tue Oct 03 2017 Julien Tagneres <jtag@interact-iv.com> 1.1.1
- Fixed regression on indicator (#572).
- Fixed history order issue (#574).

* Fri Sep 22 2017 Julien Tagneres <jtag@interact-iv.com> 1.1.0
- Implemented new version of History (#566).
- Updated iv-commons required version to 1.1.0.

* Fri Aug 18 2017 Julien Tagneres <jtag@interact-iv.com> 1.0.0
- Final pypy release.
- Updated iv-commons required version to 1.0.0.

* Thu Aug 03 2017 Julien Tagneres <jtag@interact-iv.com> 0.18.2-2
- First attempt at packaging with pypy.

* Thu Jun 29 2017 Julien Tagneres <jtag@interact-iv.com> 0.18.2
- Fixed QoS initial value (#516).
- Fixed issue with spy (#526).

* Fri Jun 16 2017 Julien Tagneres <jtag@interact-iv.com> 0.18.1
- Fixed display name in history (part of #177).
- Fixed outbound max contact duration indicator (part of #354).

* Fri Jun 09 2017 Julien Tagneres <jtag@interact-iv.com> 0.18.0
- Implemented outbound indicators (#354).
- Implemented calls history indicator (#177).

* Thu Apr 20 2017 Julien Tagneres <jtag@interact-iv.com> 0.17.2
- Fixed vocal host change check (#455).

* Tue Apr 11 2017 Julien Tagneres <jtag@interact-iv.com> 0.17.1
- Fixed indicators initial values (#443 and #450).
- Fixed issue with records feed (#459).

* Thu Mar 02 2017 Julien Tagneres <jtag@interact-iv.com> 0.17.0
- Added current spies indicator (#430).
- Implemented explorer client to kill vocal sessions (#440).

* Wed Jan 18 2017 Julien Tagneres <jtag@interact-iv.com> 0.16.0
- Updated logs for service commands externalization (#385).
- Removed virtual queues from subscriptions (#398).
- Fixed indicator update issue when update occurs during logout (#402).
- Updated iv-commons required version to 0.8.0.

* Fri Dec 09 2016 Julien Tagneres <jtag@interact-iv.com> 0.15.0-2
- Fixed typo.

* Thu Dec 08 2016 Julien Tagneres <jtag@interact-iv.com> 0.15.0
- Implemented records retrieval for phone logged agents (#289).
- Handle "ask_for_disconnect" event from consistent (#365).
- Implemented indicators for API (#91).

* Thu Oct 08 2016 Julien Tagneres <jtag@interact-iv.com> 0.14.0
- Updated record queries (#76 for IV2US#288).

* Wed Aug 24 2016 Julien Tagneres <jtag@interact-iv.com> 0.13.1
- Fixed Users Count indicator (#75 for IV2US#179).

* Mon Aug 22 2016 Julien Tagneres <jtag@interact-iv.com> 0.13.0
- Implemented count indicators: withdrawn, outbound, supervision
(#73 for IV2US#179).

* Mon Aug 08 2016 Julien Tagneres <jtag@interact-iv.com> 0.12.3
- Renamed indicators (#71 for IV2US#268).

* Thu Jul 28 2016 Julien Tagneres <jtag@interact-iv.com> 0.12.2-2
- Fixed regression on last task start date indicator (#69 for IV2US#271).

* Mon Jul 25 2016 Julien Tagneres <jtag@interact-iv.com> 0.12.2
- Fixed average waiting and ringing indicators definitions
(#66 and #67 for IV2US#261).

* Wed Jul 13 2016 Julien Tagneres <jtag@interact-iv.com> 0.12.1
- Fixed average contact duration on agents and queues (#64 for IV2US#259).

* Mon Jul 11 2016 Julien Tagneres <jtag@interact-iv.com> 0.12.0
- Implemented session and queue indicators (#53, #54, #55, #56, #57, #58, #59
and #60 for IV2US#48).

* Mon May 23 2016 Julien Tagneres <jtag@interact-iv.com> 0.11.1
- Fixed issue related to indicators reset for communications
(#48 for IV2US#193).
- Fixed call stuck in communications view when caller hang up during transfer
(#47 for IV2US#183).
- Fixed issue with indicators reset (#45 for IV2US#152).

* Tue May 03 2016 Julien Tagneres <jtag@interact-iv.com> 0.11.0
- Bumped required version of ivcommons to 0.7.1.
- Fixed #40 and #41 for IV2US#160 (Errors on communications indicators).
- Improved vocal server clients (#43 for IV2US#146).

* Wed Apr 13 2016 Julien Tagneres <jtag@interact-iv.com> 0.10.0
- Added missing iv-commons dependency.
- Refactored Dispatch client using IVReconnectingClientFactory in order to
make multiple clients connection independent (#39 for IV2US#103).

* Fri Mar 11 2016 Julien Tagneres <jtag@interact-iv.com> 0.9.0
- Fixed #32, part of INTERACT-IV/IV2US#66:
record with transfer not visible.
- Fixed #34, part of INTERACT-IV/IV2US#50:
erroneous values for call duration (seen in iv-live-supervisor).
- Handled #35, part of INTERACT-IV/IV2US#57:
Optimisations and memory leak fixes.
- Implemented #36, part of INTERACT-IV/IV2US#55:
record every call for one day).

* Mon Jan 11 2016 Julien Tagneres <jtag@interact-iv.com> 0.8.6-2
- Fixed double delete in real time indicators.

* Fri Jan 08 2016 Julien Tagneres <jtag@interact-iv.com> 0.8.6
- Fixed INTERACT-IV/IV2US-6.

* Fri Dec 04 2015 Julien Tagneres <jtag@interact-iv.com> 0.8.5
- Fixed IV2US-2227.

* Wed Oct 14 2015 Julien Tagneres <jtag@interact-iv.com> 0.8.4
- Fixed IV2US-2161, 2190, 2191, 2192 and 2193.

* Mon Oct 12 2015 Julien Tagneres <jtag@interact-iv.com> 0.8.3
- Fixed IV2US-2161, 2168, 2173, 2174, 2176 and 2181.

* Wed Sep 30 2015 Julien Tagneres <jtag@interact-iv.com> 0.8.2
- Fixed IV2US-2132 and 2137.

* Fri Sep 18 2015 Julien Tagneres <jtag@interact-iv.com> 0.8.1
- Fixed few indicators issues.

* Mon Aug 31 2015 Julien Tagneres <jtag@interact-iv.com> 0.8.0
- Implemented tasks real time indicators using new tasks resource.

* Mon Jun 22 2015 Julien Tagneres <jtag@interact-iv.com> 0.7.0
- Implemented records real time indicators.
- Implemented supervision real time indicators.
- Updated subscription API (used by iv-middleware-server).

* Tue Jun 09 2015 Julien Tagneres <jtag@interact-iv.com> 0.6.1
- Implemented 'needs_control' handler (was responsible for agents not being
able to log in) (IV2US-1860).
- Use queues name instead of display name as identifier (made things cleaner).

* Mon May 25 2015 Julien Tagneres <jtag@interact-iv.com> 0.6.0
- Implemented indicators type: list (IV2US-1785).
- Implemented queries to retrieve vocal indicators for supervisor (IV2US-1786)

* Fri Jan 23 2015 Julien Tagneres <jtag@interact-iv.com> 0.5.1-16
- Implemented IV2US-1725: added numerator / denominator in details.

* Tue Jan 20 2015 Julien Tagneres <jtag@interact-iv.com> 0.5.0-1
- Enhanced implementation of design pattern "Observer" for IV2US-1400 and 1402.

* Fri Jan 09 2015 Julien Tagneres <jtag@interact-iv.com> 0.4.0-1
- Implemented usage of design pattern "Observer" (IV2US-1402).
- Enhanced "login failed" handling (IV2US-1677).

* Wed Oct 08 2014 Julien Tagneres <jtag@interact-iv.com> 0.3.1-8
- Fixed missing demjson dependency.

* Wed Aug 13 2014 Julien Tagneres <jtag@interact-iv.com> 0.3.1-7
- Fixed IV2US-1366 and IV2US-1358.

* Fri Jul 11 2014 Julien Tagneres <jtag@interact-iv.com> 0.3.1-6
- Fixed IV2US-1350.

* Fri Jul 04 2014 Julien Tagneres <jtag@interact-iv.com> 0.3.1-4
- Fixed IV2US-1334: Initial value not provided when adding a new vocal service
indicator.

* Wed Jul 02 2014 Julien Tagneres <jtag@interact-iv.com> 0.3.1-3
- Fixed IV2US-1280 and IV2US-1329: issues with voice indicators.

* Mon Jun 23 2014 Julien Tagneres <jtag@interact-iv.com> 0.3.1-2
- Fixed IV2US-1291, 1280 and 1300: issues with voice indicators
- Fixed IV2US-1292: Erroneous 'not manageable' indicator xquery.

* Mon Jun 16 2014 Julien Tagneres <jtag@interact-iv.com> 0.3.1-1
- Fixed IV2US-1279

* Wed Apr 30 2014 Julien Tagneres <jtag@interact-iv.com> 0.3.0-2
- Fixed IV2US-1203

* Wed Apr 16 2014 Julien Tagneres <jtag@interact-iv.com> 0.3.0-1
- Implemented cccp-twisted clients (IV2US-1099)

* Wed Feb 05 2014 Sebastian Lauwers <slau@interact-iv.com> 0.2.2-1
- Added Jenkins-compatible SPEC file to source repository.

* Tue Jan 21 2014 Sebastian Lauwers <slau@interact-iv.com> 0.2.1-1
- Some bugfixes.
- Indentation errors fixed.
- Improved code readability.
- Enable multi-views.
- Share system_id betweeen all DispatchSubscribers.

* Tue Jan 21 2014 Sebastian Lauwers <slau@interact-iv.com> 0.2.0-2
- Added version information to dependencies.

* Mon Oct 07 2013 Sebastian Lauwers <slau@interact-iv.com> 0.2.0-1
- Loads of bugfixes and some new features.

* Sat Aug 31 2013 Sebastian Lauwers <slau@interact-iv.com> 0.1.0-1
- First attempt at packaging cccp.
