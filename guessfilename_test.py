#!/usr/bin/env python
# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2016-03-05 14:41:50 vk>

import unittest
from guessfilename import GuessFilename

class TestGuessFilename(unittest.TestCase):

    logging = None
    guess_filename = GuessFilename()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_str_contains_euro_charge(self):

        self.assertTrue(self.guess_filename.str_contains_euro_charge(u"12,34EUR"))
        self.assertTrue(self.guess_filename.str_contains_euro_charge(u"12.34EUR"))
        self.assertTrue(self.guess_filename.str_contains_euro_charge(u"12,34 EUR"))
        self.assertTrue(self.guess_filename.str_contains_euro_charge(u"12.34 EUR"))
        self.assertTrue(self.guess_filename.str_contains_euro_charge(u"foo bar 12,34 EUR baz"))
        self.assertTrue(self.guess_filename.str_contains_euro_charge(u"foo bar 12.34 EUR baz"))
        self.assertTrue(self.guess_filename.str_contains_euro_charge(u"foo bar 12 EUR baz"))
        self.assertTrue(self.guess_filename.str_contains_euro_charge(u"foo bar 12EUR baz"))
        self.assertTrue(self.guess_filename.str_contains_euro_charge(u"foo bar 12.34 EUR baz.extension"))
        self.assertTrue(self.guess_filename.str_contains_euro_charge(u"12,34€"))
        self.assertTrue(self.guess_filename.str_contains_euro_charge(u"12.34€"))
        self.assertTrue(self.guess_filename.str_contains_euro_charge(u"12,34 €"))
        self.assertTrue(self.guess_filename.str_contains_euro_charge(u"12.34 €"))
        self.assertTrue(self.guess_filename.str_contains_euro_charge(u"foo bar 12,34 € baz"))
        self.assertTrue(self.guess_filename.str_contains_euro_charge(u"foo bar 12.34 € baz"))
        self.assertTrue(self.guess_filename.str_contains_euro_charge(u"foo bar 12.34 € baz.extension"))
        self.assertFalse(self.guess_filename.str_contains_euro_charge(u"1234"))
        self.assertFalse(self.guess_filename.str_contains_euro_charge(u"foo bar baz"))
        self.assertFalse(self.guess_filename.str_contains_euro_charge(u"1234eur"))
        self.assertFalse(self.guess_filename.str_contains_euro_charge(u"foo 12 bar"))
        self.assertFalse(self.guess_filename.str_contains_euro_charge(u"foo 1234 bar"))
        self.assertFalse(self.guess_filename.str_contains_euro_charge(u"foo 12,34 bar"))
        self.assertFalse(self.guess_filename.str_contains_euro_charge(u"foo 12.34 bar"))

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
