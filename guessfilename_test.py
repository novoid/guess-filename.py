#!/usr/bin/env python
# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2016-03-06 12:28:12 vk>

import unittest
from guessfilename import GuessFilename

class TestGuessFilename(unittest.TestCase):

    logging = None
    guess_filename = None

    def setUp(self):
        verbose = True
        quiet = False
        self.guess_filename = GuessFilename()
        self.guess_filename.verbose = verbose

    def tearDown(self):
        pass

    def test_adding_tags(self):

        self.assertEquals(self.guess_filename.adding_tags(['foo'], ['bar']), ['foo', 'bar'])

    def test_derive_new_filename_from_old_filename(self):

        self.assertEquals(self.guess_filename.derive_new_filename_from_old_filename(u"2016-03-05 a1 12,34 €.pdf"),
                          u"2016-03-05 A1 Festnetz-Internet 12,34 € -- scan finance bill.pdf")
        self.assertEquals(self.guess_filename.derive_new_filename_from_old_filename(u"2016-03-05 A1 12.34 EUR.pdf"),
                          u"2016-03-05 A1 Festnetz-Internet 12.34 € -- scan finance bill.pdf")

    def test_contains_one_of(self):

        self.assertTrue(self.guess_filename.contains_one_of(u"foo bar baz", ['foo']))
        self.assertTrue(self.guess_filename.contains_one_of(u"foo bar baz", [u'foo']))
        self.assertTrue(self.guess_filename.contains_one_of(u"foo bar baz", [u'bar']))
        self.assertTrue(self.guess_filename.contains_one_of(u"foo bar baz", [u'ba']))
        self.assertTrue(self.guess_filename.contains_one_of(u"foo bar baz", [u'x', u'ba', u'yuio']))
        self.assertFalse(self.guess_filename.contains_one_of(u"foo bar baz", ['xfoo']))
        self.assertFalse(self.guess_filename.contains_one_of(u"foo bar baz", [u'xfoo']))
        self.assertFalse(self.guess_filename.contains_one_of(u"foo bar baz", [u'xbar']))
        self.assertFalse(self.guess_filename.contains_one_of(u"foo bar baz", [u'xba']))
        self.assertFalse(self.guess_filename.contains_one_of(u"foo bar baz", [u'x', u'xba', u'yuio']))

    def test_fuzzy_contains_one_of(self):

        ## comparing exact strings:
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of(u"foo bar baz", ['foo']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of(u"foo bar baz", [u'foo']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of(u"foo bar baz", [u'bar']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of(u"foo bar baz", [u'ba']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of(u"foo bar baz", [u'x', u'ba', u'yuio']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of(u"Kundennummer 1234567890", [u'12345']))

        ## fuzzy similarities:
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of(u"foo bar baz", ['xfoo']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of(u"foo bar baz", [u'xfoo']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of(u"foo bar baz", [u'xbar']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of(u"foo bar baz", [u'xba']))
        self.assertTrue(self.guess_filename.fuzzy_contains_one_of(u"foo bar baz", [u'x', u'xba', u'yuio']))
        #self.assertTrue(self.guess_filename.fuzzy_contains_one_of(u"Kundennummer 1234567890", [u'1234581388']))
        #self.assertTrue(self.guess_filename.fuzzy_contains_one_of(u"Rundemummer 1234567890", [u'Rundemummer 1234581388']))
        #self.assertTrue(self.guess_filename.fuzzy_contains_one_of(u"Rundemummer 1234567890", [u'Rumdemummer  1234581388']))

        ## fuzzy non-matches:
        self.assertFalse(self.guess_filename.fuzzy_contains_one_of(u"foo bar baz", [u'xyz']))
        self.assertFalse(self.guess_filename.fuzzy_contains_one_of(u"foo bar baz", [u'111']))
        self.assertFalse(self.guess_filename.fuzzy_contains_one_of(u"foo bar baz", [u'xby']))
        self.assertFalse(self.guess_filename.fuzzy_contains_one_of(u"foo bar baz", [u'x', u'yyy', u'yuio']))
        #self.assertFalse(self.guess_filename.fuzzy_contains_one_of(u"Kundennummer 1234567890", [u'12345', u' 345 ', u'0987654321']))
        #self.assertFalse(self.guess_filename.fuzzy_contains_one_of(u"Kundennummer 1234567890", [u'12345']))

    def test_has_euro_charge(self):

        self.assertTrue(self.guess_filename.has_euro_charge(u"12,34EUR"))
        self.assertTrue(self.guess_filename.has_euro_charge(u"12.34EUR"))
        self.assertTrue(self.guess_filename.has_euro_charge(u"12,34 EUR"))
        self.assertTrue(self.guess_filename.has_euro_charge(u"12.34 EUR"))
        self.assertTrue(self.guess_filename.has_euro_charge(u"foo bar 12,34 EUR baz"))
        self.assertTrue(self.guess_filename.has_euro_charge(u"foo bar 12.34 EUR baz"))
        self.assertTrue(self.guess_filename.has_euro_charge(u"foo bar 12 EUR baz"))
        self.assertTrue(self.guess_filename.has_euro_charge(u"foo bar 12EUR baz"))
        self.assertTrue(self.guess_filename.has_euro_charge(u"foo bar 12.34 EUR baz.extension"))
        self.assertTrue(self.guess_filename.has_euro_charge(u"12,34€"))
        self.assertTrue(self.guess_filename.has_euro_charge(u"12.34€"))
        self.assertTrue(self.guess_filename.has_euro_charge(u"12,34 €"))
        self.assertTrue(self.guess_filename.has_euro_charge(u"12.34 €"))
        self.assertTrue(self.guess_filename.has_euro_charge(u"foo bar 12,34 € baz"))
        self.assertTrue(self.guess_filename.has_euro_charge(u"foo bar 12.34 € baz"))
        self.assertTrue(self.guess_filename.has_euro_charge(u"foo bar 12.34 € baz.extension"))
        self.assertTrue(self.guess_filename.has_euro_charge(u"2016-03-05 A1 12.34 EUR.pdf"))
        self.assertTrue(self.guess_filename.has_euro_charge(u"2016-03-05 A1 Festnetz-Internet 12.34 € -- scan finance bill.pdf"))
        self.assertFalse(self.guess_filename.has_euro_charge(u"1234"))
        self.assertFalse(self.guess_filename.has_euro_charge(u"foo bar baz"))
        self.assertFalse(self.guess_filename.has_euro_charge(u"1234eur"))
        self.assertFalse(self.guess_filename.has_euro_charge(u"foo 12 bar"))
        self.assertFalse(self.guess_filename.has_euro_charge(u"foo 1234 bar"))
        self.assertFalse(self.guess_filename.has_euro_charge(u"foo 12,34 bar"))
        self.assertFalse(self.guess_filename.has_euro_charge(u"foo 12.34 bar"))

    def test_get_euro_charge(self):

        self.assertEquals(self.guess_filename.get_euro_charge(u"12,34EUR"), "12,34")
        self.assertEquals(self.guess_filename.get_euro_charge(u"12.34EUR"), "12.34")
        self.assertEquals(self.guess_filename.get_euro_charge(u"12,34 EUR"), "12,34")
        self.assertEquals(self.guess_filename.get_euro_charge(u"12.34 EUR"), "12.34")
        self.assertEquals(self.guess_filename.get_euro_charge(u"foo bar 12,34 EUR baz"), "12,34")
        self.assertEquals(self.guess_filename.get_euro_charge(u"foo bar 12.34 EUR baz"), "12.34")
        self.assertEquals(self.guess_filename.get_euro_charge(u"foo bar 12 EUR baz"), "12")
        self.assertEquals(self.guess_filename.get_euro_charge(u"foo bar 12EUR baz"), "12")
        self.assertEquals(self.guess_filename.get_euro_charge(u"foo bar 12.34 EUR baz.extension"), "12.34")
        self.assertEquals(self.guess_filename.get_euro_charge(u"12,34€"), "12,34")
        self.assertEquals(self.guess_filename.get_euro_charge(u"12.34€"), "12.34")
        self.assertEquals(self.guess_filename.get_euro_charge(u"12,34 €"), "12,34")
        self.assertEquals(self.guess_filename.get_euro_charge(u"12.34 €"), "12.34")
        self.assertEquals(self.guess_filename.get_euro_charge(u"foo bar 12,34 € baz"), "12,34")
        self.assertEquals(self.guess_filename.get_euro_charge(u"foo bar 12.34 € baz"), "12.34")
        self.assertEquals(self.guess_filename.get_euro_charge(u"foo bar 12.34 € baz.extension"), "12.34")
        self.assertFalse(self.guess_filename.get_euro_charge(u"1234"))
        self.assertFalse(self.guess_filename.get_euro_charge(u"foo bar baz"))
        self.assertFalse(self.guess_filename.get_euro_charge(u"1234eur"))
        self.assertFalse(self.guess_filename.get_euro_charge(u"foo 12 bar"))
        self.assertFalse(self.guess_filename.get_euro_charge(u"foo 1234 bar"))
        self.assertFalse(self.guess_filename.get_euro_charge(u"foo 12,34 bar"))
        self.assertFalse(self.guess_filename.get_euro_charge(u"foo 12.34 bar"))

    def test_split_filename_entities(self):

        self.assertEqual(self.guess_filename.split_filename_entities(u"2016-03-05T23.59.42--2017-04-06T12.13.14 foo bar -- eins zwei.extension"),
                         (u"2016-03-05T23.59.42--2017-04-06T12.13.14", u"foo bar", [u"eins", u"zwei"], u"extension"))
        self.assertEqual(self.guess_filename.split_filename_entities(u"2016-03-05T23.59.42-2017-04-06T12.13.14 foo bar -- eins zwei.extension"),
                         (u"2016-03-05T23.59.42-2017-04-06T12.13.14", u"foo bar", [u"eins", u"zwei"], u"extension"))
        self.assertEqual(self.guess_filename.split_filename_entities(u"2016-03-05T23.59--2017-04-06T12.13 foo - bar.baz - zum -- eins zwei.extension"),
                         (u"2016-03-05T23.59--2017-04-06T12.13", u"foo - bar.baz - zum", [u"eins", u"zwei"], u"extension"))
        self.assertEqual(self.guess_filename.split_filename_entities(u"2016-03-05T23.59.42 foo - bar.baz - zum -- eins zwei.extension"),
                         (u"2016-03-05T23.59.42", u"foo - bar.baz - zum", [u"eins", u"zwei"], u"extension"))
        self.assertEqual(self.guess_filename.split_filename_entities(u"2016-03-05T23.59.42 foo bar -- eins zwei.extension"),
                         (u"2016-03-05T23.59.42", u"foo bar", [u"eins", u"zwei"], u"extension"))
        self.assertEqual(self.guess_filename.split_filename_entities(u"2016-03-05T23.59--2017-04-06T12.13 foo bar -- eins zwei.extension"),
                         (u"2016-03-05T23.59--2017-04-06T12.13", u"foo bar", [u"eins", u"zwei"], u"extension"))
        self.assertEqual(self.guess_filename.split_filename_entities(u"2016-03-05T23.59--2017-04-06T12.13 foo bar.extension"),
                         (u"2016-03-05T23.59--2017-04-06T12.13", u"foo bar", [], u"extension"))
        self.assertEqual(self.guess_filename.split_filename_entities(u"2016-03-05T23.59 foo bar.extension"),
                         (u"2016-03-05T23.59", u"foo bar", [], u"extension"))
        self.assertEqual(self.guess_filename.split_filename_entities(u"foo bar.extension"),
                         (None, u"foo bar", [], u"extension"))
        self.assertEqual(self.guess_filename.split_filename_entities(u"foo bar"),
                         (None, u"foo bar", [], None))
        self.assertEqual(self.guess_filename.split_filename_entities(u"foo.bar"),
                         (None, u"foo", [], u"bar"))
        self.assertEqual(self.guess_filename.split_filename_entities(u"foo -- bar"),
                         (None, u"foo", [u"bar"], None))
        self.assertEqual(self.guess_filename.split_filename_entities(u"foo -- bar.baz"),
                         (None, u"foo", [u"bar"], u"baz"))
        self.assertEqual(self.guess_filename.split_filename_entities(u" -- "),
                         (None, u' -- ', [], None))
        self.assertEqual(self.guess_filename.split_filename_entities(u"."),
                         (None, u'.', [], None))



# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
