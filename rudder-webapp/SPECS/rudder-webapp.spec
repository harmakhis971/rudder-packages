#####################################################################################
# Copyright 2011 Normation SAS
#####################################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, Version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#####################################################################################

#=================================================
# Specification file for rudder-webapp
#
# Installs Rudder's WAR files
#
# Copyright (C) 2011 Normation
#=================================================

#=================================================
# Variables
#=================================================
%define real_name        rudder-webapp

%define rudderdir        /opt/rudder
%define ruddervardir     /var/rudder
%define rudderlogdir     /var/log/rudder

%define maven_settings settings-external.xml

%if 0%{?sles_version}
%define apache              apache2
%define apache_tools        apache2-utils
%define apache_group        www
%define htpasswd_cmd        htpasswd2
%define sysloginitscript    /etc/init.d/syslog
%define apache_vhost_dir    %{apache}/vhosts.d
%endif
%if 0%{?el5}
%define apache              httpd
%define apache_tools        httpd-tools
%define apache_group        apache
%define htpasswd_cmd        htpasswd
%define sysloginitscript    /etc/init.d/syslog
%define apache_vhost_dir    %{apache}/conf.d
%endif
%if 0%{?el6}
%define apache              httpd
%define apache_tools        httpd-tools
%define apache_group        apache
%define htpasswd_cmd        htpasswd
%define sysloginitscript    /etc/init.d/rsyslog
%define apache_vhost_dir    %{apache}/conf.d
%endif

%define apache_errlog_file %{rudderlogdir}/%{apache}/error.log
%define apache_log_file    %{rudderlogdir}/%{apache}/access.log

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - webapp
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 1299256513
License: AGPLv3
URL: http://www.rudder-project.org

Group: Applications/System

Source1: rudder-users.xml
Source2: rudder.xml
Source3: rudder-networks.conf
Source5: rudder-upgrade

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

BuildRequires: jdk >= 1.6
Requires: rudder-jetty rudder-inventory-ldap rudder-inventory-endpoint rudder-reports rudder-techniques %{apache} %{apache_tools} git-core rsync

%description
Rudder is an open source configuration management and audit solution.

This package contains the web application that is the main user interface to
Rudder. The webapp is automatically installed and started using the Jetty
application server bundled in the rudder-jetty package.


#=================================================
# Source preparation
#=================================================
%prep

sed -i 's@%APACHE_ERRLOG_FILE%@%{apache_errlog_file}@' %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/apache2-default.conf
sed -i 's@%APACHE_LOG_FILE%@%{apache_log_file}@'       %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/apache2-default.conf
cp -rf %{_sourcedir}/rudder-sources %{_builddir}

#=================================================
# Building
#=================================================
%build

export MAVEN_OPTS=-Xmx512m
cd %{_builddir}/rudder-sources/rudder-parent-pom && %{_sourcedir}/maven2/bin/mvn -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
cd %{_builddir}/rudder-sources/rudder-commons    && %{_sourcedir}/maven2/bin/mvn -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
cd %{_builddir}/rudder-sources/scala-ldap        && %{_sourcedir}/maven2/bin/mvn -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
cd %{_builddir}/rudder-sources/ldap-inventory    && %{_sourcedir}/maven2/bin/mvn -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
cd %{_builddir}/rudder-sources/cf-clerk          && %{_sourcedir}/maven2/bin/mvn -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
cd %{_builddir}/rudder-sources/rudder            && %{_sourcedir}/maven2/bin/mvn -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install package

#=================================================
# Installation
#=================================================
%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{rudderdir}/etc/
mkdir -p %{buildroot}%{rudderdir}/etc/plugins/
mkdir -p %{buildroot}%{rudderdir}/bin/
mkdir -p %{buildroot}%{rudderdir}/jetty7/webapps/
mkdir -p %{buildroot}%{rudderdir}/jetty7/contexts/
mkdir -p %{buildroot}%{rudderdir}/jetty7/rudder-plugins/
mkdir -p %{buildroot}%{rudderdir}/share/tools
mkdir -p %{buildroot}%{rudderdir}/share/plugins/
mkdir -p %{buildroot}%{rudderdir}/share/upgrade-tools/
mkdir -p %{buildroot}%{ruddervardir}/inventories/incoming
mkdir -p %{buildroot}%{ruddervardir}/inventories/accepted-nodes-updates
mkdir -p %{buildroot}%{ruddervardir}/inventories/received
mkdir -p %{buildroot}%{rudderlogdir}/%{apache}/
mkdir -p %{buildroot}/etc/%{apache_vhost_dir}/
mkdir -p %{buildroot}/etc/sysconfig/

cp %{SOURCE1} %{buildroot}%{rudderdir}/etc/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/ldap/bootstrap.ldif %{buildroot}%{rudderdir}/share/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/ldap/init-policy-server.ldif %{buildroot}%{rudderdir}/share/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/ldap/demo-data.ldif %{buildroot}%{rudderdir}/share/
cp %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/configuration.properties.sample %{buildroot}%{rudderdir}/etc/rudder-web.properties
cp %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/logback.xml %{buildroot}%{rudderdir}/etc/

cp %{_builddir}/rudder-sources/rudder/rudder-web/target/rudder-web*.war %{buildroot}%{rudderdir}/jetty7/webapps/rudder.war

cp -rf %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/load-page %{buildroot}%{rudderdir}/share/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/test/resources/script/cfe-red-button.sh %{buildroot}%{rudderdir}/bin/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/reportsInfo.xml %{buildroot}%{rudderdir}/etc/
cp %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/apache2-default.conf %{buildroot}/etc/%{apache_vhost_dir}/rudder-default.conf
cp %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/apache2-sysconfig %{buildroot}/etc/sysconfig/rudder-apache
cp %{SOURCE2} %{buildroot}%{rudderdir}/jetty7/contexts/
cp %{SOURCE3} %{buildroot}%{rudderdir}/etc/

%if 0%{?sles_version}
# On SLES, change the Apache DocumentRoot to the OS default, unless it has already been modified
sed -i "s%^DocumentRoot /var/www$%DocumentRoot /srv/www%" %{buildroot}/etc/%{apache_vhost_dir}/rudder-default.conf
%endif

# Install upgrade tools
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.3-2.4-groups-isDynamic.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.3-2.4-PT-history.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.3-2.4-PI-PT-CR-names-changed.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.3-2.4-index.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.3-2.4-add-MigrationEventLog-table.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.3-2.4-add-EventLog-reason-column.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.3-2.4-set-migration-needed-flag-for-EventLog.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.4-2.4-set-migration-needed-flag-for-EventLog.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.3-2.4-archive.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.3-2.4-index-archive.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.4-2.5-group-serialisation.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.4-2.4-eventlog-unlimited-principal-length.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.4-2.5-last-error-report-id.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.4-2.5-git-commit.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.4-2.5-add-modification-id-to-EventLog.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.5-2.6-unexpanded-value.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.5-2.6-add_workflow_support.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.6-2.6-add-modification-Id-change-request-column.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.6-2.6-index-reports.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-upgrade-LDAP-schema-2.3-2.4-add-entries.ldif %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-upgrade-modify-system-group-entries.ldif %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-upgrade-LDAP-schema-2.3-2.4-add-archives-entry.ldif %{buildroot}%{rudderdir}/share/upgrade-tools/

cp %{SOURCE5} %{buildroot}%{rudderdir}/bin/

%pre -n rudder-webapp
#=================================================
# Pre Installation
#=================================================

%post -n rudder-webapp
#=================================================
# Post Installation
#=================================================

echo "Setting Apache HTTPd as a boot service"
/sbin/chkconfig --add %{apache}
%if 0%{?rhel} >= 6
/sbin/chkconfig %{apache} on
%endif

echo "Restarting syslog"
%{sysloginitscript} restart

/sbin/service %{apache} stop
# a2dissite default

# Do this ONLY at first install
if [ $1 -eq 1 ]
then
		echo 'DAVLockDB /tmp/davlock.db' > /etc/%{apache}/conf.d/dav_mod.conf

		mkdir -p /var/rudder/configuration-repository
		mkdir -p /var/rudder/configuration-repository/shared-files
		touch /var/rudder/configuration-repository/shared-files/.placeholder
		cp -a %{rudderdir}/share/techniques /var/rudder/configuration-repository/
fi

# Add required includes in the SLES apache2 configuration
%if 0%{?sles_version}
if ! grep -qE "^. /etc/sysconfig/rudder-apache$" /etc/sysconfig/apache2
then
	echo -e '# This sources the modules/defines needed by Rudder\n. /etc/sysconfig/rudder-apache' >> /etc/sysconfig/apache2
fi
%endif

# Update /etc/sysconfig/apache2 in case an old module loading entry has already been created by Rudder
if grep -q 'APACHE_MODULES="${APACHE_MODULES} rewrite dav dav_fs proxy proxy_http' /etc/sysconfig/apache2
then
	echo "Upgrading the /etc/sysconfig/apache2 file, Rudder needed modules for Apache are now listed in /etc/sysconfig/rudder-apache"
	sed -i 's%APACHE_MODULES="${APACHE_MODULES} rewrite dav dav_fs proxy proxy_http.*%# This sources the Rudder needed by Rudder\n. /etc/sysconfig/rudder-apache%' /etc/sysconfig/apache2
fi

# Add right to apache user to access /var/rudder/inventories/incoming
chmod 751 /var/rudder/inventories
chown root:%{apache_group} %{ruddervardir}/inventories/incoming
chmod 2770 %{ruddervardir}/inventories/incoming
chown root:%{apache_group} %{ruddervardir}/inventories/accepted-nodes-updates
chmod 2770 %{ruddervardir}/inventories/accepted-nodes-updates
chmod 755 -R %{rudderdir}/share/tools
chmod 655 -R %{rudderdir}/share/load-page
%{htpasswd_cmd} -bc %{rudderdir}/etc/htpasswd-webdav-initial rudder rudder
%{htpasswd_cmd} -bc %{rudderdir}/etc/htpasswd-webdav rudder rudder

echo "(Re-)starting Apache HTTPd"
/sbin/service %{apache} restart

# Run any upgrades
# Note this must happen *before* creating the technique store, as it was moved in version 2.3.2
# and creating it manually would break the upgrade logic
%{rudderdir}/bin/rudder-upgrade

# Create and populate technique store
if [ ! -d /var/rudder/configuration-repository ]; then mkdir -p /var/rudder/configuration-repository; fi
if [ ! -d /var/rudder/configuration-repository/shared-files ]; then mkdir -p /var/rudder/configuration-repository/shared-files; fi
if [ ! -d /var/rudder/configuration-repository/techniques ]; then
	cp -a %{rudderdir}/share/techniques /var/rudder/configuration-repository/
fi

# Warn the user that Jetty needs restarting. This can't be done automatically due to a bug in Jetty's init script.
# See http://www.rudder-project.org/redmine/issues/2807
echo "********************************************************************************"
echo "rudder-webapp has been upgraded, but for the upgrade to take effect, please"
echo "restart the jetty application server as follows:"
echo "# /sbin/service jetty restart"
echo "********************************************************************************"

#=================================================
# Cleaning
#=================================================
%clean
rm -rf %{buildroot}

#=================================================
# Files
#=================================================
%files -n rudder-webapp
%defattr(-, root, root, 0755)

%{rudderdir}/etc/
%config(noreplace) %{rudderdir}/etc/rudder-web.properties
%config(noreplace) %{rudderdir}/etc/rudder-users.xml
%config(noreplace) %{rudderdir}/etc/logback.xml
%{rudderdir}/bin/
%{rudderdir}/jetty7/webapps/
%{rudderdir}/jetty7/rudder-plugins/
%{rudderdir}/jetty7/contexts/rudder.xml
%{rudderdir}/share
%{ruddervardir}/inventories/accepted-nodes-updates
%{ruddervardir}/inventories/incoming
%{ruddervardir}/inventories/received
%{rudderlogdir}/%{apache}/
/etc/%{apache_vhost_dir}/
%config(noreplace) /etc/%{apache_vhost_dir}/rudder-default.conf
%config(noreplace) %{rudderdir}/etc/rudder-networks.conf
%config(noreplace) /etc/sysconfig/rudder-apache

#=================================================
# Changelog
#=================================================
%changelog
* Thu Jul 28 2011 - Matthieu CERDA <matthieu.cerda@normation.com> 2.3-alpha4-1
- Initial package
