Summary:	Jabber server with POSIX threads
Summary(pl.UTF-8):	Serwer Jabbera używający wątków POSIX-owych
Name:		wpjabber
Version:	1.1.5
Release:	0.1
License:	GPL
Group:		Applications/Communications
#Source0:	http://www.jabberstudio.org/projects/%{name}/releases/file/%{name}-%{version}.tar.gz
Source0:	%{name}-%{version}-20050514.tar.bz2
# Source0-md5:	f018020e84fc4bf7cc8e07b1a42a39c6
#Source1:	%{name}.init
#Patch0:		%{name}-perlscript.patch
URL:		http://wpjabber.jabberstudio.org/
BuildRequires:	openssl-devel >= 0.9.6d
BuildRequires:	perl-base
BuildRequires:	rpm-perlprov >= 3.0.3-16
BuildRequires:	rpmbuild(macros) >= 1.202
BuildRequires:	%post-edits-too-many-files?
Requires(post):	textutils
Requires(post):	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	rc-scripts
Provides:	group(jabber)
Provides:	user(jabber)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
WPJabber is powerful instant messaging server based on XMPP/Jabber
protocol. WPJabber was developed to handle large amount of concurrent
users.

%description -l pl.UTF-8
WPJabber to potężny serwer komunikacji oparty na protokole
XMPP/Jabber. WPJabber został stworzony z myślą o obsłudze dużej liczby
jednoczesnych użytkowników.

%prep
%setup -q

%build
export CC="%{__cc}"
export CFLAGS="%{rpmcflags} "
./configure

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_libdir}/%{name},/var/lib/%{name}/db,/var/run/jabber,/etc/{sysconfig,rc.d/init.d,%{name}}}

install jabberd/jabberd $RPM_BUILD_ROOT%{_sbindir}/wpjabberd
install */*.so $RPM_BUILD_ROOT%{_libdir}/%{name}
install jabber.xml.example $RPM_BUILD_ROOT/etc/%{name}/jabber.xml
install wpj_epoll/wpj.xml.example $RPM_BUILD_ROOT/etc/%{name}/wpj.xml
install wpj_epoll/wpj $RPM_BUILD_ROOT%{_sbindir}

%{__perl} -p -i -e 's#\./lib#%{_libdir}/wpjabber#' $RPM_BUILD_ROOT/etc/%{name}/jabber.xml
%{__perl} -p -i -e 's#log/#/var/log/wpjabber/#'  $RPM_BUILD_ROOT/etc/%{name}/jabber.xml

#install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
#install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 74 jabber
%useradd -g jabber -d /var/lib/jabber -u 74 -s /bin/false jabber

%post
if [ -f /etc/jabber/secret ] ; then
	SECRET=`cat /etc/jabber/secret`
	if [ -n "$SECRET" ] ; then
		echo "Updating component authentication secret in Jabberd config files..."
# XXX XXX FIXME Too greedy? should edit only files from this package
		%{__sed} -i -e "s/>secret</>$SECRET</" /etc/jabber/*.xml
	fi
fi

/sbin/chkconfig --add jabberd
if [ -r /var/lock/subsys/jabberd ]; then
	/etc/rc.d/init.d/jabberd restart >&2
else
	echo "Run \"/etc/rc.d/init.d/jabberd start\" to start Jabber server."
fi

%preun
if [ "$1" = "0" ]; then
	if [ -r /var/lock/subsys/jabberd ]; then
		/etc/rc.d/init.d/jabberd stop >&2
	fi
	/sbin/chkconfig --del jabberd
fi

%postun
if [ "$1" = "0" ]; then
	%userremove jabber
	%groupremove jabber
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog README TODO doc/FAQ*
#%attr(640,root,jabber) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/jabber/*.cfg
%dir %{_sysconfdir}/%{name}
%attr(640,root,jabber) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/*.xml
#%dir %{_sysconfdir}/jabber/templates
#%attr(640,root,jabber) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/jabber/templates/*.xml
%attr(755,root,root) %{_sbindir}/*
%dir %{_libdir}/%{name}
%attr(755,root,root) %{_libdir}/%{name}/*
#%dir %attr(770,root,jabber) /var/lib/%{name}
#%dir %attr(770,root,jabber) /var/lib/%{name}/db
#%attr(754,root,root) /etc/rc.d/init.d/%{name}
#%attr(640,root,root) %config(noreplace) %verify(not md5 size mtime) /etc/sysconfig/%{name}
#%{_mandir}/man*/*
