# ANS INJECT


<img src="https://github.com/xlith/ansinject/raw/main/hero-image.png" width=200>

Image by <a href="https://pixabay.com/users/madartzgraphics-3575871/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=1915626">Darwin Laganzon</a> from <a href="https://pixabay.com//?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=1915626">Pixabay</a>


## Android Network Security Config Injector

<img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/ansinject"> <img alt="PyPI - Implementation" src="https://img.shields.io/pypi/implementation/ansinject"> <img alt="GitHub top language" src="https://img.shields.io/github/languages/top/xlith/ansinject"> <img alt="PyPI - License" src="https://img.shields.io/pypi/l/ansinject"> <img alt="PyPI" src="https://img.shields.io/pypi/v/ansinject"> <img alt="PyPI - Format" src="https://img.shields.io/pypi/format/ansinject"> <img alt="PyPI - Status" src="https://img.shields.io/pypi/status/ansinject">


This tool is simply an easier way to use some collection of other tools which can inject a network security config into an Android APK. Mainly it's sole pupose is making it easier to use the tools in the requirements list below with one line of command.

This is useful when you want to test an app that uses HTTPS but you don't have a valid certificate. This tool will allow you to bypass the certificate check.

## Disclaimer

**This tool is provided as is. I am not responsible for any damage caused by this tool. Use it at your own risk.**

## Requirements

- [adb](https://developer.android.com/studio/command-line/adb) (Part of the Android SDK)
- [zipalign](https://developer.android.com/studio/command-line/zipalign) (Part of the Android SDK)
- [jarsigner](https://docs.oracle.com/javase/7/docs/technotes/tools/windows/jarsigner.html) (Part of the JDK)
- [keytool](https://docs.oracle.com/javase/8/docs/technotes/tools/unix/keytool.html) (Part of the JDK)
- [apktool](https://ibotpeaches.github.io/Apktool/) (Need to be installed manually)

## Installation

```bash
pip install ansinject
```

## Usage

```bash
ansinject --help
```

```bash
ansinject inject [input_apk] [output_apk] --temp-dir [temp_dir]
```

Basicly the script will do the following:

1. Extract the APK
2. Copy the following network security config onto `/res/xml/network_security_config.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </base-config>
</network-security-config>
```

3. Rebuild the APK
4. Generate a keystore in order to sign the APK
5. Sign the APK
6. Align the output


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgements

* [stackoverflow - Capturing mobile phone traffic on wireshark](https://stackoverflow.com/questions/9555403/capturing-mobile-phone-traffic-on-wireshark)
* [gist - unoexperto - How to patch Android app to sniff its HTTPS traffic with self-signed certificate](https://gist.github.com/unoexperto/80694ccaed6dadc304ad5b8196cbbd2c#how-to-patch-android-app-to-sniff-its-https-traffic-with-self-signed-certificate)
* [exandroid - Capture all android network traffic](https://www.exandroid.dev/2021/03/21/capture-all-android-network-traffic/)
