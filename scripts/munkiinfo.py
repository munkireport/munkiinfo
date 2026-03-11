#!/usr/local/munkireport/munkireport-python3
"""
munkiinfo for munkireport
"""

import os
import plistlib
import sys
import urllib.parse
import re

# pylint: disable=E0611
from Foundation import CFPreferencesCopyAppValue
# pylint: enable=E0611

# For Swift MunkiTools compatibility, use CFPreferencesCopyAppValue directly
class Prefs:
    """Simple prefs wrapper for CFPreferencesCopyAppValue"""
    @staticmethod
    def pref(pref_name):
        """Read a preference value"""
        return CFPreferencesCopyAppValue(pref_name, 'ManagedInstalls')

prefs = Prefs()


def pref_to_str(pref_value):
    """If the value of a preference is None return an empty string type
    so we can write this data to a plist. Convert Bool values to strings
    for easy display in MunkiReport."""
    if pref_value is None:
        # convert to empty string for values that are not set
        pref_value = ''
    elif pref_value is True:
        pref_value = 'True'
    elif pref_value is False:
        pref_value = 'False'
    else:
        return pref_value
    return pref_value

def munki_prefs():
    """A full listing of all Munki preferences"""
    ''' https://github.com/munki/munki/wiki/Preferences '''
    ''' Last updated for version 6.4.2 of Munki '''
    our_prefs = [
        'AppleSoftwareUpdatesOnly',
        'AggressiveUpdateNotificationDays',
        'InstallAppleSoftwareUpdates',
        'UnattendedAppleUpdates',
        'SoftwareUpdateServerURL',
        'SoftwareRepoURL',
        'PackageURL',
        'CatalogURL',
        'ManifestURL',
        'IconURL',
        'ClientResourceURL',
        'ClientResourcesFilename',
        'HelpURL',
        'ClientIdentifier',
        'ManagedInstallDir',
        'LogFile',
        'LogToSyslog',
        'LoggingLevel',
        'DaysBetweenNotifications',
        'UseNotificationCenterDays',
        'UseClientCertificate',
        'UseClientCertificateCNAsClientIdentifier',
        'SoftwareRepoCAPath',
        'SoftwareRepoCACertificate',
        'ClientCertificatePath',
        'ClientKeyPath',
        # 'AdditionalHttpHeaders',
        'PackageVerificationMode',
        'SuppressUserNotification',
        'SuppressAutoInstall',
        'SuppressLoginwindowInstall',
        'SuppressStopButtonOnInstall',
        'InstallRequiresLogout',
        'ShowRemovalDetail',
        'MSULogEnabled',
        'MSUDebugLogEnabled',
        'LocalOnlyManifest',
        'FollowHTTPRedirects',
        'IgnoreSystemProxies',
        'IgnoreMiddleware',
        'PerformAuthRestarts',
        'RecoveryKeyFile',
        'ShowOptionalInstallsForHigherOSVersions',
        'EmulateProfileSupport',
        'OldestUpdateDays',
        'PendingUpdateCount'
    ]
    return our_prefs

def formatted_prefs():
    """Formatted dictionary object for output to plist"""
    my_dict = {}
    for pref in munki_prefs():
        pref_value = pref_to_str(prefs.pref(pref))
        my_dict.update({pref: pref_value})
    return my_dict

def get_munkiprotocol():
    """The protocol munki is using"""
    software_repo_url = pref_to_str(prefs.pref('SoftwareRepoURL'))
    try:
        url_parse = urllib.parse.urlparse(software_repo_url)
        return url_parse.scheme
    except AttributeError:
        return 'Could not obtain protocol'

def middleware_checks():
    """Check for middleware, get version if supported"""

    middleware_version = None
    middleware_name = None
    for filename in os.listdir('/usr/local/munki'):
        if filename.startswith('middleware') and os.path.splitext(filename)[1] == '.py':

            # Get the middleware version without running it, cuz that makes problems
            f = open("/usr/local/munki/"+filename, "r")
            for line in f:
                if "__version__ = " in line:
                    middleware_version = re.sub("__version__ = ",'', re.sub("'",'', line.strip()))
                    f.close()
                    break
            middleware_name = os.path.splitext(filename)[0]

            if middleware_version is None:
                print("Error: munkiinfo.py - Error getting version attribute from middleware.")

    if middleware_name and middleware_version:
        return middleware_name + '-' + middleware_version
    elif middleware_name:
        return middleware_name
    else:
        return ""

def munkiinfo_report():
    """Build our report data for our munkiinfo plist"""
    munkiprotocol = get_munkiprotocol()
    if 'file' in munkiprotocol:
        munkiprotocol = 'localrepo'

    AppleCatalogURL = str(CFPreferencesCopyAppValue('CatalogURL', 'com.apple.SoftwareUpdate'))
    if AppleCatalogURL == 'None':
        AppleCatalogURL = ''

    middleware_info = middleware_checks()

    report = {
        'AppleCatalogURL': AppleCatalogURL,
        'munkiprotocol': munkiprotocol,
        'Middleware': middleware_info
    }

    report.update(formatted_prefs())
    return [report]

def main():
    """Main"""

    result = munkiinfo_report()

    # Write munkiinfo report to cache
    cachedir = '%s/cache' % os.path.dirname(os.path.realpath(__file__))
    output_plist = os.path.join(cachedir, 'munkiinfo.plist')
    try:
        plistlib.writePlist(result, output_plist)
    except:
        with open(output_plist, 'wb') as fp:
            plistlib.dump(result, fp, fmt=plistlib.FMT_XML)

if __name__ == "__main__":
    main()
