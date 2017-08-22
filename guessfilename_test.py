#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2017-08-22 12:21:24 vk>

import unittest
import logging
import tempfile
import os
import os.path
import sys
from guessfilename import GuessFilename


class TestGuessFilename(unittest.TestCase):

    guess_filename = None

    def handle_logging(self, verbose=False, quiet=False):
        """Log handling and configuration"""

        if verbose:
            FORMAT = "%(levelname)-8s %(asctime)-15s %(message)s"
            logging.basicConfig(level=logging.DEBUG, format=FORMAT)
        elif quiet:
            FORMAT = "%(levelname)-8s %(message)s"
            logging.basicConfig(level=logging.ERROR, format=FORMAT)
        else:
            FORMAT = "%(levelname)-8s %(message)s"
            logging.basicConfig(level=logging.INFO, format=FORMAT)

    def setUp(self):
        verbose = True
        quiet = False

        CONFIGDIR = os.path.join(os.path.expanduser("~"), ".config/guessfilename")
        sys.path.insert(0, CONFIGDIR)  # add CONFIGDIR to Python path in order to find config file
        try:
            import guessfilenameconfig
        except ImportError:
            print("Could not find \"guessfilenameconfig.py\" in directory \"" + CONFIGDIR + "\".\nPlease take a look at \"guessfilenameconfig-TEMPLATE.py\", copy it, and configure accordingly.")
            sys.exit(1)

        self.handle_logging(verbose, quiet)
        self.guess_filename = GuessFilename(guessfilenameconfig, logging)

    def tearDown(self):
        pass

    def test_rename_file(self):

        tmp_oldfile1 = tempfile.mkstemp()[1]
        oldbasename = os.path.basename(tmp_oldfile1)
        dirname = os.path.abspath(os.path.dirname(tmp_oldfile1))
        newbasename = 'test_rename_file'
        newfilename = os.path.join(dirname, newbasename)

        self.assertTrue(os.path.isfile(tmp_oldfile1))
        self.assertFalse(os.path.isfile(newfilename))

        # return False if files are identical
        self.assertFalse(self.guess_filename.rename_file(dirname, oldbasename, oldbasename, dryrun=True, quiet=True))

        # return False if original file does not exist
        self.assertFalse(self.guess_filename.rename_file(dirname, "test_rename_file_this-is-a-non-existing-file", oldbasename, dryrun=True, quiet=True))

        # return False if target filename does exist
        tmp_oldfile2 = tempfile.mkstemp()[1]
        self.assertTrue(os.path.isfile(tmp_oldfile2))
        oldbasename2 = os.path.basename(tmp_oldfile2)
        self.assertFalse(self.guess_filename.rename_file(dirname, oldbasename, oldbasename2, dryrun=True, quiet=True))
        os.remove(tmp_oldfile2)

        # no change with dryrun set:
        self.assertTrue(self.guess_filename.rename_file(dirname, oldbasename, newbasename, dryrun=True, quiet=True))
        self.assertTrue(os.path.isfile(tmp_oldfile1))
        self.assertFalse(os.path.isfile(newfilename))

        # do rename:
        self.assertTrue(self.guess_filename.rename_file(dirname, oldbasename, newbasename, dryrun=False, quiet=True))
        self.assertFalse(os.path.isfile(tmp_oldfile1))
        self.assertTrue(os.path.isfile(newfilename))

        os.remove(newfilename)

    def test_adding_tags(self):

        self.assertEqual(self.guess_filename.adding_tags(['foo'], ['bar']), ['foo', 'bar'])
        self.assertEqual(self.guess_filename.adding_tags([], ['bar']), ['bar'])
        self.assertEqual(self.guess_filename.adding_tags(['foo'], ['bar', 'baz']), ['foo', 'bar', 'baz'])
        self.assertEqual(self.guess_filename.adding_tags(['foo'], [42]), ['foo', 42])

    def test_derive_new_filename_from_old_filename(self):

        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("2016-03-05 a1 12,34 €.pdf"),
                          "2016-03-05 A1 Festnetz-Internet 12,34€ -- scan bill.pdf")
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("2016-03-05 A1 12.34 EUR -- finance.pdf"),
                          "2016-03-05 A1 Festnetz-Internet 12.34€ -- finance scan bill.pdf")

        # 2016-01-19--2016-02-12 benutzter GVB 10er Block -- scan transportation graz.pdf
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("2016-03-05 10er.pdf"),
                          "2016-03-05 benutzter GVB 10er Block -- scan transportation graz.pdf")
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("2016-01-19--2016-02-12 10er GVB.pdf"),
                          "2016-01-19--2016-02-12 benutzter GVB 10er Block -- scan transportation graz.pdf")
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("2016-01-19--2016-02-12 10er GVB -- foobar.pdf"),
                          "2016-01-19--2016-02-12 benutzter GVB 10er Block -- foobar scan transportation graz.pdf")
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("2016-01-19 bill foobar baz 12,12EUR.pdf"),
                          "2016-01-19 foobar baz 12,12€ -- scan bill.pdf")
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("2016-03-12 another bill 34,55EUR.pdf"),
                          "2016-03-12 another 34,55€ -- scan bill.pdf")

    def test_contains_one_of(self):

        self.assertTrue(self.guess_filename.contains_one_of("foo bar baz", ['foo']))
        self.assertTrue(self.guess_filename.contains_one_of("foo bar baz", ['foo']))
        self.assertTrue(self.guess_filename.contains_one_of("foo bar baz", ['bar']))
        self.assertTrue(self.guess_filename.contains_one_of("foo bar baz", ['ba']))
        self.assertTrue(self.guess_filename.contains_one_of("foo bar baz", ['x', 'ba', 'yuio']))
        self.assertFalse(self.guess_filename.contains_one_of("foo bar baz", ['xfoo']))
        self.assertFalse(self.guess_filename.contains_one_of("foo bar baz", ['xfoo']))
        self.assertFalse(self.guess_filename.contains_one_of("foo bar baz", ['xbar']))
        self.assertFalse(self.guess_filename.contains_one_of("foo bar baz", ['xba']))
        self.assertFalse(self.guess_filename.contains_one_of("foo bar baz", ['x', 'xba', 'yuio']))

    def test_fuzzy_contains_all_of(self):

        self.assertTrue(self.guess_filename.fuzzy_contains_all_of("foo bar baz", ['foo']))
        self.assertTrue(self.guess_filename.fuzzy_contains_all_of("foo bar baz", ['foo']))
        self.assertTrue(self.guess_filename.fuzzy_contains_all_of("foo bar baz", ['bar']))
        self.assertTrue(self.guess_filename.fuzzy_contains_all_of("foo bar baz", ['ba']))
        self.assertTrue(self.guess_filename.fuzzy_contains_all_of("foo bar baz", ['foo', "bar", "baz"]))
        self.assertFalse(self.guess_filename.fuzzy_contains_all_of("foo bar baz", ['x', 'ba', 'yuio']))
        self.assertTrue(self.guess_filename.fuzzy_contains_all_of("foo bar baz", ['xfoo']))
        self.assertTrue(self.guess_filename.fuzzy_contains_all_of("foo bar baz", ['xfoo']))
        self.assertTrue(self.guess_filename.fuzzy_contains_all_of("foo bar baz", ['xbar']))
        self.assertFalse(self.guess_filename.fuzzy_contains_all_of("foo bar baz", ['xba', "12345"]))
        self.assertFalse(self.guess_filename.fuzzy_contains_all_of("foo bar baz", ['x', 'xba', 'yuio']))
        self.assertTrue(self.guess_filename.fuzzy_contains_all_of("foo\nbar\nbaz42", ['baz42']))
        self.assertTrue(self.guess_filename.fuzzy_contains_all_of("foo€\nbar\nbaz€42", ['baz€42']))

    def test_fuzzy_contains_one_of(self):

        # comparing exact strings:
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of("foo bar baz", ['foo']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of("foo bar baz", ['foo']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of("foo bar baz", ['bar']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of("foo bar baz", ['ba']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of("foo bar baz", ['x', 'ba', 'yuio']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of("Kundennummer 1234567890", ['12345']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of("Kundennummer 1234567890", ['12345']))

        # fuzzy similarities:
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of("foo bar baz", ['xfoo']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of("foo bar baz", ['xfoo']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of("foo bar baz", ['xbar']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of("foo bar baz", ['xba']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of("foo bar baz", ['x', 'xba', 'yuio']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of("Kundennummer 1234567890", ['7234567880']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of("Kundennummer 1234567890", ['Rundemummer 7234567880']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of("Kundennummer 1234567890", ['Rumdemummer  7234567880']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of("Kundennummer 1234567890", ['Rundemummer 1234581388']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of("Kundennummer 1234567890", ['Rumdemummer  1234581388']))

        # fuzzy non-matches:
        self.assertFalse(self.guess_filename.fuzzy_contains_one_of("Kundennummer 1234567890", [' 345 ']))
        self.assertFalse(self.guess_filename.fuzzy_contains_one_of("Kundennummer 1234567890", ['1234581388']))
        self.assertFalse(self.guess_filename.fuzzy_contains_one_of("foo bar baz", ['xyz']))
        self.assertFalse(self.guess_filename.fuzzy_contains_one_of("foo bar baz", ['111']))
        self.assertFalse(self.guess_filename.fuzzy_contains_one_of("foo bar baz", ['xby']))
        self.assertFalse(self.guess_filename.fuzzy_contains_one_of("foo bar baz", ['x', 'yyy', 'yuio']))
        self.assertFalse(self.guess_filename.fuzzy_contains_one_of("Kundennummer 1234567890", ['0987654321']))
        self.assertFalse(self.guess_filename.fuzzy_contains_one_of("Kundennummer 1234567890", ['Rumdemummer  1234555555']))

    def test_has_euro_charge(self):

        self.assertTrue(self.guess_filename.has_euro_charge("12,34EUR"))
        self.assertTrue(self.guess_filename.has_euro_charge("12.34EUR"))
        self.assertTrue(self.guess_filename.has_euro_charge("12,34 EUR"))
        self.assertTrue(self.guess_filename.has_euro_charge("12.34 EUR"))
        self.assertTrue(self.guess_filename.has_euro_charge("foo bar 12,34 EUR baz"))
        self.assertTrue(self.guess_filename.has_euro_charge("foo bar 12.34 EUR baz"))
        self.assertTrue(self.guess_filename.has_euro_charge("foo bar 12 EUR baz"))
        self.assertTrue(self.guess_filename.has_euro_charge("foo bar 12EUR baz"))
        self.assertTrue(self.guess_filename.has_euro_charge("foo bar 12.34 EUR baz.extension"))
        self.assertTrue(self.guess_filename.has_euro_charge("12,34€"))
        self.assertTrue(self.guess_filename.has_euro_charge("12.34€"))
        self.assertTrue(self.guess_filename.has_euro_charge("12,34 €"))
        self.assertTrue(self.guess_filename.has_euro_charge("12.34 €"))
        self.assertTrue(self.guess_filename.has_euro_charge("foo bar 12,34 € baz"))
        self.assertTrue(self.guess_filename.has_euro_charge("foo bar 12.34 € baz"))
        self.assertTrue(self.guess_filename.has_euro_charge("foo bar 12.34 € baz.extension"))
        self.assertTrue(self.guess_filename.has_euro_charge("2016-03-05 A1 12.34 EUR.pdf"))
        self.assertTrue(self.guess_filename.has_euro_charge("2016-03-05 A1 Festnetz-Internet 12.34 € -- scan finance bill.pdf"))
        self.assertFalse(self.guess_filename.has_euro_charge("1234"))
        self.assertFalse(self.guess_filename.has_euro_charge("foo bar baz"))
        self.assertFalse(self.guess_filename.has_euro_charge("1234eur"))
        self.assertFalse(self.guess_filename.has_euro_charge("foo 12 bar"))
        self.assertFalse(self.guess_filename.has_euro_charge("foo 1234 bar"))
        self.assertFalse(self.guess_filename.has_euro_charge("foo 12,34 bar"))
        self.assertFalse(self.guess_filename.has_euro_charge("foo 12.34 bar"))

    def test_get_euro_charge_from_context(self):

        self.assertEqual(self.guess_filename.get_euro_charge_from_context("xyz foo12,34EURbar xyz", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo12,34EURbar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo12.34EURbar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo12,34€bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo12.34€bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("fooEUR12,34bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("fooEUR12.34bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo€12,34bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo€12.34bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo 12,34EUR bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo 12.34EUR bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo 12,34€ bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo 12.34€ bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo 12,34 EUR bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo 12.34 EUR bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo 12,34 € bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo 12.34 € bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo EUR 12,34 bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo EUR 12.34 bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo € 12,34 bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo € 12.34 bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo 12,34 bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo 12.34 bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo ba  12,34  ba bar", "foo", "bar"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("foo xxx 12.34 xxx bar", "foo", "bar"), "12,34")
        self.assertFalse(self.guess_filename.get_euro_charge_from_context("foo xxxx 12.34 xxxx bar", "foo", "bar"))
        self.assertEqual(self.guess_filename.get_euro_charge_from_context("DasinsteinTest2015:EURJahresbeitrag123,45Offen678,90Zahlungenbis03.11.2015sindber",
                                                                           "Offen", "Zahlungen"), "678,90")


    def test_get_euro_charge(self):

        self.assertEqual(self.guess_filename.get_euro_charge("12,34EUR"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge("12.34EUR"), "12.34")
        self.assertEqual(self.guess_filename.get_euro_charge("12,34 EUR"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge("12.34 EUR"), "12.34")
        self.assertEqual(self.guess_filename.get_euro_charge("foo bar 12,34 EUR baz"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge("foo bar 12.34 EUR baz"), "12.34")
        self.assertEqual(self.guess_filename.get_euro_charge("foo bar 12 EUR baz"), "12")
        self.assertEqual(self.guess_filename.get_euro_charge("foo bar 12EUR baz"), "12")
        self.assertEqual(self.guess_filename.get_euro_charge("foo bar 12.34 EUR baz.extension"), "12.34")
        self.assertEqual(self.guess_filename.get_euro_charge("12,34€"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge("12.34€"), "12.34")
        self.assertEqual(self.guess_filename.get_euro_charge("12,34 €"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge("12.34 €"), "12.34")
        self.assertEqual(self.guess_filename.get_euro_charge("foo bar 12,34 € baz"), "12,34")
        self.assertEqual(self.guess_filename.get_euro_charge("foo bar 12.34 € baz"), "12.34")
        self.assertEqual(self.guess_filename.get_euro_charge("foo bar 12.34 € baz.extension"), "12.34")
        self.assertFalse(self.guess_filename.get_euro_charge("1234"))
        self.assertFalse(self.guess_filename.get_euro_charge("foo bar baz"))
        self.assertFalse(self.guess_filename.get_euro_charge("1234eur"))
        self.assertFalse(self.guess_filename.get_euro_charge("foo 12 bar"))
        self.assertFalse(self.guess_filename.get_euro_charge("foo 1234 bar"))
        self.assertFalse(self.guess_filename.get_euro_charge("foo 12,34 bar"))
        self.assertFalse(self.guess_filename.get_euro_charge("foo 12.34 bar"))

    def test_split_filename_entities(self):

        self.assertEqual(self.guess_filename.split_filename_entities("2016-03-05T23.59.42--2017-04-06T12.13.14 foo bar -- eins zwei.extension"),
                         ("2016-03-05T23.59.42--2017-04-06T12.13.14", "foo bar", ["eins", "zwei"], "extension"))
        self.assertEqual(self.guess_filename.split_filename_entities("2016-03-05T23.59.42-2017-04-06T12.13.14 foo bar -- eins zwei.extension"),
                         ("2016-03-05T23.59.42-2017-04-06T12.13.14", "foo bar", ["eins", "zwei"], "extension"))
        self.assertEqual(self.guess_filename.split_filename_entities("2016-03-05T23.59--2017-04-06T12.13 foo - bar.baz - zum -- eins zwei.extension"),
                         ("2016-03-05T23.59--2017-04-06T12.13", "foo - bar.baz - zum", ["eins", "zwei"], "extension"))
        self.assertEqual(self.guess_filename.split_filename_entities("2016-03-05T23.59.42 foo - bar.baz - zum -- eins zwei.extension"),
                         ("2016-03-05T23.59.42", "foo - bar.baz - zum", ["eins", "zwei"], "extension"))
        self.assertEqual(self.guess_filename.split_filename_entities("2016-03-05T23.59.42 foo bar -- eins zwei.extension"),
                         ("2016-03-05T23.59.42", "foo bar", ["eins", "zwei"], "extension"))
        self.assertEqual(self.guess_filename.split_filename_entities("2016-03-05T23.59--2017-04-06T12.13 foo bar -- eins zwei.extension"),
                         ("2016-03-05T23.59--2017-04-06T12.13", "foo bar", ["eins", "zwei"], "extension"))
        self.assertEqual(self.guess_filename.split_filename_entities("2016-03-05T23.59--2017-04-06T12.13 foo bar.extension"),
                         ("2016-03-05T23.59--2017-04-06T12.13", "foo bar", [], "extension"))
        self.assertEqual(self.guess_filename.split_filename_entities("2016-03-05T23.59 foo bar.extension"),
                         ("2016-03-05T23.59", "foo bar", [], "extension"))
        self.assertEqual(self.guess_filename.split_filename_entities("foo bar.extension"),
                         (None, "foo bar", [], "extension"))
        self.assertEqual(self.guess_filename.split_filename_entities("foo bar"),
                         (None, "foo bar", [], None))
        self.assertEqual(self.guess_filename.split_filename_entities("foo.bar"),
                         (None, "foo", [], "bar"))
        self.assertEqual(self.guess_filename.split_filename_entities("foo -- bar"),
                         (None, "foo", ["bar"], None))
        self.assertEqual(self.guess_filename.split_filename_entities("foo -- bar.baz"),
                         (None, "foo", ["bar"], "baz"))
        self.assertEqual(self.guess_filename.split_filename_entities(" -- "),
                         (None, ' -- ', [], None))
        self.assertEqual(self.guess_filename.split_filename_entities("."),
                         (None, '.', [], None))

# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
