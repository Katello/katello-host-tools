Name: katello-agent
Version: 2.2.0
Release: 2%{?dist}
Summary: The Katello Agent
Group:   Development/Languages
License: LGPLv2
URL:     https://fedorahosted.org/katello/
Source0: https://fedorahosted.org/releases/k/a/katello/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch
BuildRequires: python2-devel
BuildRequires: python-setuptools
BuildRequires: rpm-python
Requires: gofer >= 2.5
Requires: python-gofer-proton >= 2.5
Requires: python-pulp-agent-lib >= 2.6
Requires: pulp-rpm-handlers >= 2.6
Requires: subscription-manager

%description
Provides plugin for gofer, which allows communicating with Katello server
and execute scheduled actions.

%prep
%setup -q

%build
pushd src
%{__python} setup.py build
popd

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/%{_sysconfdir}/gofer/plugins
mkdir -p %{buildroot}/%{_prefix}/lib/gofer/plugins

cp etc/gofer/plugins/katelloplugin.conf %{buildroot}/%{_sysconfdir}/gofer/plugins
cp src/katello/agent/katelloplugin.py %{buildroot}/%{_prefix}/lib/gofer/plugins

mkdir -p %{buildroot}/%{_prefix}/lib/yum-plugins
cp src/yum-plugins/package_upload.py %{buildroot}/%{_prefix}/lib/yum-plugins

mkdir -p %{buildroot}/%{_sysconfdir}/yum/pluginconf.d/
cp etc/yum/pluginconf.d/package_upload.conf %{buildroot}/%{_sysconfdir}/yum/pluginconf.d/package_upload.conf

mkdir -p %{buildroot}%{_sbindir}
cp bin/katello-package-upload %{buildroot}%{_sbindir}/katello-package-upload

%clean
rm -rf %{buildroot}

%post
chkconfig goferd on
service goferd restart

%postun
%if 0%{?fedora} > 18 || 0%{?rhel} > 6
    if systemctl status goferd | grep 'active (running)'; then
        systemctl restart goferd
    fi
%else
    if service goferd status | grep 'is running'; then
        service goferd restart
    fi
%endif

%files
%config(noreplace) %{_sysconfdir}/gofer/plugins/katelloplugin.conf
%{_prefix}/lib/gofer/plugins/katelloplugin.*
%{_sysconfdir}/yum/pluginconf.d/package_upload.conf
%attr(750, root, root) %{_sbindir}/katello-package-upload
%{_prefix}/lib/yum-plugins

%doc LICENSE

%changelog
* Tue Feb 24 2015 Eric D. Helms <ericdhelms@gmail.com> 2.2.0-2
- Bumping release to 2.2.0-2 (ericdhelms@gmail.com)
- Using port: 5647 for dispatch router. (jortel@redhat.com)
- registration fixes. (jortel@redhat.com)
- Using proton; consumer registration validated. (jortel@redhat.com)
- gofer 2.x compat. (jortel@redhat.com)
- refs #9403 - get rhsm certificate from rhsm configration
  (stbenjam@redhat.com)
- fixes #9403 - use correct certificate location (stbenjam@redhat.com)

* Tue Feb 24 2015 Eric D. Helms <ericdhelms@gmail.com>
- Using port: 5647 for dispatch router. (jortel@redhat.com)
- registration fixes. (jortel@redhat.com)
- Using proton; consumer registration validated. (jortel@redhat.com)
- gofer 2.x compat. (jortel@redhat.com)
- refs #9403 - get rhsm certificate from rhsm configration
  (stbenjam@redhat.com)
- fixes #9403 - use correct certificate location (stbenjam@redhat.com)

* Tue Feb 24 2015 Eric D. Helms <ericdhelms@gmail.com>
- Using port: 5647 for dispatch router. (jortel@redhat.com)
- registration fixes. (jortel@redhat.com)
- Using proton; consumer registration validated. (jortel@redhat.com)
- gofer 2.x compat. (jortel@redhat.com)
- refs #9403 - get rhsm certificate from rhsm configration
  (stbenjam@redhat.com)
- fixes #9403 - use correct certificate location (stbenjam@redhat.com)

* Fri Dec 19 2014 David Davis <daviddavis@redhat.com> 2.2.0-1
- fixes #7815 - fixing katello-agent for older subscription-managers
  (jsherril@redhat.com)

* Fri Oct 10 2014 Justin Sherrill <jsherril@redhat.com> 2.1.2-1
- fixes #7815 - fixing package upload feature with new sub-man
  (jsherril@redhat.com)

* Wed Sep 24 2014 Eric D. Helms <ericdhelms@gmail.com> 2.1.1-1
- Fixes #7553: Update ConsumerIdentity location. (ericdhelms@gmail.com)

* Fri Sep 12 2014 Justin Sherrill <jsherril@redhat.com> 2.1.0-1
- bumping version to 2.1 (jsherril@redhat.com)

* Fri Sep 12 2014 Justin Sherrill <jsherril@redhat.com> 2.0.0-1
- bumping version to 2.0 (jsherril@redhat.com)
- refs #7330 / BZ 1136393 - %%postun - only restart goferd when it is running
  (bbuckingham@redhat.com)
- fixes #7330 / BZ 1136393 - katello-agent - update %%postun to support systemd
  (bbuckingham@redhat.com)
- refs #5271 - update for el7 builds (jsherril@redhat.com)
- fixes #6103 - updating package profile after every yum action
  (jsherril@redhat.com)
- fixes #5095 - starting goferd by default (jsherril@redhat.com)

* Tue May 20 2014 Justin Sherrill <jsherril@redhat.com> 1.5.3-1
  (jlsherrill@gmail.com)
- Fix agent requirements for pulp 2.4; catch and report errors sending the
  enabled report. (jortel@redhat.com)

* Fri May 16 2014 Justin Sherrill <jsherril@redhat.com> 1.5.2-1
- Ensure EnabledReport filters by basename. (jortel@redhat.com)
- agent requires gofer >= 1.0.10. (jortel@redhat.com)
- add unit tests. (jortel@redhat.com)
- Refit agent to work with gofer 1.0+ and pulp 2.4+. (jortel@redhat.com)

* Fri Oct 11 2013 Partha Aji <paji@redhat.com> 1.5.1-1
- Bumping package versions for 1.5 (paji@redhat.com)

* Fri Oct 11 2013 Partha Aji <paji@redhat.com> 1.4.5-1
- Implement conduit for pulp 2.3 compat (jortel@redhat.com)
- Autobuild f19 packages (paji@redhat.com)

* Wed Jul 31 2013 Partha Aji <paji@redhat.com> 1.4.4-1
- add katello-nightly-fedora19 to tito.props (msuchy@redhat.com)

* Thu Jun 06 2013 Miroslav Suchý <msuchy@redhat.com> 1.4.3-1
- 893596 - sending up baseurl of repos from katello-agent (jsherril@redhat.com)

* Sat Apr 27 2013 Mike McCune <mmccune@redhat.com> 1.4.2-1
- adding rel-eng directory for new location (mmccune@redhat.com)

* Fri Apr 12 2013 Justin Sherrill <jsherril@redhat.com> 1.4.1-1
- version bump to 1.4 (jsherril@redhat.com)

* Fri Apr 12 2013 Justin Sherrill <jsherril@redhat.com> 1.3.2-1
- remove old changelog entries (msuchy@redhat.com)
- 872528 - restart gofer after katello-agent upgrade (msuchy@redhat.com)

* Mon Jan 07 2013 Justin Sherrill <jsherril@redhat.com> 1.3.1-1
- Refit agent for pulp v2. (jortel@redhat.com)

* Fri Oct 12 2012 Lukas Zapletal <lzap+git@redhat.com> 1.1.3-1
- 

* Fri Aug 24 2012 Miroslav Suchý <msuchy@redhat.com> 1.1.2-1
- 845643 - consistently use rpm macros (msuchy@redhat.com)

* Thu Aug 23 2012 Mike McCune <mmccune@redhat.com> 1.1.1-1
- buildroot and %%clean section is not needed (msuchy@redhat.com)
- Bumping package versions for 1.1. (msuchy@redhat.com)

* Tue Jul 31 2012 Miroslav Suchý <msuchy@redhat.com> 1.0.6-1
- update copyright years (msuchy@redhat.com)
- point Source0 to fedorahosted.org where tar.gz are stored (msuchy@redhat.com)

* Fri Jul 27 2012 Lukas Zapletal <lzap+git@redhat.com> 1.0.5-1
- macro python_sitelib is not used anywhere, removing
- provide more descriptive description
- put plugins into correct location
- build root is not used since el6 (inclusive)
- point URL to our wiki
- %%defattr is not needed since rpm 4.4

* Wed Jun 27 2012 Lukas Zapletal <lzap+git@redhat.com> 1.0.4-1
- 828533 - changing to proper QPIDD SSL port
