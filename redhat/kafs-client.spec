# % define buildid .local

Name:		kafs-client
Version:	0.1
Release:	1%{?dist}%{?buildid}
Summary:	The basic tools for kAFS and the /afs dynamic root
License:	GPLv2+
URL:		https://www.infradead.org/~dhowells/kafs/
Source0:	https://www.infradead.org/~dhowells/kafs/kafs-client-%{version}.tar.bz2

BuildRequires: krb5-devel
BuildRequires: keyutils-libs-devel
BuildRequires: openssl-devel

#
# Need this for the upcall program to do DNS lookups.  v1.5.11 can read the
# kAFS config files:
#	/etc/kafs/cellservdb.conf
#
%global confdir %{_sysconfdir}/kafs
%global datadir %{_datarootdir}/kafs
Requires: keyutils
# >= 1.5.11

BuildRequires: systemd-units
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
Requires: selinux-policy-base >= 3.7.19-5

%description
Provide basic AFS-compatible tools for kAFS and systemd scripts to mount the
dynamic root on /afs and preload the cell database.

#
# We generate a compatibility package that makes kafs look like OpenAFS, but it
# needs to be uninstalled be able to install OpenAFS or Auristor.
#
%package compat
Summary: AFS compatibility package, providing access through /afs
Requires: %{name}%{?_isa} = %{version}-%{release}

%description compat
Compatibility package providing standard AFS names for tools and locations such
as /afs and aklog.  This package must be uninstalled for kAFS to coexist with
another AFS implementation (such as OpenAFS).

%define _hardened_build 1
%global docdir %{_docdir}/kafs-client

%prep
%setup -q

%build
make all \
	ETCDIR=%{etcdir} \
	BINDIR=%{_bindir} \
	MANDIR=%{_mandir} \
	DATADIR=%{datadir} \
	CFLAGS="-Wall -Werror $RPM_OPT_FLAGS $RPM_LD_FLAGS $ARCH_OPT_FLAGS"

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_mandir}/man1
mkdir -p %{buildroot}%{confdir}
mkdir -p %{buildroot}%{datadir}

make DESTDIR=%{buildroot} install \
	ETCDIR=%{confdir} \
	DATADIR=%{datadir} \
	SBINDIR=%{_sbindir} \
	MANDIR=%{_mandir} \
	CFLAGS="-Wall $RPM_OPT_FLAGS -Werror"

%{__install} -m 644 conf/afs.mount %{buildroot}%{_unitdir}/afs.mount
%{__install} -m 644 conf/etc.conf %{buildroot}%{confdir}/cellservdb.conf

# Compat
ln -s aklog-kafs %{buildroot}/%{_bindir}/aklog

%post
%systemd_post afs.mount

%preun
%systemd_preun afs.mount

%postun
%systemd_postun_with_restart afs.mount

%files
%doc README
%license LICENCE.GPL
/afs
%{_bindir}/aklog-kafs
%{_unitdir}/*
%{_mandir}/man1/aklog-kafs.1*
%{confdir}
%{datadir}
%config(noreplace) %{confdir}/cellservdb.conf
%config(noreplace) %{confdir}/cellservdb.d

%files compat
%{_bindir}/aklog
%{_mandir}/man1/aklog.1*

%changelog
* Fri Feb 9 2018 David Howells <dhowells@redhat.com> 0.1-1
- Initial commit
