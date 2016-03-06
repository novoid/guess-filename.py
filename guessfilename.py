#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2016-03-06 19:00:59 vk>

# TODO:
# * fix parts marked with «FIXXME»


# ===================================================================== ##
#  You might not want to modify anything below this line if you do not  ##
#  know, what you are doing :-)                                         ##
# ===================================================================== ##

import re
import sys
import os
import os.path
import time
import logging
from optparse import OptionParser

try:
    from fuzzywuzzy import fuzz  # for fuzzy comparison of strings
except ImportError:
    print "Could not find Python module \"fuzzywuzzy\".\nPlease install it, e.g., with \"sudo pip install fuzzywuzzy\"."
    sys.exit(1)


PROG_VERSION_NUMBER = u"0.1"
PROG_VERSION_DATE = u"2016-03-04"
INVOCATION_TIME = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())

USAGE = u"\n\
    " + sys.argv[0] + u" [<options>] <list of files>\n\
\n\
FIXXME\n\
\n\
\n\
Example usages:\n\
  " + sys.argv[0] + u" --tags=\"presentation projectA\" *.pptx\n\
      ... FIXXME\n\
\n\
\n\
\n\
Verbose description: FIXXME: http://Karl-Voit.at/managing-digital-photographs/\n\
\n\
:copyright: (c) by Karl Voit <tools@Karl-Voit.at>\n\
:license: GPL v3 or any later version\n\
:URL: https://github.com/novoid/guess-filename.py\n\
:bugreports: via github or <tools@Karl-Voit.at>\n\
:version: " + PROG_VERSION_NUMBER + " from " + PROG_VERSION_DATE + "\n"

parser = OptionParser(usage=USAGE)

parser.add_option("-d", "--dryrun", dest="dryrun", action="store_true",
                  help="enable dryrun mode: just simulate what would happen, do not modify files")

parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                  help="enable verbose mode")

parser.add_option("-q", "--quiet", dest="quiet", action="store_true",
                  help="enable quiet mode")

parser.add_option("--version", dest="version", action="store_true",
                  help="display version and exit")

(options, args) = parser.parse_args()


def handle_logging():
    """Log handling and configuration"""

    if options.verbose:
        FORMAT = "%(levelname)-8s %(asctime)-15s %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    elif options.quiet:
        FORMAT = "%(levelname)-8s %(message)s"
        logging.basicConfig(level=logging.ERROR, format=FORMAT)
    else:
        FORMAT = "%(levelname)-8s %(message)s"
        logging.basicConfig(level=logging.INFO, format=FORMAT)


def error_exit(errorcode, text):
    """exits with return value of errorcode and prints to stderr"""

    sys.stdout.flush()
    logging.error(text)

    sys.exit(errorcode)


class GuessFilename(object):
    """
    Contains methods of the guess filename domain
    """

    FILENAME_TAG_SEPARATOR = u' -- '
    BETWEEN_TAG_SEPARATOR = u' '

    # file names containing tags matches following regular expression
    # ( (date(time)?)?(--date(time)?)? )? filename (tags)? (extension)?
    DAY_REGEX = "[12]\d{3}-?[01]\d-?[0123]\d"  # note: I made the dashes between optional to match simpler format as well
    TIME_REGEX = "T[012]\d.[012345]\d(.[012345]\d)?"
    DAYTIME_REGEX = "(" + DAY_REGEX + "(" + TIME_REGEX + ")?)"
    DAYTIME_DURATION_REGEX = DAYTIME_REGEX + "(--?" + DAYTIME_REGEX + ")?"

    ISO_NAME_TAGS_EXTENSION_REGEX = re.compile("((" + DAYTIME_DURATION_REGEX + ")[ -_])?(.+?)(" + FILENAME_TAG_SEPARATOR + "((\w+[" + BETWEEN_TAG_SEPARATOR + "]?)+))?(\.(\w+))?$")
    DAYTIME_DURATION_INDEX = 2
    NAME_INDEX = 10
    TAGS_INDEX = 12
    EXTENSION_INDEX = 15

    EURO_CHARGE_REGEX = re.compile(u"^(.+[-_ ])?(\d+([,.]\d+)?)[-_ ]?(EUR|€)([-_ .].+)?$")
    EURO_CHARGE_INDEX = 2

    logger = None
    config = None

    def __init__(self, config, logger):
        self.logger = logger

    def adding_tags(self, tagarray, newtags):
        """
        Returns unique array of tags containing the newtag.

        @param tagarray: a array of unicode strings containing tags
        @param newtag: a array of unicode strings containing tags
        @param return: a array of unicode strings containing tags
        """

        assert tagarray.__class__ == list
        assert newtags.__class__ == list

        resulting_tags = tagarray

        for tag in newtags:
            if tag not in tagarray:
                resulting_tags.append(tag)

        return resulting_tags

    def split_filename_entities(self, filename):
        """
        Takes a filename of format ( (date(time)?)?(--date(time)?)? )? filename (tags)? (extension)?
        and returns a set of (date/time/duration, filename, array of tags, extension).
        """

        # FIXXME: return directory as well!

        assert(type(filename) == unicode or type(filename) == str)
        assert(len(filename) > 0)

        components = re.match(self.ISO_NAME_TAGS_EXTENSION_REGEX, filename)

        assert(components)

        if components.group(self.TAGS_INDEX):
            tags = components.group(self.TAGS_INDEX).split(' ')
        else:
            tags = []
        return components.group(self.DAYTIME_DURATION_INDEX), \
            components.group(self.NAME_INDEX), \
            tags, \
            components.group(self.EXTENSION_INDEX)

    def contains_one_of(self, string, entries):
        """
        Returns true, if the string contains one of the strings within entries array
        """

        assert(type(string) == unicode or type(string) == str)
        assert(type(entries) == list)
        assert(len(string) > 0)
        assert(len(entries) > 0)

        for entry in entries:
            if entry in string:
                return True

        return False

    def fuzzy_contains_one_of(self, string, entries):
        """
        Returns true, if the string contains a similar one of the strings within entries array
        """

        assert(type(string) == unicode or type(string) == str)
        assert(type(entries) == list)
        assert(len(string) > 0)
        assert(len(entries) > 0)

        for entry in entries:
            similarity = fuzz.partial_ratio(string, entry)
            if similarity > 64:
                #logging.debug(u"MATCH   fuzzy_contains_one_of(%s, %s) == %i" % (string, str(entry), similarity))
                return True
            else:
                #logging.debug(u"¬ MATCH fuzzy_contains_one_of(%s, %s) == %i" % (string, str(entry), similarity))
                pass

        return False

    def has_euro_charge(self, string):
        """
        Returns true, if the string contains a number with a €-currency
        """

        assert(type(string) == unicode or type(string) == str)
        assert(len(string) > 0)

        components = re.match(self.EURO_CHARGE_REGEX, string)

        if components:
            return True
        else:
            return False

    def get_euro_charge(self, string):
        """
        Returns the included €-currency or False
        """

        assert(type(string) == unicode or type(string) == str)
        assert(len(string) > 0)

        components = re.match(self.EURO_CHARGE_REGEX, string)

        if components:
            return components.group(self.EURO_CHARGE_INDEX)
        else:
            return False

    def rename_file(self, dirname, oldbasename, newbasename, dryrun=False, quiet=False):
        """
        Renames a file from oldbasename to newbasename in dirname.

        Only simulates result if dryrun is True.

        @param dirname: string containing the directory of the file
        @param oldbasename: string containing the old file name (oldbasename)
        @param newbasename: string containing the new file name (oldbasename)
        @param dryrun: boolean which defines if files should be changed (False) or not (True)
        """

        if oldbasename == newbasename:
            logging.debug("old filename is same as new filename [%s]. Doing nothing." % oldbasename)
            return False

        oldfile = os.path.join(dirname, oldbasename)
        newfile = os.path.join(dirname, newbasename)

        if not os.path.isfile(oldfile):
            logging.error("file to rename does not exist: [%s]" % oldfile)
            return False

        if os.path.isfile(newfile):
            logging.error("file can't be renamed since new file name already exists: [%s]" % newfile)
            return False

        if not quiet:
            print u"   %s  →  %s" % (oldbasename, newbasename)
        logging.debug(u" renaming \"%s\"" % oldfile)
        logging.debug(u"      ⤷   \"%s\"" % newfile)
        if not dryrun:
            os.rename(oldfile, newfile)
        return True

    def derive_new_filename_from_old_filename(s, oldfilename):
        """
        Analyses the old filename and returns a new one if feasible.
        If not, False is returned instead.

        @param oldfilename: string containing one file name
        @param return: False or new oldfilename
        """

        logging.debug("derive_new_filename_from_old_filename called")
        datetimestr, basefilename, tags, extension = s.split_filename_entities(oldfilename)

        # 2015-11-24 Rechnung A1 Festnetz-Internet 12,34€ -- scan finance.pdf
        if s.contains_one_of(oldfilename, [" A1 ", " a1 "]) and s.has_euro_charge(oldfilename) and datetimestr:
            return datetimestr + \
                u" A1 Festnetz-Internet " + s.get_euro_charge(oldfilename) + \
                u"€ -- " + ' '.join(s.adding_tags(tags, ['scan', 'finance', 'bill'])) + \
                u".pdf"

        # 2016-01-19--2016-02-12 benutzter GVB 10er Block -- scan transportation graz.pdf
        if s.contains_one_of(oldfilename, ["10er"]) and datetimestr:
            return datetimestr + \
                u" benutzter GVB 10er Block" + \
                u" -- " + ' '.join(s.adding_tags(tags, ['scan', 'transportation', 'graz'])) + \
                u".pdf"

        # FIXXME: more cases!

        return False  # no new filename found

    def handle_file(self, oldfilename, dryrun):
        """
        @param oldfilename: string containing one file name
        @param dryrun: boolean which defines if files should be changed (False) or not (True)
        @param return: error value or new oldfilename
        """

        assert oldfilename.__class__ == str or \
            oldfilename.__class__ == unicode
        if dryrun:
            assert dryrun.__class__ == bool

        if os.path.isdir(oldfilename):
            logging.warning("Skipping directory \"%s\" because this tool only renames file names." % oldfilename)
            return
        elif not os.path.isfile(oldfilename):
            logging.debug("file type error in folder [%s]: file type: is file? %s  -  is dir? %s  -  is mount? %s" %
                          (os.getcwdu(), str(os.path.isfile(oldfilename)), str(os.path.isdir(oldfilename)), str(os.path.islink(oldfilename))))
            logging.error("Skipping \"%s\" because this tool only renames existing file names." % oldfilename)
            return

        dirname = os.path.abspath(os.path.dirname(oldfilename))
        logging.debug(u"————→ dirname  [%s]" % dirname)
        basename = os.path.basename(oldfilename)
        logging.debug(u"————→ basename [%s]" % basename)

        newfilename = self.derive_new_filename_from_old_filename(basename)

        if newfilename:
            logging.debug("derive_new_filename_from_old_filename returned new filename: %s" % newfilename)
            self.rename_file(dirname, basename, newfilename, dryrun)
            return newfilename

        # FIXXME: try to derive new filename from content


def main():
    """Main function"""

    if options.version:
        print os.path.basename(sys.argv[0]) + " version " + PROG_VERSION_NUMBER + \
            " from " + PROG_VERSION_DATE
        sys.exit(0)

    handle_logging()

    if options.verbose and options.quiet:
        error_exit(1, "Options \"--verbose\" and \"--quiet\" found. " +
                   "This does not make any sense, you silly fool :-)")

    if options.dryrun:
        logging.debug("DRYRUN active, not changing any files")
    logging.debug("extracting list of files ...")

    files = args

    logging.debug("%s filenames found: [%s]" % (str(len(files)), '], ['.join(files)))

    CONFIGDIR = os.path.join(os.path.expanduser("~"), ".config/guessfilename")
    sys.path.insert(0, CONFIGDIR)  # add CONFIGDIR to Python path in order to find config file
    try:
        import guessfilenameconfig
    except ImportError:
        print "Could not find \"guessfilenameconfig.py\" in directory \"" + CONFIGDIR + "\".\nPlease take a look at \"guessfilenameconfig-TEMPLATE.py\", copy it, and configure accordingly."
        sys.exit(1)

    guess_filename = GuessFilename(guessfilenameconfig, logging.getLogger())

    if len(args) < 1:
        error_exit(5, "Please add at least one file name as argument")

    logging.debug("iterating over files ...\n" + "=" * 80)
    for filename in files:
        if filename.__class__ == str:
            filename = unicode(filename, "UTF-8")
        guess_filename.handle_file(filename, options.dryrun)

    logging.debug("successfully finished.")

    if not options.quiet:
        # add empty line for better screen output readability
        print


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:

        logging.info("Received KeyboardInterrupt")

# END OF FILE #################################################################
