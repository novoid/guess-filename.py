#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2017-01-06 14:44:59 vk>

# TODO:
# * add -i (interactive) where user gets asked if renaming should be done (per file)
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

try:
    import PyPDF2
except ImportError:
    print "Could not find Python module \"PyPDF2\".\nPlease install it, e.g., with \"sudo pip install PyPDF2\"."
    sys.exit(1)

PROG_VERSION_NUMBER = u"0.1"
PROG_VERSION_DATE = u"2016-03-06"
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
Verbose description: FIXXME: http://Karl-Voit.at/FIXXME/\n\
\n\
:copyright: (c) by Karl Voit <tools@Karl-Voit.at>\n\
:license: GPL v3 or any later version\n\
:URL: https://github.com/novoid/guess-filename.py\n\
:bugreports: via github or <tools@Karl-Voit.at>\n\
:version: " + PROG_VERSION_NUMBER + " from " + PROG_VERSION_DATE + "\n"

ERROR_DIR = 'guess-filename_fails'
SUCCESS_DIR = 'guess-filename_success'

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
    DAY_REGEX = '[12]\d{3}-?[01]\d-?[0123]\d'  # note: I made the dashes between optional to match simpler format as well
    TIME_REGEX = 'T[012]\d.[012345]\d(.[012345]\d)?'

    DAYTIME_REGEX = '(' + DAY_REGEX + '(' + TIME_REGEX + ')?)'
    DAYTIME_DURATION_REGEX = DAYTIME_REGEX + '(--?' + DAYTIME_REGEX + ')?'

    ISO_NAME_TAGS_EXTENSION_REGEX = re.compile('((' + DAYTIME_DURATION_REGEX + ')[ -_])?(.+?)(' + FILENAME_TAG_SEPARATOR + '((\w+[' + BETWEEN_TAG_SEPARATOR + ']?)+))?(\.(\w+))?$', re.UNICODE)
    DAYTIME_DURATION_INDEX = 2
    NAME_INDEX = 10
    TAGS_INDEX = 12
    EXTENSION_INDEX = 15

    RAW_EURO_CHARGE_REGEX = u'(\d+([,.]\d+)?)[-_ ]?(EUR|€)'
    EURO_CHARGE_REGEX = re.compile(u'^(.+[-_ ])?' + RAW_EURO_CHARGE_REGEX + '([-_ .].+)?$', re.UNICODE)
    EURO_CHARGE_INDEX = 2

    ANDROID_SCREENSHOT_REGEX = re.compile(u'Screenshot_([12]\d{3})-?([01]\d)-?([0123]\d)' + '-?' + \
                               '([012]\d).?([012345]\d)(.?([012345]\d))?' + '( .*)?.png', re.UNICODE)
    ANDROID_SCREENSHOT_INDEXGROUPS = [1, '-', 2, '-', 3, 'T', 4, '.', 5, '.', 7, 8, ' -- screenshots android.png']

    TIMESTAMP_DELIMITERS = '[.;:-]?'
    DATESTAMP_REGEX = '([12]\d{3})' + TIMESTAMP_DELIMITERS + '([01]\d)' + TIMESTAMP_DELIMITERS + '([0123]\d)'
    TIMESTAMP_REGEX = '([012]\d)' + TIMESTAMP_DELIMITERS + '([012345]\d)(' + TIMESTAMP_DELIMITERS + '([012345]\d))?'

    OSMTRACKS_REGEX = re.compile(DATESTAMP_REGEX + 'T?' + TIMESTAMP_REGEX + '(_.*)?.gpx', re.UNICODE)
    OSMTRACKS_INDEXGROUPS = [1, '-', 2, '-', 3, 'T', 4, '.', 5, ['.', 7], 8, '.gpx']

    IMG_REGEX = re.compile(u'IMG_' + DATESTAMP_REGEX + '_' + TIMESTAMP_REGEX + '(.+)?.jpg', re.UNICODE)
    IMG_INDEXGROUPS = [1, '-', 2, '-', 3, 'T', 4, '.', 5, ['.', 7], 8, '.jpg']
    VID_REGEX = re.compile(u'VID_' + DATESTAMP_REGEX + '_' + TIMESTAMP_REGEX + '(.+)?.mp4', re.UNICODE)
    VID_INDEXGROUPS = [1, '-', 2, '-', 3, 'T', 4, '.', 5, ['.', 7], 8, '.mp4']

    # MediathekView: Settings > modify Set > Targetfilename: "%DT%d h%i %s %t - %T - %N.mp4"
    # results in files like:
    #   20161227T201500 h115421 ORF Das Sacher. In bester Gesellschaft 1.mp4
    #   20161227T193000 l119684 ORF ZIB 1 - Auswirkungen der _Panama-Papers_ - 2016-12-27_1930_tl_02_ZIB-1_Auswirkungen-de__.mp4
    MEDIATHEKVIEW_REGEX = re.compile(DATESTAMP_REGEX + 'T?' + TIMESTAMP_REGEX + \
                          '(.+?)( - [12]\d{3}' + TIMESTAMP_DELIMITERS + '[01]\d' + TIMESTAMP_DELIMITERS + \
                          '[0123]\d_.+)?.mp4', re.UNICODE)
    MEDIATHEKVIEW_INDEXGROUPS = [1, '-', 2, '-', 3, 'T', 4, '.', 5, ['.', 7], 8, '.mp4']

    logger = None
    config = None

    def __init__(self, config, logger):
        self.logger = logger
        self.config = config

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

    def contains_all_of(self, string, entries):
        """
        Returns true, if the string contains all of the strings within entries array
        """

        assert(type(string) == unicode or type(string) == str)
        assert(type(entries) == list)
        assert(len(string) > 0)
        assert(len(entries) > 0)

        for entry in entries:
            if entry not in string:
                return False

        return True

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

    def fuzzy_contains_all_of(self, string, entries):
        """
        Returns true, if the string contains all similar ones of the strings within the entries array
        """

        assert(type(string) == unicode or type(string) == str)
        assert(type(entries) == list)
        assert(len(string) > 0)
        assert(len(entries) > 0)

        for entry in entries:
            assert(type(entry) == unicode or type(entry) == str)
            #logging.debug(u"fuzzy_contains_all_of(%s..., %s...) ... " % (string[:30], str(entry[:30])))
            if not entry in string:
                ## if entry is found in string (exactly), try with fuzzy search:

                similarity = fuzz.partial_ratio(string, entry)
                if similarity > 64:
                    #logging.debug(u"MATCH   fuzzy_contains_all_of(%s..., %s) == %i" % (string[:30], str(entry), similarity))
                    pass
                else:
                    #logging.debug(u"¬ MATCH fuzzy_contains_all_of(%s..., %s) == %i" % (string[:30], str(entry), similarity))
                    return False

        return True

    def has_euro_charge(self, string):
        """
        Returns true, if the single-line string contains a number with a €-currency
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
        Returns the first included €-currency within single-line "string" or False
        """

        assert(type(string) == unicode or type(string) == str)
        assert(len(string) > 0)

        components = re.match(self.EURO_CHARGE_REGEX, string)

        if components:
            return components.group(self.EURO_CHARGE_INDEX)
        else:
            return False

    def get_euro_charge_from_context_or_basename(self, string, before, after, basename):
        """
        Returns the included €-currency which is between before and after
        strings or within the basename or return 'FIXXME'
        """

        charge = self.get_euro_charge_from_context(string, before, after)
        if not charge:
            charge = self.get_euro_charge(basename)
            if not charge:
                return 'FIXXME'

        return charge

    def get_euro_charge_from_context(self, string, before, after):
        """
        Returns the included €-currency which is between before and after strings or False
        """

        assert(type(string) == unicode or type(string) == str)
        assert(type(before) == unicode or type(before) == str)
        assert(type(after) == unicode or type(after) == str)
        assert(len(string) > 0)

        context_range = '5'  # range of characters where before/after is valid

        # for testing: re.search(".*" + before + r"\D{0,6}(\d{1,6}[,.]\d{2})\D{0,6}" + after + ".*", string).groups()
        components = re.search(".*" + before + r"\D{0," + context_range + "}((\d{1,6})[,.](\d{2}))\D{0," + context_range + "}" + after + ".*", string)

        if components:
            floatstring = components.group(2) + ',' + components.group(3)
            #logging.debug("get_euro_charge_from_context extracted float: [%s]" % floatstring)
            return floatstring
        else:
            logging.warning(u"Sorry, I was not able to extract a charge for this file, please fix manually")
            logging.debug(u"get_euro_charge_from_context was not able to extract a float: between [%s] and [%s] within [%s]" % (before, after, string[:30] + u"..."))
            return False

    def rename_file(self, dirname, oldbasename, newbasename, dryrun=False, quiet=False):
        """
        Renames a file from oldbasename to newbasename in dirname.

        Only simulates result if dryrun is True.

        @param dirname: string containing the directory of the file
        @param oldbasename: string containing the old file name (basename)
        @param newbasename: string containing the new file name (basename)
        @param dryrun: boolean which defines if files should be changed (False) or not (True)
        """

        if oldbasename == newbasename:
            logging.info("Old filename is same as new filename: skipping file")
            return False

        oldfile = os.path.join(dirname, oldbasename).encode('utf-8')
        newfile = os.path.join(dirname, newbasename).encode('utf-8')

        if not os.path.isfile(oldfile):
            logging.error("file to rename does not exist: [%s]" % oldfile)
            return False

        if os.path.isfile(newfile):
            logging.error("file can't be renamed since new file name already exists: [%s]" % newfile)
            return False

        if not quiet:
            print u'       →  '.encode('utf-8') + newbasename.encode('utf-8')
        logging.debug(u" renaming \"%s\"".encode('utf-8') % oldfile)
        logging.debug(u"      ⤷   \"%s\"".encode('utf-8') % newfile)
        if not dryrun:
            os.rename(oldfile, newfile)
        return True

    def build_string_via_indexgroups(self, regex_match, indexgroups):
        """This function takes a regex_match object and concatenates its
        groups. It does this by traversing the list of indexgroups. If
        the list item is an integer, the corresponding
        regex_match.group() is appended to the result string. If the
        list item is a string, the string is appended to the result
        string.

        When a list item is a list, its elements are appended as well as
        long as all list items exist.

        match-groups that are in the indexgroups but are None are ignored.

        @param regex_match: a regex match object from re.match(REGEX, STRING)
        @param indexgroups: list of strings and integers like [1, '-', 2, '-', 3, 'T', 4, '.', 5, ' foo .png']
        @param return: string containing the concatenated string

        """

        if not regex_match:
            logging.error('no re.match object found; please check before calling build_string_via_indexgroups()')
            return "ERROR"

        def append_element(string, indexgroups):
            result = string
            for element in indexgroups:
                if type(element) ==  str:
                    result += element
                    #print 'DEBUG: result after element [' + str(element)  + '] =  [' + str(result) + ']'
                elif type(element) == int:
                    potential_element = regex_match.group(element)
                    # ignore None matches
                    if potential_element:
                        result += regex_match.group(element)
                        #print 'DEBUG: result after element [' + str(element)  + '] =  [' + str(result) + ']'
                    else:
                        #print 'DEBUG: match-group element ' + str(element) + ' is None'
                        pass
                elif type(element) == list:
                    # recursive: if a list element is a list, process if all elements exists:
                    #print 'DEBUG: found list item = ' + str(element)
                    #print 'DEBUG:   result before = [' + str(result) + ']'
                    all_found = True
                    for listelement in element:
                        if type(listelement) == int and (regex_match.group(listelement) is None or
                                                         len(regex_match.group(listelement)) <1):
                            all_found = False
                    if all_found:
                        result = append_element(result, element)
                        #print 'DEBUG:   result after =  [' + str(result) + ']'
                    else:
                        pass
                        #print 'DEBUG:   result after =  [' + str(result) + ']' + \
                        #    '   -> not changed because one or more elements of sub-list were not found'
            return result

        logging.debug('build_string_via_indexgroups: FILENAME: ' + str(regex_match.group(0).encode('utf-8')))
        logging.debug('build_string_via_indexgroups: GROUPS: ' + str(regex_match.groups()))
        result = append_element(u'', indexgroups)
        logging.debug('build_string_via_indexgroups: RESULT:   ' + result)
        return result

    def derive_new_filename_from_old_filename(self, oldfilename):
        """
        Analyses the old filename and returns a new one if feasible.
        If not, False is returned instead.

        @param oldfilename: string containing one file name
        @param return: False or new filename
        """

        logging.debug("derive_new_filename_from_old_filename called")
        datetimestr, basefilename, tags, extension = self.split_filename_entities(oldfilename)

        # Android screenshots:
        # Screenshot_2013-03-05-08-14-09.png -> 2013-03-05T08-14-09 -- android screenshots.png
        regex_match = re.match(self.ANDROID_SCREENSHOT_REGEX, oldfilename)
        if regex_match:
            return self.build_string_via_indexgroups(regex_match, self.ANDROID_SCREENSHOT_INDEXGROUPS)

        # MediathekView: Settings > modify Set > Targetfilename: "%DT%d h%i %s %t - %T - %N.mp4"
        # results in files like:
        #   20161227T201500 h115421 ORF Das Sacher. In bester Gesellschaft 1.mp4
        #     -> 2016-12-27T20.15.00 h115421 ORF Das Sacher. In bester Gesellschaft 1.mp4
        #   20161227T193000 l119684 ORF ZIB 1 - Auswirkungen der _Panama-Papers_ - 2016-12-27_1930_tl_02_ZIB-1_Auswirkungen-de__.mp4
        #     -> 2016-12-27T19.30.00 l119684 ORF ZIB 1 - Auswirkungen der _Panama-Papers_.mp4
        regex_match = re.match(self.MEDIATHEKVIEW_REGEX, oldfilename)
        if regex_match:
            return self.build_string_via_indexgroups(regex_match, self.MEDIATHEKVIEW_INDEXGROUPS).replace('_', ' ')

        # Android OSMTracker GPS track files:
        # 2015-05-27T09;00;15_foo_bar.gpx -> 2015-05-27T09.00.15 foo bar.gpx
        regex_match = re.match(self.OSMTRACKS_REGEX, oldfilename)
        if regex_match:
            return self.build_string_via_indexgroups(regex_match, self.OSMTRACKS_INDEXGROUPS).replace('_', ' ')

        # digital camera images: IMG_20161014_214404 foo bar.jpg -> 2016-10-14T21.44.04 foo bar.jpg  OR
        regex_match = re.match(self.IMG_REGEX, oldfilename)
        if regex_match:
            return self.build_string_via_indexgroups(regex_match, self.IMG_INDEXGROUPS)
        #                        VID_20170105_173104.mp4         -> 2017-01-05T17.31.04.mp4
        regex_match = re.match(self.VID_REGEX, oldfilename)
        if regex_match:
            return self.build_string_via_indexgroups(regex_match, self.VID_INDEXGROUPS)

        # 2015-11-24 Rechnung A1 Festnetz-Internet 12,34€ -- scan bill.pdf
        if self.contains_one_of(oldfilename, [" A1 ", " a1 "]) and self.has_euro_charge(oldfilename) and datetimestr:
            return datetimestr + \
                u" A1 Festnetz-Internet " + self.get_euro_charge(oldfilename) + \
                u"€ -- " + ' '.join(self.adding_tags(tags, ['scan', 'bill'])) + \
                u".pdf"

        # 2016-01-19--2016-02-12 benutzter GVB 10er Block -- scan transportation graz.pdf
        if self.contains_one_of(oldfilename, ["10er"]) and datetimestr:
            return datetimestr + \
                u" benutzter GVB 10er Block" + \
                u" -- " + ' '.join(self.adding_tags(tags, ['scan', 'transportation', 'graz'])) + \
                u".pdf"

        # 2016-01-19 bill foobar baz 12,12EUR.pdf -> 2016-01-19 foobar baz 12,12€ -- scan bill.pdf
        if u'bill' in oldfilename and datetimestr and self.has_euro_charge(oldfilename):
            return datetimestr + ' ' + \
                basefilename.replace(' bill', ' ').replace('bill ', ' ').replace('  ', ' ').replace(u'EUR', u'€').strip() + \
                u" -- " + ' '.join(self.adding_tags(tags, ['scan', 'bill'])) + \
                u".pdf"

        # 2015-04-30 FH St.Poelten - Abrechnungsbeleg 12,34 EUR - Honorar -- scan fhstp.pdf
        if self.contains_all_of(oldfilename, [" FH ", "Abrechnungsbeleg"]) and self.has_euro_charge(oldfilename) and datetimestr:
            return datetimestr + \
                u" FH St.Poelten - Abrechnungsbeleg " + self.get_euro_charge(oldfilename) + \
                u"€ Honorar -- " + ' '.join(self.adding_tags(tags, ['scan', 'fhstp'])) + \
                u".pdf"

        # 2016-02-26 Gehaltszettel Februar 12,34 EUR -- scan infonova.pdf
        if self.contains_all_of(oldfilename, ["Gehalt", "infonova"]) and self.has_euro_charge(oldfilename) and datetimestr:
            return datetimestr + \
                u" Gehaltszettel " + self.get_euro_charge(oldfilename) + \
                u"€ -- " + ' '.join(self.adding_tags(tags, ['scan', 'infonova'])) + \
                u".pdf"

        # 2012-05-26T22.25.12_IMAG0861 Rage Ergebnis - MITSPIELER -- games.jpg
        if self.contains_one_of(basefilename, ["Hive", "Rage", "Stratego"]) and \
           extension.lower() == 'jpg' and not self.has_euro_charge(oldfilename):
            return datetimestr + basefilename + \
                u" - Ergebnis -- games" + \
                u".jpg"

        # 2015-03-11 VBV Kontoinformation 123 EUR -- scan finance infonova.pdf
        if self.contains_all_of(oldfilename, ["VBV", "Kontoinformation"]) and self.has_euro_charge(oldfilename) and datetimestr:
            return datetimestr + \
                u" VBV Kontoinformation " + self.get_euro_charge(oldfilename) + \
                u"€ -- " + ' '.join(self.adding_tags(tags, ['scan', 'finance', 'infonova'])) + \
                u".pdf"

        # 2015-03-11 Verbrauchsablesung Wasser - Holding Graz -- scan bwg.pdf
        if self.contains_all_of(oldfilename, ["Verbrauchsablesung", "Wasser"]) and datetimestr:
            return datetimestr + \
                u" Verbrauchsablesung Wasser - Holding Graz -- " + \
                ' '.join(self.adding_tags(tags, ['scan', 'bwg'])) + \
                u".pdf"

        # FIXXME: more cases!

        return False  # no new filename found

    def derive_new_filename_from_content(self, dirname, basename):
        """
        Analyses the content of basename and returns a new file name if feasible.
        If not, False is returned instead.

        @param dirname: string containing the directory of file within basename
        @param basename: string containing one file name
        @param return: False or new filename
        """

        filename = os.path.join(dirname, basename)
        assert os.path.isfile(filename)

        try:
            pdffile = PyPDF2.PdfFileReader(open(filename, "rb"))
        except:
            logging.error('Could not read PDF file content. Skipping its content.')
            return False
        ## use first and second page of content only:
        if pdffile.getNumPages() > 1:
            content = pdffile.pages[0].extractText() + pdffile.pages[1].extractText()
        elif pdffile.getNumPages() == 1:
            content = pdffile.pages[0].extractText()
        else:
            logging.error('Could not determine number of pages of PDF content! (skipping content analysis)')
            return False

        if len(content) == 0:
            logging.warning('Could read PDF file content but it is empty (skipping content analysis)')
            return False

        datetimestr, basefilename, tags, extension = self.split_filename_entities(basename)

        if extension.lower() != 'pdf':
            logging.debug("File is not a PDF file and thus can't be parsed by this script: %s" % filename)
            return False

        # 2010-06-08 easybank - neue TAN-Liste -- scan private.pdf
        if self.fuzzy_contains_all_of(content, ["Transaktionsnummern (TANs)", "Ihre TAN-Liste in Verlust geraten"]) and \
           datetimestr:
            return datetimestr + \
                u" easybank - neue TAN-Liste -- " + \
                ' '.join(self.adding_tags(tags, ['scan', 'private'])) + \
                u".pdf"

        # 2015-11-20 Kirchenbeitrag 12,34 EUR -- scan taxes bill.pdf
        if self.fuzzy_contains_all_of(content, ["4294-0208", "AT086000000007042401"]) and \
           datetimestr:
            floatstr = self.get_euro_charge_from_context_or_basename(content, "Offen", "Zahlungen", basename)
            return datetimestr + \
                u" Kirchenbeitrag " + floatstr + u"€ -- " + \
                ' '.join(self.adding_tags(tags, ['scan', 'taxes', 'bill'])) + \
                u".pdf"

        # 2015-11-24 Generali Erhoehung Dynamikklausel - Praemie nun 12,34 - Polizze 12345 -- scan bill.pdf
        if self.config.GENERALI1_POLIZZE_NUMBER in content and \
           self.fuzzy_contains_all_of(content, [u"ImHinblickaufdievereinbarteDynamikklauseltritteineWertsteigerunginKraft",
                                                u"IhreangepasstePrämiebeträgtdahermonatlich",
                                                u"AT44ZZZ00000002054"]) and \
            datetimestr:
            floatstr = self.get_euro_charge_from_context_or_basename(content,
                                                                     "IndiesemBetragistauchdiegesetzlicheVersicherungssteuerenthalten.EUR",
                                                                     "Wird",
                                                                     basename)
            return datetimestr + \
                u" Generali Erhoehung Dynamikklausel - Praemie nun " + floatstr + \
                u"€ - Polizze " + self.config.GENERALI1_POLIZZE_NUMBER + " -- " + \
                ' '.join(self.adding_tags(tags, ['scan', 'bill'])) + \
                u".pdf"

        # 2015-11-30 Merkur Lebensversicherung 123456 - Praemienzahlungsaufforderung 12,34€ -- scan bill.pdf
        if self.config.MERKUR_GESUNDHEITSVORSORGE_NUMBER in content and \
           self.fuzzy_contains_all_of(content, [u"Prämienvorschreibung",
                                                self.config.MERKUR_GESUNDHEITSVORSORGE_ZAHLUNGSREFERENZ]) and \
            datetimestr:
            floatstr = self.get_euro_charge_from_context_or_basename(content,
                                                                     "EUR",
                                                                     "Gesundheit ist ein kostbares Gut",
                                                                     basename)
            return datetimestr + \
                u" Merkur Lebensversicherung " + self.config.MERKUR_GESUNDHEITSVORSORGE_NUMBER + \
                u" - Praemienzahlungsaufforderung " + floatstr + \
                u"€ -- " + \
                ' '.join(self.adding_tags(tags, ['scan', 'bill'])) + \
                u".pdf"

        # 2016-02-22 BANK - Darlehnen - Kontomitteilung -- scan taxes.pdf
        if self.fuzzy_contains_all_of(content, [self.config.LOAN_INSTITUTE, self.config.LOAN_ID]) and \
            datetimestr:
            return datetimestr + \
                u" " + self.config.LOAN_INSTITUTE + " - Darlehnen - Kontomitteilung -- " + \
                ' '.join(self.adding_tags(tags, ['scan', 'taxes'])) + \
                u".pdf"

        # 2015-11-24 Rechnung A1 Festnetz-Internet 12,34€ -- scan bill.pdf
        if self.fuzzy_contains_all_of(content, [self.config.PROVIDER_CONTRACT, self.config.PROVIDER_CUE]) and \
            datetimestr:
            floatstr = self.get_euro_charge_from_context_or_basename(content,
                                                                     u"\u2022",
                                                                     "Bei Online Zahlungen geben Sie",
                                                                     basename)
            return datetimestr + \
                u" A1 Festnetz-Internet " + floatstr + \
                u"€ -- " + ' '.join(self.adding_tags(tags, ['scan', 'bill'])) + \
                u".pdf"

        # FIXXME: more file documents
        #import pdb; pdb.set_trace()

        return False

    def handle_file(self, oldfilename, dryrun):
        """
        @param oldfilename: string containing one file name
        @param dryrun: boolean which defines if files should be changed (False) or not (True)
        @param return: error value or new filename
        """

        assert oldfilename.__class__ == str or \
            oldfilename.__class__ == unicode
        if dryrun:
            assert dryrun.__class__ == bool

        if os.path.isdir(oldfilename):
            logging.debug("Skipping directory \"%s\" because this tool only renames file names." % oldfilename)
            return
        elif not os.path.isfile(oldfilename):
            logging.debug("file type error in folder [%s]: file type: is file? %s  -  is dir? %s  -  is mount? %s" %
                          (os.getcwdu(), str(os.path.isfile(oldfilename)), str(os.path.isdir(oldfilename)), str(os.path.islink(oldfilename))))
            logging.error("Skipping \"%s\" because this tool only renames existing file names." % oldfilename)
            return

        print '\n   ' + oldfilename + '  ...'
        dirname = os.path.abspath(os.path.dirname(oldfilename))
        logging.debug(u"————→ dirname  [%s]" % dirname)
        basename = os.path.basename(oldfilename)
        logging.debug(u"————→ basename [%s]" % basename)

        newfilename = self.derive_new_filename_from_old_filename(basename)
        if newfilename:
            logging.debug(u"derive_new_filename_from_old_filename returned new filename: %s" % newfilename)
        else:
            logging.debug(u"derive_new_filename_from_old_filename could not derive a new filename for %s" % basename)

        if not newfilename:
            if basename[-4:].lower() == '.pdf':
                newfilename = self.derive_new_filename_from_content(dirname, basename)
                logging.debug(u"derive_new_filename_from_content returned new filename: %s" % newfilename)
            else:
                logging.debug(u"file extension is not PDF and therefore I skip analyzing file content")

        if newfilename:
            self.rename_file(dirname, basename, newfilename, dryrun)
            move_to_success_dir(dirname, newfilename)
            return newfilename
        else:
            logging.warning(u"I failed to derive new filename: not enough cues in file name or PDF file content")
            move_to_error_dir(dirname, basename)
            return False


def move_to_success_dir(dirname, newfilename):
    """
    Moves a file to SUCCESS_DIR
    """
    if os.path.isdir(SUCCESS_DIR):
        logging.debug('using hidden feature: if a folder named \"' + SUCCESS_DIR +
                      '\" exists, move renamed files into it')
        os.rename(os.path.join(dirname, newfilename), os.path.join(dirname, SUCCESS_DIR,
                                                                   newfilename))
        logging.info('moved file to sub-directory "' + SUCCESS_DIR + '"')


def move_to_error_dir(dirname, basename):
    """
    Moves a file to SUCCESS_DIR
    """
    if os.path.isdir(ERROR_DIR):
        logging.debug('using hidden feature: if a folder named \"' + ERROR_DIR +
                      '\" exists, move failed files into it')
        os.rename(os.path.join(dirname, basename),
                  os.path.join(dirname, ERROR_DIR, basename))
        logging.info('moved file to sub-directory "' + ERROR_DIR + '"')

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

    filenames_could_not_be_found = 0
    logging.debug("iterating over files ...\n" + "=" * 80)
    for filename in files:
        if filename.__class__ == str:
            filename = unicode(filename, "UTF-8")
        if not guess_filename.handle_file(filename, options.dryrun):
            filenames_could_not_be_found += 1

    if not options.quiet:
        # add empty line for better screen output readability
        print

    if filenames_could_not_be_found == 0:
        logging.debug('successfully finished.')
    else:
        logging.debug("finished with %i filename(s) that could not be derived" % filenames_could_not_be_found)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:

        logging.info("Received KeyboardInterrupt")

# END OF FILE #################################################################
