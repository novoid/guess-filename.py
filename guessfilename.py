#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2016-03-05 14:51:51 vk>

## TODO:
## * fix parts marked with «FIXXME»


## ===================================================================== ##
##  You might not want to modify anything below this line if you do not  ##
##  know, what you are doing :-)                                         ##
## ===================================================================== ##

import re
import sys
import os
import os.path
import time
import logging
from optparse import OptionParser

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

    ## file names containing tags matches following regular expression
    ## ( (date(time)?)?(--date(time)?)? )? filename (tags)? (extension)?
    DAY_REGEX = "[12]\d{3}-?[01]\d-?[0123]\d"  ## note: I made the dashes between optional to match simpler format as well
    TIME_REGEX = "T[012]\d.[012345]\d(.[012345]\d)?"
    DAYTIME_REGEX = "(" + DAY_REGEX + "(" + TIME_REGEX + ")?)"
    DAYTIME_DURATION_REGEX = DAYTIME_REGEX + "(--?" + DAYTIME_REGEX + ")?"

    ISO_NAME_TAGS_EXTENSION_REGEX = re.compile("((" + DAYTIME_DURATION_REGEX + ")[ -_])?(.+?)(" + FILENAME_TAG_SEPARATOR + "((\w+[" + BETWEEN_TAG_SEPARATOR + "]?)+))?(\.(\w+))?$")
    DAYTIME_DURATION_INDEX = 2
    NAME_INDEX = 10
    TAGS_INDEX = 12
    EXTENSION_INDEX = 15

    EURO_CHARGE_REGEX = re.compile(u"^(.+[-_ ])?(\d+([,.]\d+)?)[-_ ]?(EUR|€)([-_ ].+)?$")
    EURO_CHARGE_INDEX = 2

    def adding_tag_to_filename(self, filename, tagname):
        """
        Returns string of file name with tagname as additional tag.

        @param filename: an unicode string containing a file name
        @param tagname: an unicode string containing a tag name
        @param return: an unicode string of filename containing tagname
        """

        assert filename.__class__ == str or \
            filename.__class__ == unicode
        assert tagname.__class__ == str or \
            tagname.__class__ == unicode

        if contains_tag(filename) is False:
            logging.debug(u"adding_tag_to_filename(%s, %s): no tag found so far" % (filename, tagname))

            components = re.match(FILE_WITH_EXTENSION_REGEX, os.path.basename(filename))
            if components:
                old_filename = components.group(1)
                extension = components.group(2)
                return os.path.join(os.path.dirname(filename), old_filename + FILENAME_TAG_SEPARATOR + tagname + u'.' + extension)
            else:
                return os.path.join(os.path.dirname(filename), os.path.basename(filename) + FILENAME_TAG_SEPARATOR + tagname)

        elif contains_tag(filename, tagname):
            logging.debug("adding_tag_to_filename(%s, %s): tag already found in filename" % (filename, tagname))

            return filename

        else:
            logging.debug("adding_tag_to_filename(%s, %s): add as additional tag to existing list of tags" %
                          (filename, tagname))

            components = re.match(FILE_WITH_EXTENSION_REGEX, os.path.basename(filename))
            if components:
                old_filename = components.group(1)
                extension = components.group(2)
                return os.path.join(os.path.dirname(filename), old_filename + BETWEEN_TAG_SEPARATOR + tagname + u'.' + extension)
            else:
                return os.path.join(os.path.dirname(filename), filename + BETWEEN_TAG_SEPARATOR + tagname)

    def rename_file(self, oldfilename, newfilename, dryrun=False, quiet=False):
        """
        Renames a file from oldfilename to newfilename.

        Only simulates result if dryrun is True.

        @param oldfilename: string containing the old file name
        @param newfilename: string containing the new file name
        @param dryrun: boolean which defines if files should be changed (False) or not (True)
        """

        if dryrun:
            logging.info(u" ")
            logging.info(u" renaming \"%s\"" % oldfilename)
            logging.info(u"      ⤷   \"%s\"" % (newfilename))
        else:
            if oldfilename != newfilename:
                if not quiet:
                    print u"   %s  ⤷  %s" % (oldfilename, newfilename)
                logging.debug(u" renaming \"%s\"" % oldfilename)
                logging.debug(u"      ⤷   \"%s\"" % (newfilename))
                os.rename(oldfilename, newfilename)

    def derive_new_filename_from_old_filename(self, oldfilename):
        """
        Analyses the old filename and returns a new one if feasible.
        If not, False is returned instead.

        @param oldfilename: string containing one file name
        @param return: False or new oldfilename
        """

        datetimestr, basefilename, tags, extension = self.split_filename_entities(oldfilename)

        if (" a1 " or " A1 ") in oldfilename and self.str_contains_euro_charge(oldfilename) and datetimestr:
            return datetimestr + \
                " A1 Festnetz-Internet " + self.get_euro_charge(oldfilename) + \
                " -- " + ' '.join(adding_tags(tags, ['scan', 'finance', 'bill'])) + \
                ".pdf"

        pass ## FIXXME: more cases!

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

        new_filename = self.derive_new_filename_from_old_filename(oldfilename)
        if new_filename:
            self.rename_file(oldfilename, new_filename, dryrun, options.quiet)
        #else:
        #    new_filename = self.derive_new_filename_from_content(oldfilename)

        pass ## FIXXME: ========================================= marker

        return new_filename

    def split_filename_entities(self, filename):
        """
        Takes a filename of format ( (date(time)?)?(--date(time)?)? )? filename (tags)? (extension)?
        and returns a set of (date/time/duration, filename, array of tags, extension).
        """

        assert(type(filename) == unicode or type(filename) == str)
        assert(len(filename)>0)

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

    def str_contains_euro_charge(self, string):
        """
        Returns true, if the string contains a number with a €-currency
        """

        assert(type(string) == unicode or type(string) == str)
        assert(len(string)>0)

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
        assert(len(string)>0)

        components = re.match(self.EURO_CHARGE_REGEX, string)

        if components:
            return components.group(self.EURO_CHARGE_INDEX)
        else:
            return False


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

    logging.debug("extracting list of files ...")
    logging.debug("len(args) [%s]" % str(len(args)))

    files = args

    logging.debug("%s filenames found: [%s]" % (str(len(files)), '], ['.join(files)))

    guess_filename = GuessFilename()

    if len(args) < 1:
        error_exit(5, "Please add at least one file name as argument")

    logging.debug("iterate over files ...")
    for filename in files:
        if filename.__class__ == str:
            filename = unicode(filename, "UTF-8")
        guess_filename.handle_file(filename, options.dryrun)

    logging.debug("successfully finished.")

    if not options.quiet:
        ## add empty line for better screen output readability
        print


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:

        logging.info("Received KeyboardInterrupt")

## END OF FILE #################################################################

#end
