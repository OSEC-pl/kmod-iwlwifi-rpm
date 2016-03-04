# Define the kmod package name here.
%define kmod_name iwlwifi
%define osec_github git@github.com:OSEC-pl
%define today %(date '+%%y%%m%%d')

# If kversion isn't defined on the rpmbuild line, define it here.
%{!?kversion: %define kversion 3.10.0-327.10.1.el7.%{_target_cpu}}

Name:    %{kmod_name}-kmod
Version: 0.0
Release: 1.%{today}%{?dist}
Group:   System Environment/Kernel
License: GPLv2
Summary: %{kmod_name} kernel module(s)
URL:     http://www.kernel.org/

BuildRequires: perl
BuildRequires: redhat-rpm-config
BuildRequires: git
ExclusiveArch: x86_64

# Sources.
#Source0:  %{kmod_name}-%{version}.tar.bz2
Source0: kmodtool-%{kmod_name}-el7.sh

# Magic hidden here.
%{expand:%(sh %{SOURCE0} rpmtemplate %{kmod_name} %{kversion} "")}

# Disable the building of the debug package(s).
%define debug_package %{nil}

%description
This package provides the %{kmod_name} kernel module(s).
It is built to depend upon the specific ABI provided by a range of releases
of the same variant of the Linux kernel and not on any one specific build.

%prep
echo %_builddir
#%setup -q -n %{kmod_name}-%{version}
cd %_builddir
rm -rf %{kmod_name}-%{version}
git clone %{osec_github}/kmod-%{kmod_name}.git %{kmod_name}-%{version}
cd %{kmod_name}-%{version}
echo "override iwlwifi * weak-updates/%{kmod_name}" > kmod-%{kmod_name}.conf
echo "override iwlmvm * weak-updates/%{kmod_name}" >> kmod-%{kmod_name}.conf
echo "override iwldvm * weak-updates/%{kmod_name}" >> kmod-%{kmod_name}.conf
%build
KSRC=%{_usrsrc}/kernels/%{kversion}
%{__make} -C "${KSRC}" %{?_smp_mflags} modules M=$PWD/%{kmod_name}-%{version}

%install
cd %{kmod_name}-%{version}
%{__install} -d %{buildroot}/lib/modules/%{kversion}/extra/%{kmod_name}/
%{__install} iwlwifi.ko %{buildroot}/lib/modules/%{kversion}/extra/%{kmod_name}/
%{__install} mvm/iwlmvm.ko %{buildroot}/lib/modules/%{kversion}/extra/%{kmod_name}/
%{__install} dvm/iwldvm.ko %{buildroot}/lib/modules/%{kversion}/extra/%{kmod_name}/
%{__install} -d %{buildroot}%{_sysconfdir}/depmod.d/
%{__install} kmod-%{kmod_name}.conf %{buildroot}%{_sysconfdir}/depmod.d/
%{__install} -d %{buildroot}%{_defaultdocdir}/kmod-%{kmod_name}-%{version}/

# strip the modules(s)
find %{buildroot} -type f -name \*.ko -exec %{__strip} --strip-debug \{\} \;

# Sign the modules(s)
%if %{?_with_modsign:1}%{!?_with_modsign:0}
# If the module signing keys are not defined, define them here.
%{!?privkey: %define privkey %{_sysconfdir}/pki/SECURE-BOOT-KEY.priv}
%{!?pubkey: %define pubkey %{_sysconfdir}/pki/SECURE-BOOT-KEY.der}
for module in $(find %{buildroot} -type f -name \*.ko);
do %{__perl} /usr/src/kernels/%{kversion}/scripts/sign-file \
sha256 %{privkey} %{pubkey} $module;
done
%endif

%clean
%{__rm} -rf %{buildroot}

%changelog
* Fri Mar 4 2016 Radoslaw Kujawa <radoslaw.kujawa@gmail.com> - 0.0-1
- Initial el7 build of the kmod package.
- Ripped from RHEL 7 kernel-3.10.0-327.10.1.
- Hacked in support for 8260 board as found in Lenovo E460.

