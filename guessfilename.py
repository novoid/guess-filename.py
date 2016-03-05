#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2016-03-05 11:59:27 vk>

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

parser.add_option("-s", "--dryrun", dest="dryrun", action="store_true",
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
    DAY_REGEX="[12]\d{3}-[01]\d-[0123]\d"
    TIME_REGEX="T[012]\d.[012345]\d(.[012345]\d)?"
    DAYTIME_REGEX="(" + DAY_REGEX + "(" + TIME_REGEX + ")?)"
    DAYTIME_DURATION_REGEX=DAYTIME_REGEX + "(--?" + DAYTIME_REGEX + ")?"

    ISO_NAME_TAGS_EXTENSION_REGEX = re.compile("((" + DAYTIME_DURATION_REGEX + ")[ -_])?(.+?)(" + FILENAME_TAG_SEPARATOR + "(\w+[" + BETWEEN_TAG_SEPARATOR + "]?)+)?(\.(\w+))?$")
    DAYTIME_DURATION_INDEX=2
    NAME_INDEX=10
    TAGS_INDEX=11
    EXTENSION_INDEX=14

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

    def handle_file(self, filename, tags, do_remove, dryrun):
        """
        @param filename: string containing one file name
        @param tags: list containing one or more tags
        @param do_remove: boolean which defines if tags should be added (False) or removed (True)
        @param dryrun: boolean which defines if files should be changed (False) or not (True)
        @param return: error value or new filename
        """

        assert filename.__class__ == str or \
            filename.__class__ == unicode
        assert tags.__class__ == list
        if do_remove:
            assert do_remove.__class__ == bool
        if dryrun:
            assert dryrun.__class__ == bool

        if os.path.isdir(filename):
            logging.warning("Skipping directory \"%s\" because this tool only renames file names." % filename)
            return
        elif not os.path.isfile(filename):
            logging.debug("file type error in folder [%s]: file type: is file? %s  -  is dir? %s  -  is mount? %s" % (os.getcwdu(), str(os.path.isfile(filename)), str(os.path.isdir(filename)), str(os.path.islink(filename))))
            logging.error("Skipping \"%s\" because this tool only renames existing file names." % filename)
            return

        new_filename = filename

        ## if tag within UNIQUE_LABELS found, and new UNIQUE_LABEL is given, remove old label:
        ## e.g.: UNIQUE_LABELS = (u'yes', u'no') -> if 'no' should be added, remove existing label 'yes' (and vice versa)
        ## FIXXME: this is an undocumented feature -> please add proper documentation
        if not do_remove:
            unique_labels_in_old_filename = set(extract_tags_from_filename(filename)).intersection(UNIQUE_LABELS)
            unique_label_to_add = set(tags).intersection(UNIQUE_LABELS)
            if unique_label_to_add and unique_labels_in_old_filename:
                logging.debug("found unique label %s which require old unique label to be removed: %s" % (str(unique_label_to_add), str(unique_labels_in_old_filename)))
                for tagname in unique_labels_in_old_filename:
                    new_filename = removing_tag_from_filename(new_filename, tagname)

        for tagname in tags:
            if do_remove:
                new_filename = removing_tag_from_filename(new_filename, tagname)
            else:
                new_filename = adding_tag_to_filename(new_filename, tagname)

        if dryrun:
            logging.info(u" ")
            logging.info(u" renaming \"%s\"" % filename)
            logging.info(u"      ⤷   \"%s\"" % (new_filename))
        else:
            if filename != new_filename:
                if not options.quiet:
                    print u"   %s  ⤷  %s" % (filename, new_filename)
                logging.debug(u" renaming \"%s\"" % filename)
                logging.debug(u"      ⤷   \"%s\"" % (new_filename))
                os.rename(filename, new_filename)

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

        if components.group(11):
            tags = components.group(11)[4:].split(' ')
        else:
            tags = []
        return components.group(2), \
            components.group(10), \
            tags, \
            components.group(14)


def main():
    """Main function"""

    guess_filename = GuessFilename()

    sys.exit(0)

    if options.version:
        print os.path.basename(sys.argv[0]) + " version " + PROG_VERSION_NUMBER + \
            " from " + PROG_VERSION_DATE
        sys.exit(0)

    handle_logging()

    if options.verbose and options.quiet:
        error_exit(1, "Options \"--verbose\" and \"--quiet\" found. " +
                   "This does not make any sense, you silly fool :-)")

    ## interactive mode and tags are given
    if options.interactive and options.tags:
        error_exit(3, "I found option \"--tag\" and option \"--interactive\". \n" +
                   "Please choose either tag option OR interactive mode.")

    if options.list_tags_by_number and options.list_tags_by_alphabet:
        error_exit(6, "Please use only one list-by-option at once.")

    if options.tag_gardening and (options.list_tags_by_number or options.list_tags_by_alphabet or options.tags or options.remove):
        error_exit(7, "Please don't use that gardening option together with any other option.")

    if (options.list_tags_by_alphabet or options.list_tags_by_number) and (options.tags or options.interactive or options.remove):
        error_exit(8, "Please don't use list any option together with add/remove tag options.")

    logging.debug("extracting list of files ...")
    logging.debug("len(args) [%s]" % str(len(args)))

    files = extract_filenames_from_argument(args)

    logging.debug("%s filenames found: [%s]" % (str(len(files)), '], ['.join(files)))

    tags_from_userinput = []
    vocabulary = locate_and_parse_controlled_vocabulary(os.getcwdu())

    if len(args) < 1 and not (options.list_tags_by_alphabet or options.list_tags_by_number or options.list_unknown_tags or options.tag_gardening):
        error_exit(5, "Please add at least one file name as argument")

    if options.list_tags_by_alphabet:
        logging.debug("handling option list_tags_by_alphabet")
        list_tags_by_alphabet()

    elif options.list_tags_by_number:
        logging.debug("handling option list_tags_by_number")
        list_tags_by_number()

    elif options.list_unknown_tags:
        logging.debug("handling option list_unknown_tags")
        list_unknown_tags()

    elif options.tag_gardening:
        logging.debug("handling option for tag gardening")
        handle_tag_gardening(vocabulary)

    elif options.interactive or not options.tags:

        completionhint = u''

        if len(args) < 1:
            error_exit(5, "Please add at least one file name as argument")

        tags_from_filenames_of_arguments_dict = {}
        upto9_tags_from_filenames_of_same_dir_list = []

        ## look out for .filetags file and add readline support for tag completion if found with content
        if options.remove:
            ## vocabulary for completing tags is current tags of files
            for file in files:
                ## add tags so that list contains all unique tags:
                for newtag in extract_tags_from_filename(file):
                    add_tag_to_countdict(newtag, tags_from_filenames_of_arguments_dict)

            vocabulary = sorted(tags_from_filenames_of_arguments_dict.keys())
            upto9_tags_from_filenames_of_arguments_list = sorted(get_upto_nine_keys_of_dict_with_highest_value(tags_from_filenames_of_arguments_dict))
        else:
            if files:

                upto9_tags_from_filenames_of_same_dir_list = sorted(get_upto_nine_keys_of_dict_with_highest_value(get_tags_from_files_and_subfolders(startdir=os.path.dirname(os.path.abspath(files[0])))))
            vocabulary = sorted(locate_and_parse_controlled_vocabulary(args[0]))

        if vocabulary:

            assert(vocabulary.__class__ == list)

            # Register our completer function
            readline.set_completer(SimpleCompleter(vocabulary).complete)

            # Use the tab key for completion
            readline.parse_and_bind('tab: complete')

            completionhint = u'; complete %s tags with TAB' % str(len(vocabulary))

        logging.debug("len(args) [%s]" % str(len(args)))
        logging.debug("args %s" % str(args))

        print "                 "
        print "Please enter tags, separated by \"" + BETWEEN_TAG_SEPARATOR + "\"; abort with Ctrl-C" + \
            completionhint
        print "                     "
        print "        ,---------.  "
        print "        |  ?     o | "
        print "        `---------'  "
        print "                     "

        if options.remove:
            logging.info("Interactive mode: tags get REMOVED from file names ...")
            if len(upto9_tags_from_filenames_of_arguments_list) > 0:
                print_tag_shortcut_with_numbers(upto9_tags_from_filenames_of_arguments_list, tags_get_added=False)
        else:
            logging.debug("Interactive mode: tags get ADDED to file names ...")
            if upto9_tags_from_filenames_of_same_dir_list:
                print_tag_shortcut_with_numbers(upto9_tags_from_filenames_of_same_dir_list, tags_get_added=True)


        ## interactive: ask for list of tags
        logging.debug("interactive mode: asking for tags ...")

        entered_tags = raw_input('Tags: ').strip()

        tags_from_userinput = extract_tags_from_argument(entered_tags)

        if not tags_from_userinput:
            logging.info("no tags given, exiting.")
            sys.stdout.flush()
            sys.exit(0)

        if options.remove:
            if len(tags_from_userinput) == 1 and len(upto9_tags_from_filenames_of_arguments_list) > 0:
                ## check if user entered number shortcuts for tags to be removed:
                tags_from_userinput = check_for_possible_shortcuts_in_entered_tags(tags_from_userinput, upto9_tags_from_filenames_of_arguments_list)

            logging.info("removing tags \"%s\" ..." % str(BETWEEN_TAG_SEPARATOR.join(tags_from_userinput)))
        else:
            if len(tags_from_userinput) == 1 and upto9_tags_from_filenames_of_same_dir_list:
                ## check if user entered number shortcuts for tags to be removed:
                tags_from_userinput = check_for_possible_shortcuts_in_entered_tags(tags_from_userinput, upto9_tags_from_filenames_of_same_dir_list)
            logging.info("adding tags \"%s\" ..." % str(BETWEEN_TAG_SEPARATOR.join(tags_from_userinput)))

    else:
        ## non-interactive: extract list of tags
        logging.debug("non-interactive mode: extracting tags from argument ...")

        tags_from_userinput = extract_tags_from_argument(options.tags)

        if not tags_from_userinput:
            ## FIXXME: check: can this be the case?
            logging.info("no tags given, exiting.")
            sys.stdout.flush()
            sys.exit(0)

    logging.debug("tags found: [%s]" % '], ['.join(tags_from_userinput))

    logging.debug("iterate over files ...")
    for filename in files:
        if filename.__class__ == str:
            filename = unicode(filename, "UTF-8")
        handle_file(filename, tags_from_userinput, options.remove, options.dryrun)

    logging.debug("successfully finished.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:

        logging.info("Received KeyboardInterrupt")

## END OF FILE #################################################################

#end
