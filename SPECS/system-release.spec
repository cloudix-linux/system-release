%define _buildid .1

%bcond_without gpu
%bcond_without upstart

%define product_family cloudix Linux
#dist_version is for dist build tag .cloudix
%define dist_version 1
#%%define beta beta

Summary:        %{product_family} release file
Name:           system-release
Version:        2015.03
Release:        0%{?_buildid}
License:        GPLv2
Group:          System Environment/Base

# sets 1-9 reserved for repository definitions
Source1:        cloudix-main.repo
Source2:        cloudix-master.repo
Source3:        cloudix-updates.repo
Source4:        cloudix-extra.repo

# 10-19 reserved for scripts and other program fare
Source10:        30-banner

# 20-29 reserved for auth and gpg keys

# 30-39 documentation
Source31:       GPL

# 40-onwards cloud-init configurations

Obsoletes:      redhat-release
Provides:       redhat-release
Provides:       system-release = %{version}-%{release}
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
# cloud-init-0.7.2-8 is the first amzn1 release that provides the write-metadata module
Conflicts:      cloud-init < 0.7.2-8
Requires:       yum-plugin-security >= 1.1.30-6.11.amzn1
Requires:       yum-plugin-priorities
Requires:       yum-plugin-upgrade-helper
Requires:       ec2-utils
Requires:       sysctl-defaults
%if %{with upstart}
Requires:       update-motd
%endif

%description
%{product_family} release files

%package obsoletes
Summary:        Obsoletes packages no longer provided
Group:          System Environment/Base
# cleanup packages from previous releases that no longer are supposed to be
# used in this release:
Obsoletes:      hal
Obsoletes:      hal-devel
Obsoletes:      hal-docs
Obsoletes:      hal-info
Obsoletes:      hal-storage-addon
Obsoletes:      libieee1284
Obsoletes:      libieee1284-devel
Obsoletes:      libieee1284-python
Obsoletes:      mcelog
Obsoletes:      nagios-plugins-sensors
Obsoletes:      nash-devel
Obsoletes:      opensm
Obsoletes:      opensm-devel
Obsoletes:      opensm-libs
Obsoletes:      opensm-static
Obsoletes:      pm-utils
Obsoletes:      pm-utils-devel

%description obsoletes
This package obsoletes packages which are no longer provided
usually because they are not relevant to %{product_family}

%prep
%setup -q -c -T
cp %{SOURCE31} ./GPL

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/etc
echo "%{product_family} release %{version}" > $RPM_BUILD_ROOT/etc/system-release
cp $RPM_BUILD_ROOT/etc/system-release $RPM_BUILD_ROOT/etc/issue
echo "Kernel \r on an \m" >> $RPM_BUILD_ROOT/etc/issue
cp $RPM_BUILD_ROOT/etc/issue $RPM_BUILD_ROOT/etc/issue.net
echo >> $RPM_BUILD_ROOT/etc/issue

cat << EOF > $RPM_BUILD_ROOT/etc/os-release
NAME="cloudix Linux"
VERSION="%{version}"
ID="cloudix"
ID_LIKE="rhel fedora"
VERSION_ID="%{version}"
PRETTY_NAME="cloudix Linux %{version}"
ANSI_COLOR="0;33"
HOME_URL="http://cloudix-linux.com/"
EOF

mkdir -p -m 755 $RPM_BUILD_ROOT/etc/pki/rpm-gpg

# Setup repo definitions
install -d -m 755 $RPM_BUILD_ROOT/etc/yum.repos.d/
install -m 644 %{SOURCE1} $RPM_BUILD_ROOT/etc/yum.repos.d/
install -m 644 %{SOURCE2} $RPM_BUILD_ROOT/etc/yum.repos.d/
install -m 644 %{SOURCE3} $RPM_BUILD_ROOT/etc/yum.repos.d/
install -m 644 %{SOURCE4} $RPM_BUILD_ROOT/etc/yum.repos.d/

# Setup yum vars for repo definitions
install -d -m 755 $RPM_BUILD_ROOT/etc/yum/vars/

%if %{with upstart}
# Install banner MOTD script
install -d -m 755 $RPM_BUILD_ROOT/etc/update-motd.d
install -m 755 %{SOURCE10} $RPM_BUILD_ROOT/etc/update-motd.d/
%endif

# Install cloud-init configuration
install -d -m 755 $RPM_BUILD_ROOT/etc/cloud/cloud.cfg.d

# Set up the dist tag macros
install -d -m 755 $RPM_BUILD_ROOT/etc/rpm
cat >> $RPM_BUILD_ROOT/etc/rpm/macros.disttag << EOF
# dist macros

%%cloudix               %{dist_version}
%%dist          .cloudix%{dist_version}
%%cloudix%{dist_version}             1

%%distribution %{product_family}

%%_without_X11       1
%%_without_gcj_support 1
EOF
#adding checkbuild macro
printf %s%b "%" "__arch_install_post /usr/lib/rpm/check-buildroot\n" >> $RPM_BUILD_ROOT/etc/rpm/macros.checkbuild

# Symlink to the version-specific doc dir
install -d -m 755 $RPM_BUILD_ROOT%{_docdir}/
ln -s %name-%version $RPM_BUILD_ROOT%{_docdir}/%name

# Add a README for to make the obsoletes package not empty
cat <<EOF > README
This package exists to obsolete packages which are no longer provided.
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%attr(0644,root,root) /etc/system-release
%attr(0644,root,root) /etc/os-release
%doc GPL
%config(noreplace) %attr(0644,root,root) /etc/issue
%config(noreplace) %attr(0644,root,root) /etc/issue.net
%config %attr(0644,root,root) /etc/rpm/macros.disttag
%config %attr(0644,root,root) /etc/rpm/macros.checkbuild
%config /etc/yum.repos.d/cloudix-main.repo
%config /etc/yum.repos.d/cloudix-master.repo
%config /etc/yum.repos.d/cloudix-updates.repo
%config /etc/yum.repos.d/cloudix-extra.repo
#/usr/share/firstboot/modules/eula.py*
#/usr/share/eula/eula.*
%dir /etc/pki/rpm-gpg
/etc/pki/rpm-gpg/*
# release notes
%{_docdir}/%name
%if %{with upstart}
# update-motd scripts
/etc/update-motd.d/30-banner
%endif

%files obsoletes
%doc README

%changelog
* Wed Feb 11 2015 Ben Cressey <bcressey@amazon.com>
- Obsolete packages we no longer ship

* Tue Jan 20 2015 Ben Cressey <bcressey@amazon.com>
- Update to 2015.03

* Thu Sep 18 2014 Ben Cressey <bcressey@amazon.com>
- Require sysctl-defaults

* Fri Aug 8 2014 Ian Weller <iweller@amazon.com>
- Don't overwrite cloud_config_modules

* Tue Aug 5 2014 Lee Trager <ltrager@amazon.com>
- Add /etc/os-release

* Fri Jul 25 2014 Ian Weller <iweller@amazon.com>
- Use static repo files with new $awsregion and $awsdomain yum vars

* Mon Jul 14 2014 Ian Weller <iweller@amazon.com>
- Update to 2014.09

* Wed Mar 12 2014 Andrew Jorgensen <ajorgens@amazon.com>
- Require newer cloud-init and improve the way it does .repo generation

* Thu Feb 27 2014 Andrew Jorgensen <ajorgens@amazon.com>
- Revert "Add a macros.dist-build"

* Fri Feb 21 2014 Andrew Jorgensen <ajorgens@amazon.com>
- Add a macros.dist-build

* Wed Feb 19 2014 Tom Kirchner <tjk@amazon.com>
- Update to 2014.03

* Thu Oct 10 2013 Andrew Jorgensen <ajorgens@amazon.com>
- Improve the available updates update-motd.d script

* Tue Aug 27 2013 Ethan Faust <efaust@amazon.com>
- Add report_instanceid

* Wed Aug 21 2013 Tom Kirchner <tjk@amazon.com>
- Update to 2013.09

* Tue Jan 22 2013 Lee Trager <ltrager@amazon.com> - 2013.03-0
- Update version to 2013.03

* Tue Jan 22 2013 Lee Trager <ltrager@amazon.com>
- Update to 2013.03

* Mon Sep 17 2012 Cristian Gafton <gafton@amazon.com>
- add upgrade-helper as a pluging for upgrades

* Tue Aug 14 2012 Andrew Jorgensen <ajorgens@amazon.com> - 2012.09-0
- Update version to 2012.09
- Change priority of .repo files to 10 to allow higher priorities

* Tue Aug 14 2012 Andrew Jorgensen <ajorgens@amazon.com>
- 2012.09 and change priority of .repo files to 10 to allow higher priorities

* Tue Mar 27 2012 Andrew Jorgensen <ajorgens@amazon.com> - 2012.03-7
- Move the release notes to the web

* Tue Mar 27 2012 Andrew Jorgensen <ajorgens@amazon.com>
- Move release notes to the web

* Tue Mar 20 2012 Andrew Jorgensen <ajorgens@amazon.com>
- Add an obsoletes package to handle packages which are no longer provided

* Mon Mar 19 2012 Andrew Jorgensen <ajorgens@amazon.com>
- Handle upgrade path from -hvm to -gpu

* Mon Mar 5 2012 Pan Gu <pangu@amazon.com>
- Update repo template files to add timeouts/retries settings

* Thu Feb 23 2012 Andrew Jorgensen <ajorgens@amazon.com> - 2012.03-5
- Obsolete hal, hal-info, and mcelog

* Thu Feb 23 2012 Andrew Jorgensen <ajorgens@amazon.com>
- Obsolete packages we are no longer including

* Mon Feb 20 2012 Cristian Gafton <gafton@amazon.com>
- rebuild for Amazon Linux AMI

* Sat Feb 18 2012 Cristian Gafton <gafton@amazon.com>
- let the meta python package handle the install and content of the macros.python file

* Fri Feb 17 2012 Cristian Gafton <gafton@amazon.com> - 2012.03-3
- move the handling of macros.python into the python package

* Fri Feb 17 2012 Andrew Jorgensen <ajorgens@amazon.com> - 2012.03-3
- Rename hvm to gpu and add a preview repo

* Fri Feb 17 2012 Andrew Jorgensen <ajorgens@amazon.com>
- Fix Obsoletes versions for system-release-hvm
- Add a warning to repo template files that changes may be overwritten
- Rename hvm repo to gpu and add preview repo

* Fri Jan 20 2012 Andrew Jorgensen <ajorgens@amazon.com>
- Update version

* Tue Jan 3 2012 Andrew Jorgensen <ajorgens@amazon.com>
- Only tell users how to apply if there are updates available
- Tell users how to apply updates

* Fri Oct 28 2011 Andrew Jorgensen <ajorgens@amazon.com>
- Use debuginfo/mirror.list instead of debuginfo-mirror.list

* Thu Oct 27 2011 Andrew Jorgensen <ajorgens@amazon.com>
- 2011.09 R2

* Thu Oct 27 2011 Nathan Blackham <blackham@amazon.com>
- Conditionalize hvm and upstart support

* Thu Oct 27 2011 Andrew Jorgensen <ajorgens@amazon.com>
- No gpg check for nosrc repo

* Thu Oct 13 2011 Cristian Gafton <gafton@amazon.com>
- add a post install script to the system-config-hvm package to regenerate the yum repo configs as well

* Fri Oct 7 2011 Andrew Jorgensen <ajorgens@amazon.com>
- Use better output from patched yum security plugin

* Tue Sep 20 2011 Andrew Jorgensen <ajorgens@amazon.com>
- Reduce mirror timeouts for yum config in ALAMI
- Remove the amzn-ami doc dir as it is only a dup of the release notes in the usual dir

* Tue Sep 13 2011 Andrew Jorgensen <ajorgens@amazon.com>
- JIRA AL-1694: MOTD release notes path is incorrect

* Thu Aug 25 2011 Cristian Gafton <gafton@amazon.com>
- correct the %%post script to only run on upgrade paths
- add post script that will regenerate the yum repository configuration

* Wed Aug 24 2011 Andrew Jorgensen <ajorgens@amazon.com>
- Disable nosrc by default
- Add system-update MOTD script to files list (oops)
- Added system-update MOTD script

* Wed Aug 17 2011 Cristian Gafton <gafton@amazon.com>
- updated repository templates for new repo urls

* Mon Aug 15 2011 Andrew Jorgensen <ajorgens@amazon.com>
- Only print message if not empty
- repo templates to use $releasever and ga key properly
- Only print if the check-update worked

* Wed Aug 10 2011 Matt Wilson <msw@amazon.com>
- remove extra cp statement
- add GA GPG key. Use $releasever in repository templates

* Mon Aug 8 2011 Andrew Jorgensen <ajorgens@amazon.com>
- Put the release notes message below
- Only show available updates if there are any

* Thu Aug 4 2011 Cristian Gafton <gafton@amazon.com>
- cleanup packages from previous releases that are no longer usable

* Wed Jul 27 2011 Andrew Jorgensen <ajorgens@amazon.com>
- Use update-motd for MOTD

* Mon Jul 25 2011 Andrew Jorgensen <ajorgens@amazon.com>
- Modify CPE generation in system-release to only include the base release numbering, i.e. 2011.09

* Fri Jun 10 2011 Nathan Blackham <blackham@amazon.com> - 2011.02-1
- adding hvm update repo to the hvm subpackage

* Fri Jun 10 2011 Cristian Gafton <gafton@amazon.com>
- fix sourcename for hvm update repo template

* Fri Jun 10 2011 Nathan Blackham <blackham@amazon.com>
- adding hvm updates repo template to hvm subpackage
- Adding hvm updates to their own repo file.
- added hvm updates

* Thu Feb 24 2011 Cristian Gafton <gafton@amazon.com>
- add Requires for ec2-utils
- build release 2011.02

* Wed Feb 23 2011 Cristian Gafton <gafton@amazon.com>
- fix typo in requires for hvm subpackage
- add subpackage for hvm template

* Tue Feb 22 2011 Cristian Gafton <gafton@amazon.com> - 2011.02-0
- add subpackage for hvm template

* Fri Jan 28 2011 Cristian Gafton <gafton@amazon.com>
- fix image release notes pathname

* Thu Jan 27 2011 Nathan Blackham <blackham@amazon.com>
- fixing verison number
- fixing typo

* Thu Jan 27 2011 Cristian Gafton <gafton@amazon.com>
- update version number
- integrate release notes

* Thu Jan 27 2011 Nathan Blackham <blackham@amazon.com>
- adding repo templates adding conflicts to spec file adding yum plugin requires to spec file

* Wed Jan 26 2011 Cristian Gafton <gafton@amazon.com> - 2010.11-1
- add release notes

* Fri Nov 5 2010 Nathan Blackham <blackham@amazon.com>
- moving to date based release numbering

* Fri Jul 23 2010 Matt Wilson <msw@amazon.com>
- bump release
- add RPM-GPG-KEY-amazon-beta

* Tue Jul 20 2010 Matt Wilson <msw@amazon.com>
- bump release
- rename gcj variable to match jpackage

* Mon Jul 19 2010 Nathan Blackham <blackham@amazon.com>
- rebuild
- add full name to product line

* Mon Jul 19 2010 Matt Wilson <msw@amazon.com>
- remove release_variant bit

* Sat Jul 17 2010 Cristian Gafton <gafton@amazon.com>
- add _without_GCJ and define the python_sitearch and python_sitelib as equivalents to their corresponding _python_ versions

* Tue Jul 13 2010 Nathan Blackham <blackham@amazon.com>
- rebuild

* Tue Jul 13 2010 Matt Wilson <msw@amazon.com>
- initial system-release .spec file

* Mon Jul 12 2010 Matt Wilson <msw@amazon.com>
- setup complete for package system-release

* Sun Jul  4 2010 Cristian Gafton <gafton@amazon.com> - 1-0.6.4
- unpack the too-small-to-matter tar.gz file and use multiple source files instead

* Thu Jun 24 2010 Nathan Blackham <blackham@amazon.com>
- adding macros from buildsys-macros

* Wed Jun 16 2010 Nathan Blackham <blackham@amazon.com>
- modifing repo file

* Wed Apr 07 2010 Nathan Blackham <blackham@amazon.com>
- initial build
