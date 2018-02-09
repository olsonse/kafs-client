# % define buildid .local

Name:		kafs-client
Version:	0.1
Release:	1%{?dist}%{?buildid}
Summary:	kAFS basic tools and /afs dynamic root
License:	GPLv2+
URL:		https://www.infradead.org/~dhowells/kafs/
Source0:	https://www.infradead.org/~dhowells/kafs/kafs-client-%{version}.tar.bz2

BuildRequires: krb5-devel
BuildRequires: keyutils-libs-devel
BuildRequires: openssl-devel
Requires: krb5-libs
Requires: keyutils-libs
Requires: openssl-libs

BuildRequires: systemd-units
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
Requires: selinux-policy-base >= 3.7.19-5

%define _hardened_build 1

%description
Provide basic AFS-compatible tools for kAFS and mount the dynamic root
on /afs.

%global docdir %{_docdir}/kafs-client

%prep
%setup -q

%build
make all \
	ETCDIR=%{_sysconfdir} \
	BINDIR=%{_bindir} \
	MANDIR=%{_mandir} \
	CFLAGS="-Wall -Werror $RPM_OPT_FLAGS $RPM_LD_FLAGS $ARCH_OPT_FLAGS"

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_mandir}/man1

make DESTDIR=%{buildroot} install \
	ETCDIR=%{_sysconfdir} \
	SBINDIR=%{_bindir} \
	MANDIR=%{_mandir} \
	CFLAGS="-Wall $RPM_OPT_FLAGS -Werror"

install -m 644 afs.mount %{buildroot}%{_unitdir}/afs.mount

%post
%systemd_post afs.mount

%preun
%systemd_preun afs.mount

%postun
%systemd_postun_with_restart afs.mount

%files
%doc README
%{_bindir}/*
%{_unitdir}/*
%{_mandir}/*/*

%changelog
* Fri Feb 9 2018 David Howells <dhowells@redhat.com> 0.1-1
- Initial commit
