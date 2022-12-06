%global project QtAV
%global repo %{project}

# QTAV's builds fail with FFMpeg-5*
# https://bugzilla.rpmfusion.org/show_bug.cgi?id=6271
%bcond_with oldffmpeg

Name:           qtav
Version:        1.13.0
Release:        1
Summary:        A media playback framework based on Qt and FFmpeg
License:        LGPLv2+ and GPLv3+ and BSD
URL:            http://www.qtav.org/
Source0:        https://github.com/wang-bin/QtAV/archive/v%{version}/%{project}-%{version}.tar.gz
Patch0:         fix_qt514_build.patch

# Fix builds with Qt-5.15.1
Patch1:         %{name}-fix_Qt515_builds.patch

# Exclude avresample library (bug #5350)
Patch2:         %{name}-avoid-avresample_dependency.patch

# Fix avutil test during configuration
# https://bugzilla.rpmfusion.org/show_bug.cgi?id=6271
Patch3:         %{name}-fix-avutil_test.patch

BuildRequires:  desktop-file-utils
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtdeclarative-devel
BuildRequires:  qt5-qtquickcontrols
BuildRequires:  qt5-qtsvg-devel
BuildRequires:  libass-devel
%if %{with oldffmpeg}
BuildRequires:  compat-ffmpeg4-devel
%else
BuildRequires:  ffmpeg-devel
%endif
BuildRequires:  openal-soft-devel
BuildRequires:  libXv-devel
BuildRequires:  libva-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  dos2unix
Requires:       hicolor-icon-theme

%description
QtAV is a multimedia playback library based on Qt and FFmpeg.
It can help you to write a player with less effort than ever before.

Features include:
  * Hardware decoding suppprt: DXVA2, VAAPI, VDA, CedarX, CUDA.
  * OpenGL and ES2 support for Hi10P and other 16-bit YUV videos.
  * Video capture in rgb and yuv format.
  * OSD and custom filters.
  * filters in libavfilter, for example stero3d, blur.
  * Subtitle.
  * Transform video using GraphicsItemRenderer. (rotate, shear, etc)
  * Playing frame by frame (currently support forward playing).
  * Playback speed control. At any speed.
  * Variant streams: locale file, http, rtsp, etc.
  * Choose audio channel.
  * Choose media stream, e.g. play a desired audio track.
  * Multiple render engine support. Currently supports QPainter, GDI+, Direct2D,
    XV and OpenGL(and ES2).
  * Dynamically change render engine when playing.
  * Multiple video outputs for 1 player.
  * Region of interest(ROI), i.e. video cropping.
  * Video eq: brightness, contrast, saturation, hue.
  * QML support as a plugin. Most playback APIs are compatible with QtMultiMedia
    module.

%package -n lib%{name}
Summary: QtAV library
Requires: ffmpeg

%description -n lib%{name}
QtAV is a multimedia playback library based on Qt and FFmpeg.
It can help you to write a player with less effort than ever before.

This package contains the QtAV library.

%package -n lib%{name}widgets
Summary: QtAV Widgets module
Requires: libqtav%{?_isa} = %{version}-%{release}

%description -n lib%{name}widgets
QtAV is a multimedia playback library based on Qt and FFmpeg.
It can help you to write a player with less effort than ever before.

This package contains a set of widgets to play media.

%package devel
Summary: QtAV development files
Requires: libqtav%{?_isa} = %{version}-%{release}
Requires: libqtavwidgets%{?_isa} = %{version}-%{release}
Requires: qt5-qtbase-devel%{?_isa}

%description devel
QtAV is a multimedia playback library based on Qt and FFmpeg.
It can help you to write a player with less effort than ever before.

This package contains the header development files for building some
QtAV applications using QtAV headers.

%package qml-module
Summary: QtAV QML module

%description qml-module
QtAV is a multimedia playback library based on Qt and FFmpeg.
It can help you to write a player with less effort than ever before.

This package contains the QtAV QML module for Qt declarative.

%package players
Summary: QtAV/QML players
License: GPLv3
Requires: libqtav%{?_isa} = %{version}-%{release}
Requires: libqtavwidgets%{?_isa} = %{version}-%{release}
Requires: qtav-qml-module%{?_isa} = %{version}-%{release}

%description players
QtAV is a multimedia playback framework based on Qt and FFmpeg.
High performance. User & developer friendly.

This package contains the QtAV based players.

%prep
%autosetup -n %repo-%{version} -N

%patch0 -p1 -b .backup
%patch1 -p1 -b .backup
%patch2 -p1 -b .backup
%if %{with oldffmpeg}
%patch3 -p1 -b .backup
%endif

# E: script-without-shebang /usr/share/icons/hicolor/scalable/apps/QtAV.svg
# ignore them src/QtAV.svg: SVG Scalable Vector Graphics image

# delete .jar File from examples
rm -rf examples/QMLPlayer/android/gradle/wrapper/gradle-wrapper.jar

# W: doc-file-dependency /usr/share/doc/qtav-devel/examples/QMLPlayer/android/gradlew /usr/bin/env
# An included file marked as %%doc creates a possible additional dependency in
# the package.  Usually, this is not wanted and may be caused by eg. example
# scripts with executable bits set included in the package's documentation.
chmod -x examples/QMLPlayer/android/gradlew

# prepare example dir for -devel
mkdir -p _tmpdoc/examples
cp -pr examples/* _tmpdoc/examples

%build
mkdir -p build; pushd build
%if %{with oldffmpeg}
export CPATH=" -I%{_includedir}/compat-ffmpeg4"
%{_qt5_qmake} \
   QMAKE_CFLAGS="${RPM_OPT_FLAGS} -I%{_includedir}/compat-ffmpeg4" \
   QMAKE_CXXFLAGS="${RPM_OPT_FLAGS} -I%{_includedir}/compat-ffmpeg4" \
   QMAKE_LFLAGS="${RPM_LD_FLAGS} -L%{_libdir}/compat-ffmpeg4 -lavformat -lavcodec -lavutil -lavdevice -lavfilter -lswscale -lswresample" \
   QMAKE_STRIP="" \
   CONFIG+="no_rpath recheck config_libass_link release" ..
%else
export CPATH="`pkg-config --variable=includedir libswresample`"
%{_qt5_qmake} \
   QMAKE_CFLAGS="${RPM_OPT_FLAGS}" \
   QMAKE_CXXFLAGS="${RPM_OPT_FLAGS}" \
   QMAKE_LFLAGS="${RPM_LD_FLAGS}" \
   QMAKE_STRIP="" \
   CONFIG+="no_rpath recheck config_libass_link release" ..
%endif
%make_build

%install
%make_install INSTALL_ROOT=%{buildroot} -C build

rm -rf %{buildroot}%{_datadir}/doc/*
rm -rf %{buildroot}%{_qt5_archdatadir}/bin/libcommon.*
rm -rf %{buildroot}%{_qt5_headerdir}/*.h
install -d %{buildroot}%{_bindir}
ln -sfv %{_qt5_bindir}/Player %{buildroot}%{_bindir}
ln -sfv %{_qt5_bindir}/QMLPlayer %{buildroot}%{_bindir}
install -D src/QtAV.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/QtAV.svg

# library links
ln -sfv %{_libdir}/libQtAV.so %{buildroot}%{_libdir}/libQt5AV.so
ln -sfv %{_libdir}/libQtAVWidgets.so %{buildroot}%{_libdir}/libQt5AVWidgets.so

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop

%files -n lib%{name}
%doc README.md Changelog
%license lgpl-2.1.txt
%{_libdir}/libQtAV.so.*

%files -n lib%{name}widgets
%{_libdir}/libQtAVWidgets.so.*

%files devel
%{_qt5_headerdir}/QtAV/*
%{_qt5_headerdir}/QtAVWidgets/*
%dir %{_qt5_headerdir}/QtAV/
%dir %{_qt5_headerdir}/QtAVWidgets/
%{_libdir}/libQtAV.so
%{_libdir}/libQtAV.prl
%{_libdir}/libQt5AV.so
%{_libdir}/libQtAVWidgets.so
%{_libdir}/libQtAVWidgets.prl
%{_libdir}/libQt5AVWidgets.so
%{_qt5_archdatadir}/mkspecs/features/av.prf
%{_qt5_archdatadir}/mkspecs/features/avwidgets.prf
%{_qt5_archdatadir}/mkspecs/modules/qt_lib_av.pri
%{_qt5_archdatadir}/mkspecs/modules/qt_lib_avwidgets.pri
%{_qt5_archdatadir}/mkspecs/modules/qt_lib_av_private.pri
%{_qt5_archdatadir}/mkspecs/modules/qt_lib_avwidgets_private.pri

%files qml-module
%doc README.md Changelog
%license lgpl-2.1.txt
%{_qt5_archdatadir}/qml/QtAV/libQmlAV.so
%{_qt5_archdatadir}/qml/QtAV/plugins.qmltypes
%{_qt5_archdatadir}/qml/QtAV/qmldir
%{_qt5_archdatadir}/qml/QtAV/Video.qml
%dir %{_qt5_archdatadir}/qml/QtAV/

%files players
%doc README.md Changelog
%license gpl-3.0.txt
%{_qt5_bindir}/Player
%{_qt5_bindir}/QMLPlayer
%{_bindir}/Player
%{_bindir}/QMLPlayer
%{_datadir}/applications/Player.desktop
%{_datadir}/applications/QMLPlayer.desktop
%{_datadir}/icons/hicolor/*/apps/QtAV.svg

%changelog
* Tue Dec 6 2022 peijiankang <peijiankang@kylinos.cn> - 1.13.0-1
- Init package for openEuler
