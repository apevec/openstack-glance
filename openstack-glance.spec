
Name:             openstack-glance
Version:          2011.3
Release:          6%{?dist}
Summary:          OpenStack Image Service

Group:            Applications/System
License:          ASL 2.0
URL:              http://glance.openstack.org
Source0:          http://launchpad.net/glance/diablo/%{version}/+download/glance-%{version}.tar.gz
Source1:          openstack-glance-api.init
Source2:          openstack-glance-registry.init
Source3:          openstack-glance.logrotate

#
# Patches managed here: https://github.com/markmc/glance/tree/fedora-patches
#
#   $> git format-patch -N 2011.3
#   $> for p in 00*.patch; do filterdiff -x '*/.gitignore' -x '*/.mailmap' -x '*/Authors' -x '*/.bzrignore' $p | sponge $p; done
#   $> for p in 00*.patch; do echo "Patch${p:2:2}:          $p"; done
#   $> for p in 00*.patch; do echo "%patch${p:2:2} -p1"; done
#

# These are from stable/diablo
Patch01:          0001-Point-tools-rfc.sh-at-the-correct-branch.patch
Patch02:          0002-Fixes-LP-Bug-845788.patch
Patch03:          0003-Fixes-LP-Bug-850685.patch
Patch04:          0004-Make-remote-swift-image-streaming-functional.patch
Patch05:          0005-Returning-functionality-of-s3-backend-to-stream-remo.patch
Patch06:          0006-Fixes-LP-Bug-860862-Security-creds-still-shown.patch
Patch07:          0007-Fixes-LP-Bug-872276-small-typo-in-error-message.patch
Patch08:          0008-Better-document-using-Glance-with-Keystone.patch
Patch09:          0009-Fixes-LP-Bug-844618-SQLAlchemy-errors-not-logged.patch
Patch10:          0010-Add-.gitreview-config-file-for-gerrit.patch
Patch11:          0011-Removed-mox-0.5.0-and-replaced-with-just-mox-in-tool.patch
Patch12:          0012-Remove-location-from-POST-PUT-image-responses.patch
Patch13:          0013-Fix-Keystone-API-skew-issue-with-Glance-client.patch
Patch14:          0014-load-gettext-in-__init__-to-fix-_-is-not-defined.patch
Patch15:          0015-Update-glance-show-to-print-a-valid-URI.-Fixes-bug-8.patch
Patch16:          0016-Using-Keystone-s-new-port-number-35357.patch
Patch17:          0017-Making-prefetcher-call-create_stores.patch
Patch18:          0018-Add-a-LICENSE-file.patch
Patch19:          0019-Rename-.glance-venv-to-.venv.patch
Patch20:          0020-Always-reference-the-glance-module-from-the-package-.patch
Patch21:          0021-Don-t-access-the-net-while-building-docs.patch

# EPEL specific
Patch100:         openstack-glance-newdeps.patch

BuildArch:        noarch
BuildRequires:    python2-devel
BuildRequires:    python-setuptools
BuildRequires:    python-distutils-extra
BuildRequires:    intltool

Requires(post):   chkconfig
Requires(preun):  initscripts
Requires(preun):  chkconfig
Requires(pre):    shadow-utils
Requires:         python-glance = %{version}-%{release}

%description
OpenStack Image Service (code-named Glance) provides discovery, registration,
and delivery services for virtual disk images. The Image Service API server
provides a standard REST interface for querying information about virtual disk
images stored in a variety of back-end stores, including OpenStack Object
Storage. Clients can register new virtual disk images with the Image Service,
query for information on publicly available disk images, and use the Image
Service's client library for streaming virtual disk images.

This package contains the API and registry servers.

%package -n       python-glance
Summary:          Glance Python libraries
Group:            Applications/System

Requires:         python-eventlet
Requires:         python-kombu
Requires:         python-paste-deploy
Requires:         python-routes
Requires:         python-sqlalchemy0.7
Requires:         python-webob1.0
Requires:         python-setuptools
Requires:         python-httplib2

#
# The image cache requires this http://pypi.python.org/pypi/xattr
# but Fedora's python-xattr is http://pyxattr.sourceforge.net/
#
# The cache is disabled by default, so it's only an issue if you
# enabled it
#
Requires:         python-xattr

%description -n   python-glance
OpenStack Image Service (code-named Glance) provides discovery, registration,
and delivery services for virtual disk images.

This package contains the glance Python library.

%package doc
Summary:          Documentation for OpenStack Image Service
Group:            Documentation

Requires:         %{name} = %{version}-%{release}

BuildRequires:    python-sphinx10
BuildRequires:    graphviz

# Required to build module documents
BuildRequires:    python-boto
BuildRequires:    python-daemon
BuildRequires:    python-eventlet
BuildRequires:    python-gflags
BuildRequires:    python-routes
BuildRequires:    python-sqlalchemy0.7
BuildRequires:    python-webob1.0

%description      doc
OpenStack Image Service (code-named Glance) provides discovery, registration,
and delivery services for virtual disk images.

This package contains documentation files for glance.

%prep
%setup -q -n glance-%{version}

%patch01 -p1
%patch02 -p1
%patch03 -p1
%patch04 -p1
%patch05 -p1
%patch06 -p1
%patch07 -p1
%patch08 -p1
%patch09 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
%patch15 -p1
%patch16 -p1
%patch17 -p1
%patch18 -p1
%patch19 -p1
%patch20 -p1
%patch21 -p1

%patch100 -p1 -b .newdeps

sed -i 's|\(sql_connection = sqlite:///\)\(glance.sqlite\)|\1%{_sharedstatedir}/glance/\2|' etc/glance-registry.conf

sed -i '/\/usr\/bin\/env python/d' glance/common/config.py glance/registry/db/migrate_repo/manage.py

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

# Delete tests
rm -fr %{buildroot}%{python_sitelib}/tests

export PYTHONPATH="$( pwd ):$PYTHONPATH"
pushd doc
sphinx-1.0-build -b html source build/html
sphinx-1.0-build -b man source build/man

mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 build/man/*.1 %{buildroot}%{_mandir}/man1/
popd

# Fix hidden-file-or-dir warnings
rm -fr doc/build/html/.doctrees doc/build/html/.buildinfo
rm -f %{buildroot}%{_sysconfdir}/glance*.conf
rm -f %{buildroot}%{_sysconfdir}/logging.cnf.sample
rm -f %{buildroot}/usr/share/doc/glance/README

# Setup directories
install -d -m 755 %{buildroot}%{_sharedstatedir}/glance/images

# Config file
install -p -D -m 644 etc/glance-api.conf %{buildroot}%{_sysconfdir}/glance/glance-api.conf
install -p -D -m 644 etc/glance-registry.conf %{buildroot}%{_sysconfdir}/glance/glance-registry.conf

# Initscripts
install -p -D -m 755 %{SOURCE1} %{buildroot}%{_initrddir}/openstack-glance-api
install -p -D -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/openstack-glance-registry

# Logrotate config
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-glance

# Install pid directory
install -d -m 755 %{buildroot}%{_localstatedir}/run/glance

# Install log directory
install -d -m 755 %{buildroot}%{_localstatedir}/log/glance

%pre
getent group glance >/dev/null || groupadd -r glance -g 161
getent passwd glance >/dev/null || \
useradd -u 161 -r -g glance -d %{_sharedstatedir}/glance -s /sbin/nologin \
-c "OpenStack Glance Daemons" glance
exit 0

%post
/sbin/chkconfig --add openstack-glance-api
/sbin/chkconfig --add openstack-glance-registry

%preun
if [ $1 = 0 ] ; then
    /sbin/service openstack-glance-api stop >/dev/null 2>&1
    /sbin/chkconfig --del openstack-glance-api
    /sbin/service openstack-glance-registry stop >/dev/null 2>&1
    /sbin/chkconfig --del openstack-glance-registry
fi

%files
%doc README
%{_bindir}/glance
%{_bindir}/glance-api
%{_bindir}/glance-control
%{_bindir}/glance-manage
%{_bindir}/glance-registry
%{_bindir}/glance-upload
%{_bindir}/glance-cache-prefetcher
%{_bindir}/glance-cache-pruner
%{_bindir}/glance-cache-reaper
%{_bindir}/glance-scrubber
%{_initrddir}/openstack-glance-api
%{_initrddir}/openstack-glance-registry
%{_mandir}/man1/glance-*.1.gz
%dir %{_sysconfdir}/glance
%config(noreplace) %{_sysconfdir}/glance/glance-api.conf
%config(noreplace) %{_sysconfdir}/glance/glance-registry.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-glance
%dir %attr(0755, glance, nobody) %{_sharedstatedir}/glance
%dir %attr(0755, glance, nobody) %{_localstatedir}/log/glance
%dir %attr(0755, glance, nobody) %{_localstatedir}/run/glance

%files -n python-glance
%doc README
%{python_sitelib}/glance
%{python_sitelib}/glance-%{version}-*.egg-info

%files doc
%doc doc/build/html

%changelog
* Fri Jan  6 2012 Pádraig Brady <P@draigBrady.com> - 2011.3-6
- Reapply patch to use parallel install versions of epel packages

* Fri Jan  6 2012 Mark McLoughlin <markmc@redhat.com> - 2011.3-5
- Rebase to latest upstream stable/diablo branch adding ~20 patches

* Tue Dec 20 2011 David Busby <oneiroi@fedoraproject.org> - 2011.3-4
- Depend on python-httplib2

* Tue Nov 22 2011 Pádraig Brady <P@draigBrady.com> - 2011.3-3
- Use updated parallel install versions of epel packages

* Tue Nov 22 2011 Pádraig Brady <P@draigBrady.com> - 2011.3-2
- Ensure the docs aren't built with the system glance module
- Ensure we don't access the net when building docs
- Depend on python-paste-deploy (#759512)

* Tue Sep 27 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-1
- Update to Diablo final

* Tue Sep  6 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-0.8.d4
- fix DB path in config
- add BR: intltool for distutils-extra

* Wed Aug 31 2011 Angus Salkeld <asalkeld@redhat.com> - 2011.3-0.7.d4
- Use the available man pages
- don't make service files executable
- delete unused files
- add BR: python-distutils-extra (#733610)

* Tue Aug 30 2011 Angus Salkeld <asalkeld@redhat.com> - 2011.3-0.6.d4
- Change from LSB scripts to systemd service files (#732689).

* Fri Aug 26 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-0.5.d4
- Update to diablo4 milestone
- Add logrotate config (#732691)

* Wed Aug 24 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-0.4.992bzr
- Update to latest upstream
- Use statically assigned uid:gid 161:161 (#732687)

* Mon Aug 22 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-0.3.987bzr
- Re-instate python2-devel BR (#731966)

* Mon Aug 22 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-0.2.987bzr
- Fix rpmlint warnings, reduce macro usage (#731966)

* Wed Aug 17 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-0.1.987bzr
- Update to latest upstream
- Require python-kombu for new notifiers support

* Mon Aug  8 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-0.1.967bzr
- Initial package from Alexander Sakhnov <asakhnov@mirantis.com>
  with cleanups by Mark McLoughlin
