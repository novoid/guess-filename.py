#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2020-02-29 11:47:58 vk>

import unittest
import logging
import tempfile
import os
import os.path
import sys
import re
from guessfilename import GuessFilename
from guessfilename import FileSizePlausibilityException


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

    def test_youtube_json_metadata(self):

        tmpdir=tempfile.mkdtemp()
        mediafile=tempfile.mkstemp(dir=tmpdir, prefix='The Star7 PDA Prototype-', suffix='.mp4')[1]
        jsonfile=os.path.join(os.path.dirname(mediafile), os.path.splitext(mediafile)[0] + '.info.json')

        with open(mediafile, 'w') as outputhandle:
            outputhandle.write('This is not of any interest. Delete me.')

        with open(jsonfile, 'w') as outputhandle:
            outputhandle.write("""{
  "upload_date": "20070913",
  "playlist": null,
  "age_limit": 0,
  "http_headers": {
    "Accept-Language": "en-us,en;q=0.5",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.57 Safari/537.36",
    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7"
  },
  "format_id": "18",
  "automatic_captions": null,
  "duration": 591,
  "subtitles": null,
  "tags": [
    "java",
    "oak",
    "star7",
    "*7",
    "green",
    "project",
    "sun",
    "james",
    "gosling",
    "duke"
  ],
  "uploader_url": "http://www.youtube.com/user/enaiel",
  "average_rating": 4.9502072,
  "categories": [
    "Howto & Style"
  ],
  "url": "https://r2---sn-uigxx50n-8pxk.googlevideo.com/videoplayback?expire=1571352127&ei=35moXcuGLdqZ1gK7zqeACw&ip=178.115.128.175&id=o-AHlmX6ewQ0oGkLxHaBex7a7LhrxFyL7ROERRi9UiIYW6&itag=18&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-uigxx50n-8pxk%2Csn-c0q7lnly&ms=au%2Crdu&mv=m&mvi=1&pl=20&initcwndbps=771250&mime=video%2Fmp4&gir=yes&clen=26294671&ratebypass=yes&dur=591.458&lmt=1415795880482368&mt=1571330440&fvip=5&fexp=23842630&c=WEB&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cratebypass%2Cdur%2Clmt&sig=ALgxI2wwRAIgY-EEHBbMKgL3IOtT574RJJNPZRQgYw3gZb682o8-TfQCIEwAsWs8FjYXX8mBZR_wRZlgz1XcGlfN1LCoVbYmhNu_&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRgIhANqY0o3uYDdDP-Ayajc9sWOgDH-9SUVNft9S78aFM3YqAiEA0MTAGAhSuXCGMun6oKkwCBnQ5r5sVLBK1MvH6Cr-gVs%3D",
  "thumbnail": "https://i.ytimg.com/vi/Ahg8OBYixL0/hqdefault.jpg",
  "extractor": "youtube",
  "season_number": null,
  "track": null,
  "height": 262,
  "series": null,
  "uploader": "Enaiel",
  "like_count": 238,
  "artist": null,
  "protocol": "https",
  "playlist_index": null,
  "release_date": null,
  "end_time": null,
  "formats": [
    {
      "height": null,
      "filesize": 3121140,
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.57 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-us,en;q=0.5"
      },
      "format_id": "249",
      "vcodec": "none",
      "protocol": "https",
      "ext": "webm",
      "downloader_options": {
        "http_chunk_size": 10485760
      },
      "acodec": "opus",
      "format": "249 - audio only (tiny)",
      "format_note": "tiny",
      "tbr": 64.949,
      "fps": null,
      "player_url": null,
      "url": "https://r2---sn-uigxx50n-8pxk.googlevideo.com/videoplayback?expire=1571352127&ei=35moXcuGLdqZ1gK7zqeACw&ip=178.115.128.175&id=o-AHlmX6ewQ0oGkLxHaBex7a7LhrxFyL7ROERRi9UiIYW6&itag=249&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-uigxx50n-8pxk%2Csn-c0q7lnly&ms=au%2Crdu&mv=m&mvi=1&pl=20&initcwndbps=771250&mime=audio%2Fwebm&gir=yes&clen=3121140&dur=591.401&lmt=1507622941749296&mt=1571330440&fvip=5&keepalive=yes&fexp=23842630&c=WEB&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRAIgMEEY1cSicYKiXxBGisCl6HTs8BqyAM7BADcrxSbs8GECIEDuTMg-dFUTZmXxV-wtIO4yrVNBGO2rwvJGg-g0cEP6&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRgIhANqY0o3uYDdDP-Ayajc9sWOgDH-9SUVNft9S78aFM3YqAiEA0MTAGAhSuXCGMun6oKkwCBnQ5r5sVLBK1MvH6Cr-gVs%3D&ratebypass=yes",
      "abr": 50,
      "asr": 48000,
      "width": null
    },
    {
      "height": null,
      "filesize": 3854861,
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.57 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-us,en;q=0.5"
      },
      "format_id": "250",
      "vcodec": "none",
      "protocol": "https",
      "ext": "webm",
      "downloader_options": {
        "http_chunk_size": 10485760
      },
      "acodec": "opus",
      "format": "250 - audio only (tiny)",
      "format_note": "tiny",
      "tbr": 76.443,
      "fps": null,
      "player_url": null,
      "url": "https://r2---sn-uigxx50n-8pxk.googlevideo.com/videoplayback?expire=1571352127&ei=35moXcuGLdqZ1gK7zqeACw&ip=178.115.128.175&id=o-AHlmX6ewQ0oGkLxHaBex7a7LhrxFyL7ROERRi9UiIYW6&itag=250&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-uigxx50n-8pxk%2Csn-c0q7lnly&ms=au%2Crdu&mv=m&mvi=1&pl=20&initcwndbps=771250&mime=audio%2Fwebm&gir=yes&clen=3854861&dur=591.401&lmt=1507622945308441&mt=1571330440&fvip=5&keepalive=yes&fexp=23842630&c=WEB&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRQIhALgR6NH1IAZwIk3MzFeJs5MSEtPXQ6ptzfS_c0-CowKbAiAWdGAB9JFCwtL39n8ee8AO_2atOlJyKU0W_9Tt1OENjA%3D%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRgIhANqY0o3uYDdDP-Ayajc9sWOgDH-9SUVNft9S78aFM3YqAiEA0MTAGAhSuXCGMun6oKkwCBnQ5r5sVLBK1MvH6Cr-gVs%3D&ratebypass=yes",
      "abr": 70,
      "asr": 48000,
      "width": null
    },
    {
      "height": null,
      "filesize": 7065084,
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.57 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-us,en;q=0.5"
      },
      "format_id": "251",
      "vcodec": "none",
      "protocol": "https",
      "ext": "webm",
      "downloader_options": {
        "http_chunk_size": 10485760
      },
      "acodec": "opus",
      "format": "251 - audio only (tiny)",
      "format_note": "tiny",
      "tbr": 124.188,
      "fps": null,
      "player_url": null,
      "url": "https://r2---sn-uigxx50n-8pxk.googlevideo.com/videoplayback?expire=1571352127&ei=35moXcuGLdqZ1gK7zqeACw&ip=178.115.128.175&id=o-AHlmX6ewQ0oGkLxHaBex7a7LhrxFyL7ROERRi9UiIYW6&itag=251&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-uigxx50n-8pxk%2Csn-c0q7lnly&ms=au%2Crdu&mv=m&mvi=1&pl=20&initcwndbps=771250&mime=audio%2Fwebm&gir=yes&clen=7065084&dur=591.401&lmt=1507622947971155&mt=1571330440&fvip=5&keepalive=yes&fexp=23842630&c=WEB&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRQIgB4hAT4pF8aI6rI2q84eGG3IF2fIdO806JuGkv7ax8LACIQC7avZujeiNtmRZDEIzAWelxzJLYWqC75Gzik0Yhyjcrw%3D%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRgIhANqY0o3uYDdDP-Ayajc9sWOgDH-9SUVNft9S78aFM3YqAiEA0MTAGAhSuXCGMun6oKkwCBnQ5r5sVLBK1MvH6Cr-gVs%3D&ratebypass=yes",
      "abr": 160,
      "asr": 48000,
      "width": null
    },
    {
      "height": null,
      "filesize": 9495914,
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.57 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-us,en;q=0.5"
      },
      "format_id": "140",
      "container": "m4a_dash",
      "protocol": "https",
      "ext": "m4a",
      "downloader_options": {
        "http_chunk_size": 10485760
      },
      "acodec": "mp4a.40.2",
      "format": "140 - audio only (tiny)",
      "format_note": "tiny",
      "vcodec": "none",
      "tbr": 129.672,
      "fps": null,
      "player_url": null,
      "url": "https://r2---sn-uigxx50n-8pxk.googlevideo.com/videoplayback?expire=1571352127&ei=35moXcuGLdqZ1gK7zqeACw&ip=178.115.128.175&id=o-AHlmX6ewQ0oGkLxHaBex7a7LhrxFyL7ROERRi9UiIYW6&itag=140&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-uigxx50n-8pxk%2Csn-c0q7lnly&ms=au%2Crdu&mv=m&mvi=1&pl=20&initcwndbps=771250&mime=audio%2Fmp4&gir=yes&clen=9495914&dur=591.458&lmt=1415795872140674&mt=1571330440&fvip=5&keepalive=yes&fexp=23842630&c=WEB&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRAIgVEvtk7Bvo-dTP-QHZ90r12NYpLMnM7Ps1qp9PL563XMCIFoG5qllYYr_4l2CxVyMN_dtwsWv_HWbyrOk9kUUrdbh&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRgIhANqY0o3uYDdDP-Ayajc9sWOgDH-9SUVNft9S78aFM3YqAiEA0MTAGAhSuXCGMun6oKkwCBnQ5r5sVLBK1MvH6Cr-gVs%3D&ratebypass=yes",
      "abr": 128,
      "asr": 44100,
      "width": null
    },
    {
      "height": 144,
      "filesize": 5187560,
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.57 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-us,en;q=0.5"
      },
      "format_id": "278",
      "container": "webm",
      "protocol": "https",
      "ext": "webm",
      "format": "278 - 194x144 (144p)",
      "fps": 30,
      "format_note": "144p",
      "tbr": 74.487,
      "acodec": "none",
      "downloader_options": {
        "http_chunk_size": 10485760
      },
      "player_url": null,
      "url": "https://r2---sn-uigxx50n-8pxk.googlevideo.com/videoplayback?expire=1571352127&ei=35moXcuGLdqZ1gK7zqeACw&ip=178.115.128.175&id=o-AHlmX6ewQ0oGkLxHaBex7a7LhrxFyL7ROERRi9UiIYW6&itag=278&aitags=133%2C160%2C242%2C278&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-uigxx50n-8pxk%2Csn-c0q7lnly&ms=au%2Crdu&mv=m&mvi=1&pl=20&initcwndbps=771250&mime=video%2Fwebm&gir=yes&clen=5187560&dur=591.367&lmt=1507623061784408&mt=1571330440&fvip=5&keepalive=yes&fexp=23842630&c=WEB&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRQIhAJGGF4cFF2qnvAjtO4lmJMkhlqR2UKzPUqbwaEv8rFsCAiBkiVT6XPHfxCbkyopAh4AiEPc9JtY5hbHtRuRBDnTvrA%3D%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRgIhANqY0o3uYDdDP-Ayajc9sWOgDH-9SUVNft9S78aFM3YqAiEA0MTAGAhSuXCGMun6oKkwCBnQ5r5sVLBK1MvH6Cr-gVs%3D&ratebypass=yes",
      "width": 194,
      "asr": null,
      "vcodec": "vp9"
    },
    {
      "height": 144,
      "filesize": 7913960,
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.57 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-us,en;q=0.5"
      },
      "format_id": "160",
      "protocol": "https",
      "ext": "mp4",
      "format": "160 - 194x144 (144p)",
      "fps": 15,
      "format_note": "144p",
      "tbr": 113.723,
      "acodec": "none",
      "downloader_options": {
        "http_chunk_size": 10485760
      },
      "player_url": null,
      "url": "https://r2---sn-uigxx50n-8pxk.googlevideo.com/videoplayback?expire=1571352127&ei=35moXcuGLdqZ1gK7zqeACw&ip=178.115.128.175&id=o-AHlmX6ewQ0oGkLxHaBex7a7LhrxFyL7ROERRi9UiIYW6&itag=160&aitags=133%2C160%2C242%2C278&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-uigxx50n-8pxk%2Csn-c0q7lnly&ms=au%2Crdu&mv=m&mvi=1&pl=20&initcwndbps=771250&mime=video%2Fmp4&gir=yes&clen=7913960&dur=591.400&lmt=1415795873455728&mt=1571330440&fvip=5&keepalive=yes&fexp=23842630&c=WEB&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRQIhAIDs6R7ItsH5lM25V_dqN_yYFm_5mAc2gF6U_awc9sXxAiBu5Jrir1bgSXMsC7ZrnhpMJCts8PE0V9qcDrzySgMTpg%3D%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRgIhANqY0o3uYDdDP-Ayajc9sWOgDH-9SUVNft9S78aFM3YqAiEA0MTAGAhSuXCGMun6oKkwCBnQ5r5sVLBK1MvH6Cr-gVs%3D&ratebypass=yes",
      "width": 194,
      "asr": null,
      "vcodec": "avc1.4d400c"
    },
    {
      "height": 240,
      "filesize": 8734238,
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.57 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-us,en;q=0.5"
      },
      "format_id": "242",
      "protocol": "https",
      "ext": "webm",
      "format": "242 - 322x240 (240p)",
      "fps": 30,
      "format_note": "240p",
      "tbr": 169.449,
      "acodec": "none",
      "downloader_options": {
        "http_chunk_size": 10485760
      },
      "player_url": null,
      "url": "https://r2---sn-uigxx50n-8pxk.googlevideo.com/videoplayback?expire=1571352127&ei=35moXcuGLdqZ1gK7zqeACw&ip=178.115.128.175&id=o-AHlmX6ewQ0oGkLxHaBex7a7LhrxFyL7ROERRi9UiIYW6&itag=242&aitags=133%2C160%2C242%2C278&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-uigxx50n-8pxk%2Csn-c0q7lnly&ms=au%2Crdu&mv=m&mvi=1&pl=20&initcwndbps=771250&mime=video%2Fwebm&gir=yes&clen=8734238&dur=591.367&lmt=1507623061440828&mt=1571330440&fvip=5&keepalive=yes&fexp=23842630&c=WEB&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRQIhAN7D8OkjklXr0AO_F1An8alz2mpJgys08pbtmrSePhD0AiBY_8JuGPizqdr70zqijdcmYS-NLWwDBAuQWcJxQrixLg%3D%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRgIhANqY0o3uYDdDP-Ayajc9sWOgDH-9SUVNft9S78aFM3YqAiEA0MTAGAhSuXCGMun6oKkwCBnQ5r5sVLBK1MvH6Cr-gVs%3D&ratebypass=yes",
      "width": 322,
      "asr": null,
      "vcodec": "vp9"
    },
    {
      "height": 240,
      "filesize": 18043410,
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.57 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-us,en;q=0.5"
      },
      "format_id": "133",
      "protocol": "https",
      "ext": "mp4",
      "format": "133 - 322x240 (240p)",
      "fps": 30,
      "format_note": "240p",
      "tbr": 247.387,
      "acodec": "none",
      "downloader_options": {
        "http_chunk_size": 10485760
      },
      "player_url": null,
      "url": "https://r2---sn-uigxx50n-8pxk.googlevideo.com/videoplayback?expire=1571352127&ei=35moXcuGLdqZ1gK7zqeACw&ip=178.115.128.175&id=o-AHlmX6ewQ0oGkLxHaBex7a7LhrxFyL7ROERRi9UiIYW6&itag=133&aitags=133%2C160%2C242%2C278&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-uigxx50n-8pxk%2Csn-c0q7lnly&ms=au%2Crdu&mv=m&mvi=1&pl=20&initcwndbps=771250&mime=video%2Fmp4&gir=yes&clen=18043410&dur=591.366&lmt=1415795874677447&mt=1571330440&fvip=5&keepalive=yes&fexp=23842630&c=WEB&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRQIgAmTNtcaK6cOtqjOHHPNlg3h-dPT-iDBQpCnvAVxEv2gCIQCUOw-KYpMdg2d3Xv1hEC8GMZpu1jDAXvxarBKTgmgJKQ%3D%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRgIhANqY0o3uYDdDP-Ayajc9sWOgDH-9SUVNft9S78aFM3YqAiEA0MTAGAhSuXCGMun6oKkwCBnQ5r5sVLBK1MvH6Cr-gVs%3D&ratebypass=yes",
      "width": 322,
      "asr": null,
      "vcodec": "avc1.4d400d"
    },
    {
      "height": 360,
      "filesize": 21700774,
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.57 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-us,en;q=0.5"
      },
      "format_id": "43",
      "protocol": "https",
      "ext": "webm",
      "tbr": null,
      "format": "43 - 640x360 (360p)",
      "acodec": "vorbis",
      "format_note": "360p",
      "width": 640,
      "fps": null,
      "player_url": null,
      "url": "https://r2---sn-uigxx50n-8pxk.googlevideo.com/videoplayback?expire=1571352127&ei=35moXcuGLdqZ1gK7zqeACw&ip=178.115.128.175&id=o-AHlmX6ewQ0oGkLxHaBex7a7LhrxFyL7ROERRi9UiIYW6&itag=43&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-uigxx50n-8pxk%2Csn-c0q7lnly&ms=au%2Crdu&mv=m&mvi=1&pl=20&initcwndbps=771250&mime=video%2Fwebm&gir=yes&clen=21700774&ratebypass=yes&dur=0.000&lmt=1298436288017332&mt=1571330440&fvip=5&fexp=23842630&c=WEB&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cratebypass%2Cdur%2Clmt&sig=ALgxI2wwRQIgEE0vAIDpN9JC4xFD4wTMvZwP7BrTPkJk-uMSw2g30H4CIQDU52N-7pFnM8cZgd1bchLRthcl6i6ZGbTCweZ61txrdg%3D%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRgIhANqY0o3uYDdDP-Ayajc9sWOgDH-9SUVNft9S78aFM3YqAiEA0MTAGAhSuXCGMun6oKkwCBnQ5r5sVLBK1MvH6Cr-gVs%3D",
      "abr": 128,
      "asr": null,
      "vcodec": "vp8.0"
    },
    {
      "height": 262,
      "filesize": 26294671,
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.57 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-us,en;q=0.5"
      },
      "format_id": "18",
      "protocol": "https",
      "ext": "mp4",
      "tbr": 355.714,
      "format": "18 - 352x262 (240p)",
      "acodec": "mp4a.40.2",
      "format_note": "240p",
      "width": 352,
      "fps": null,
      "player_url": null,
      "url": "https://r2---sn-uigxx50n-8pxk.googlevideo.com/videoplayback?expire=1571352127&ei=35moXcuGLdqZ1gK7zqeACw&ip=178.115.128.175&id=o-AHlmX6ewQ0oGkLxHaBex7a7LhrxFyL7ROERRi9UiIYW6&itag=18&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-uigxx50n-8pxk%2Csn-c0q7lnly&ms=au%2Crdu&mv=m&mvi=1&pl=20&initcwndbps=771250&mime=video%2Fmp4&gir=yes&clen=26294671&ratebypass=yes&dur=591.458&lmt=1415795880482368&mt=1571330440&fvip=5&fexp=23842630&c=WEB&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cratebypass%2Cdur%2Clmt&sig=ALgxI2wwRAIgY-EEHBbMKgL3IOtT574RJJNPZRQgYw3gZb682o8-TfQCIEwAsWs8FjYXX8mBZR_wRZlgz1XcGlfN1LCoVbYmhNu_&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRgIhANqY0o3uYDdDP-Ayajc9sWOgDH-9SUVNft9S78aFM3YqAiEA0MTAGAhSuXCGMun6oKkwCBnQ5r5sVLBK1MvH6Cr-gVs%3D",
      "abr": 96,
      "asr": 44100,
      "vcodec": "avc1.42001E"
    }
  ],
  "format_note": "240p",
  "webpage_url": "https://www.youtube.com/watch?v=Ahg8OBYixL0",
  "alt_title": null,
  "release_year": null,
  "webpage_url_basename": "watch",
  "format": "18 - 352x262 (240p)",
  "fps": null,
  "uploader_id": "enaiel",
  "_filename": "The Star7 PDA Prototype-Ahg8OBYixL0.mp4",
  "width": 352,
  "chapters": null,
  "view_count": 43611,
  "thumbnails": [
    {
      "url": "https://i.ytimg.com/vi/Ahg8OBYixL0/hqdefault.jpg",
      "id": "0"
    }
  ],
  "channel_id": "UC5hlZn3loBczMoU9KskruoA",
  "is_live": null,
  "display_id": "Ahg8OBYixL0",
  "description": "The Star7 (*7) was a prototype for a SPARC based, handheld wireless PDA, with a 5\\" color LCD with touchscreen input, a new 16 bit --5:6:5 color hardware double buffered NTSC framebuffer, 900MHz wireless networking, PCMCIA bus interfaces, multi-media audio codec, a new power supply/battery interface, radical industrial design and packaging/process technology, a version of Unix that runs in under a megabyte, including drivers for PCMCIA, radio networking, touchscreen, display, flash RAM file system, execute-in-place, split I/D cache, with cached framebuffer support, a new small, safe, secure, distributed, robust, interpreted, garbage collected, multi-threaded, architecture neutral, high performance, dynamic programming language, a new small, fast, true-color alpha channel compositing, sprite graphics library, a set of classes that implement a spatial user interface metaphor, a user interface methodology which uses animation, audio, spatial cues, gestures, agency, color, and fun, a set of applications which show all of the features of the *7 hardware and software combination, including a TV guide, a fully functioning television remote control, a ShowMe style distributed whiteboard which allows active objects to be transmitted over a wireless network, and an on-screen agent which makes the whole experience fun and engaging.\\n\\nAll of this, in 1992! While the Star7 may have never entered commercial production, Oak, the language behind it all, became the very popular Java programming language.\\n\\nCopyright (c) Sun Microsystems.\\n\\nFor more information see:\\nhttps://duke.dev.java.net/green/\\nhttp://blogs.sun.com/jag/entry/the_green_ui",
  "episode_number": null,
  "extractor_key": "Youtube",
  "title": "The Star7 PDA Prototype",
  "acodec": "mp4a.40.2",
  "dislike_count": 3,
  "abr": 96,
  "creator": null,
  "filesize": 26294671,
  "id": "Ahg8OBYixL0",
  "vcodec": "avc1.42001E",
  "license": null,
  "fulltitle": "The Star7 PDA Prototype",
  "annotations": null,
  "start_time": null,
  "channel_url": "http://www.youtube.com/channel/UC5hlZn3loBczMoU9KskruoA",
  "ext": "mp4",
  "player_url": null,
  "album": null,
  "asr": 44100,
  "tbr": 355.714
}""")

        new_mediafilename_generated = os.path.join(tmpdir, self.guess_filename.handle_file(mediafile, False))
        new_mediafilename_comparison = os.path.join(tmpdir, "2007-09-13 youtube - The Star7 PDA Prototype - Ahg8OBYixL0.mp4")
        self.assertEqual(new_mediafilename_generated, new_mediafilename_comparison)

        os.remove(new_mediafilename_generated)
        os.remove(jsonfile)
        os.rmdir(tmpdir)


    def test_orf_tvthek_json_metadata(self):

        tmpdir=tempfile.mkdtemp()
        mediafile=tempfile.mkstemp(dir=tmpdir, prefix='Durchbruch bei Brexit-Verhandlungen-', suffix='.mp4')[1]
        jsonfile=os.path.join(os.path.dirname(mediafile), os.path.splitext(mediafile)[0] + '.info.json')

        with open(mediafile, 'w') as outputhandle:
            outputhandle.write('This is not of any interest. Delete me.')

        with open(jsonfile, 'w') as outputhandle:
            outputhandle.write("""{
  "duration": null,
  "playlist_title": null,
  "playlist": "14577219",
  "width": 1280,
  "extractor_key": "ORFTVthek",
  "thumbnail": null,
  "playlist_uploader": null,
  "description": "Es ist vollbracht: Die EU und Großbritannien haben sich auf einen Brexit-Vertrag geeinigt. Das bestätigten Kommissionspräsident Juncker und Premier Johnson. Durch ist die Einigung damit aber noch längst nicht.",
  "extractor": "orf:tvthek",
  "url": "https://apasfiis.sf.apa.at/cms-worldwide_nas/_definst_/nas/cms-worldwide/online/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_Q8C.mp4/chunklist.m3u8",
  "playlist_id": "14577219",
  "height": 720,
  "n_entries": 8,
  "format_id": "hls-Q8C-Sehr_hoch-3886",
  "_type": "video",
  "display_id": "14577219",
  "vcodec": "avc1.77.31",
  "tbr": 3886.742,
  "upload_date": null,
  "fps": null,
  "subtitles": {
    "de-AT": [
      {
        "url": "https://api-tvthek.orf.at/uploads/media/subtitles/0091/63/8b058fcdeb1046abe4866a70d6a7280c06b2ee3a.",
        "ext": "unknown_video"
      },
      {
        "url": "https://api-tvthek.orf.at/uploads/media/subtitles/0091/63/505af4543d7f9e5d3ab53ac37621d1a1e9e4cad7.srt",
        "ext": "srt"
      },
      {
        "url": "https://api-tvthek.orf.at/uploads/media/subtitles/0091/63/abee3589f30be631cad01b8ae93def8a2d76f7dd.vtt",
        "ext": "vtt"
      },
      {
        "url": "https://api-tvthek.orf.at/uploads/media/subtitles/0091/63/6a5b96f23da49f3d4da1905b2d1477b6282da83d.smi",
        "ext": "smi"
      },
      {
        "url": "https://api-tvthek.orf.at/uploads/media/subtitles/0091/63/1207bb113fabd7865efa04f0870bd0de614c8a4c.ttml",
        "ext": "ttml"
      }
    ]
  },
  "id": "14577219",
  "formats": [
    {
      "protocol": "f4m",
      "width": 320,
      "preference": null,
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3554.1 Safari/537.36",
        "Accept-Language": "en-us,en;q=0.5",
        "Cookie": "ASP.NET_SessionId=0npxlhiy2jqaapscvafzp0sf",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
      },
      "manifest_url": "https://apasfiis.sf.apa.at/f4m/cms-worldwide/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_Q1A.3gp/manifest.f4m",
      "url": "https://apasfiis.sf.apa.at/f4m/cms-worldwide/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_Q1A.3gp/manifest.f4m",
      "height": 180,
      "ext": "flv",
      "format_id": "hds-Q1A-Niedrig-430",
      "tbr": 430,
      "vcodec": null,
      "format": "hds-Q1A-Niedrig-430 - 320x180"
    },
    {
      "fps": null,
      "protocol": "m3u8",
      "width": 320,
      "preference": null,
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3554.1 Safari/537.36",
        "Accept-Language": "en-us,en;q=0.5",
        "Cookie": "ASP.NET_SessionId=0npxlhiy2jqaapscvafzp0sf",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
      },
      "acodec": "mp4a.40.2",
      "manifest_url": "https://apasfiis.sf.apa.at/cms-worldwide_nas/_definst_/nas/cms-worldwide/online/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_Q1A.3gp/playlist.m3u8",
      "url": "https://apasfiis.sf.apa.at/cms-worldwide_nas/_definst_/nas/cms-worldwide/online/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_Q1A.3gp/chunklist.m3u8",
      "height": 180,
      "ext": "mp4",
      "format_id": "hls-Q1A-Niedrig-516",
      "tbr": 516.024,
      "vcodec": "avc1.77.30",
      "format": "hls-Q1A-Niedrig-516 - 320x180"
    },
    {
      "protocol": "f4m",
      "width": 640,
      "preference": null,
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3554.1 Safari/537.36",
        "Accept-Language": "en-us,en;q=0.5",
        "Cookie": "ASP.NET_SessionId=0npxlhiy2jqaapscvafzp0sf",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
      },
      "manifest_url": "https://apasfiis.sf.apa.at/f4m/cms-worldwide/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_Q4A.mp4/manifest.f4m",
      "url": "https://apasfiis.sf.apa.at/f4m/cms-worldwide/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_Q4A.mp4/manifest.f4m",
      "height": 360,
      "ext": "flv",
      "format_id": "hds-Q4A-Mittel-989",
      "tbr": 989,
      "vcodec": null,
      "format": "hds-Q4A-Mittel-989 - 640x360"
    },
    {
      "manifest_url": "https://apasfiis.sf.apa.at/cms-worldwide_nas/_definst_/nas/cms-worldwide/online/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_hr.smil/playlist.m3u8",
      "url": "https://apasfiis.sf.apa.at/cms-worldwide_nas/_definst_/nas/cms-worldwide/online/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_hr.smil/chunklist_b992000.m3u8",
      "protocol": "m3u8",
      "ext": "mp4",
      "fps": null,
      "format_id": "hls-QXB-Adaptiv-992",
      "tbr": 992.0,
      "preference": null,
      "format": "hls-QXB-Adaptiv-992 - unknown",
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3554.1 Safari/537.36",
        "Accept-Language": "en-us,en;q=0.5",
        "Cookie": "ASP.NET_SessionId=0npxlhiy2jqaapscvafzp0sf",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
      }
    },
    {
      "fps": null,
      "protocol": "m3u8",
      "width": 640,
      "preference": null,
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3554.1 Safari/537.36",
        "Accept-Language": "en-us,en;q=0.5",
        "Cookie": "ASP.NET_SessionId=0npxlhiy2jqaapscvafzp0sf",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
      },
      "acodec": "mp4a.40.2",
      "manifest_url": "https://apasfiis.sf.apa.at/cms-worldwide_nas/_definst_/nas/cms-worldwide/online/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_Q4A.mp4/playlist.m3u8",
      "url": "https://apasfiis.sf.apa.at/cms-worldwide_nas/_definst_/nas/cms-worldwide/online/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_Q4A.mp4/chunklist.m3u8",
      "height": 360,
      "ext": "mp4",
      "format_id": "hls-Q4A-Mittel-1236",
      "tbr": 1236.117,
      "vcodec": "avc1.77.30",
      "format": "hls-Q4A-Mittel-1236 - 640x360"
    },
    {
      "protocol": "f4m",
      "width": 960,
      "preference": null,
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3554.1 Safari/537.36",
        "Accept-Language": "en-us,en;q=0.5",
        "Cookie": "ASP.NET_SessionId=0npxlhiy2jqaapscvafzp0sf",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
      },
      "manifest_url": "https://apasfiis.sf.apa.at/f4m/cms-worldwide/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_Q6A.mp4/manifest.f4m",
      "url": "https://apasfiis.sf.apa.at/f4m/cms-worldwide/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_Q6A.mp4/manifest.f4m",
      "height": 540,
      "ext": "flv",
      "format_id": "hds-Q6A-Hoch-1991",
      "tbr": 1991,
      "vcodec": null,
      "format": "hds-Q6A-Hoch-1991 - 960x540"
    },
    {
      "manifest_url": "https://apasfiis.sf.apa.at/cms-worldwide_nas/_definst_/nas/cms-worldwide/online/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_hr.smil/playlist.m3u8",
      "url": "https://apasfiis.sf.apa.at/cms-worldwide_nas/_definst_/nas/cms-worldwide/online/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_hr.smil/chunklist_b1992000.m3u8",
      "protocol": "m3u8",
      "ext": "mp4",
      "fps": null,
      "format_id": "hls-QXB-Adaptiv-1992",
      "tbr": 1992.0,
      "preference": null,
      "format": "hls-QXB-Adaptiv-1992 - unknown",
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3554.1 Safari/537.36",
        "Accept-Language": "en-us,en;q=0.5",
        "Cookie": "ASP.NET_SessionId=0npxlhiy2jqaapscvafzp0sf",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
      }
    },
    {
      "fps": null,
      "protocol": "m3u8",
      "width": 960,
      "preference": null,
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3554.1 Safari/537.36",
        "Accept-Language": "en-us,en;q=0.5",
        "Cookie": "ASP.NET_SessionId=0npxlhiy2jqaapscvafzp0sf",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
      },
      "acodec": "mp4a.40.2",
      "manifest_url": "https://apasfiis.sf.apa.at/cms-worldwide_nas/_definst_/nas/cms-worldwide/online/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_Q6A.mp4/playlist.m3u8",
      "url": "https://apasfiis.sf.apa.at/cms-worldwide_nas/_definst_/nas/cms-worldwide/online/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_Q6A.mp4/chunklist.m3u8",
      "height": 540,
      "ext": "mp4",
      "format_id": "hls-Q6A-Hoch-2437",
      "tbr": 2437.8,
      "vcodec": "avc1.77.31",
      "format": "hls-Q6A-Hoch-2437 - 960x540"
    },
    {
      "protocol": "f4m",
      "width": 1280,
      "preference": null,
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3554.1 Safari/537.36",
        "Accept-Language": "en-us,en;q=0.5",
        "Cookie": "ASP.NET_SessionId=0npxlhiy2jqaapscvafzp0sf",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
      },
      "manifest_url": "https://apasfiis.sf.apa.at/f4m/cms-worldwide/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_Q8C.mp4/manifest.f4m",
      "url": "https://apasfiis.sf.apa.at/f4m/cms-worldwide/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_Q8C.mp4/manifest.f4m",
      "height": 720,
      "ext": "flv",
      "format_id": "hds-Q8C-Sehr_hoch-3188",
      "tbr": 3188,
      "vcodec": null,
      "format": "hds-Q8C-Sehr_hoch-3188 - 1280x720"
    },
    {
      "manifest_url": "https://apasfiis.sf.apa.at/cms-worldwide_nas/_definst_/nas/cms-worldwide/online/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_hr.smil/playlist.m3u8",
      "url": "https://apasfiis.sf.apa.at/cms-worldwide_nas/_definst_/nas/cms-worldwide/online/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_hr.smil/chunklist_b3192000.m3u8",
      "protocol": "m3u8",
      "ext": "mp4",
      "fps": null,
      "format_id": "hls-QXB-Adaptiv-3192",
      "tbr": 3192.0,
      "preference": null,
      "format": "hls-QXB-Adaptiv-3192 - unknown",
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3554.1 Safari/537.36",
        "Accept-Language": "en-us,en;q=0.5",
        "Cookie": "ASP.NET_SessionId=0npxlhiy2jqaapscvafzp0sf",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
      }
    },
    {
      "fps": null,
      "protocol": "m3u8",
      "width": 1280,
      "preference": null,
      "http_headers": {
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3554.1 Safari/537.36",
        "Accept-Language": "en-us,en;q=0.5",
        "Cookie": "ASP.NET_SessionId=0npxlhiy2jqaapscvafzp0sf",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
      },
      "acodec": "mp4a.40.2",
      "manifest_url": "https://apasfiis.sf.apa.at/cms-worldwide_nas/_definst_/nas/cms-worldwide/online/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_Q8C.mp4/playlist.m3u8",
      "url": "https://apasfiis.sf.apa.at/cms-worldwide_nas/_definst_/nas/cms-worldwide/online/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_Q8C.mp4/chunklist.m3u8",
      "height": 720,
      "ext": "mp4",
      "format_id": "hls-Q8C-Sehr_hoch-3886",
      "tbr": 3886.742,
      "vcodec": "avc1.77.31",
      "format": "hls-Q8C-Sehr_hoch-3886 - 1280x720"
    }
  ],
  "protocol": "m3u8",
  "manifest_url": "https://apasfiis.sf.apa.at/cms-worldwide_nas/_definst_/nas/cms-worldwide/online/2019-10-17_1700_tl_02_ZIB-17-00_Durchbruch-bei-__14029194__o__9751208575__s14577219_9__ORF2BHD_16590721P_17000309P_Q8C.mp4/playlist.m3u8",
  "fulltitle": "Durchbruch bei Brexit-Verhandlungen",
  "preference": null,
  "webpage_url_basename": "14577219",
  "acodec": "mp4a.40.2",
  "http_headers": {
    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3554.1 Safari/537.36",
    "Accept-Language": "en-us,en;q=0.5",
    "Cookie": "ASP.NET_SessionId=0npxlhiy2jqaapscvafzp0sf",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
  },
  "title": "Durchbruch bei Brexit-Verhandlungen",
  "_filename": "Durchbruch bei Brexit-Verhandlungen-14577219.mp4",
  "webpage_url": "https://tvthek.orf.at/profile/ZIB-1700/71284/ZIB-1700/14029194/Durchbruch-bei-Brexit-Verhandlungen/14577219",
  "ext": "mp4",
  "playlist_uploader_id": null,
  "format": "hls-Q8C-Sehr_hoch-3886 - 1280x720",
  "playlist_index": 2
}""")

        new_mediafilename_generated = os.path.join(tmpdir, self.guess_filename.handle_file(mediafile, False))
        new_mediafilename_comparison = os.path.join(tmpdir, "2019-10-17T16.59.07 ORF - ZIB 17 00 - Durchbruch bei Brexit-Verhandlungen -- highquality.mp4")
        self.assertEqual(new_mediafilename_generated, new_mediafilename_comparison)

        os.remove(new_mediafilename_generated)
        os.remove(jsonfile)
        os.rmdir(tmpdir)


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

        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("2017-03-12--2017-09-23 hipster.pdf"),
                         "2017-03-12--2017-09-23 Hipster-PDA vollgeschrieben -- scan notes.pdf")
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("2017-03-12--2017-09-23 hipster.png"),
                         "2017-03-12--2017-09-23 Hipster-PDA vollgeschrieben -- scan notes.png")
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("2017-03-12-2017-09-23 hipster.png"),
                         "2017-03-12-2017-09-23 Hipster-PDA vollgeschrieben -- scan notes.png")
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("2017-03-12-2017-09-23 Hipster.png"),
                         "2017-03-12-2017-09-23 Hipster-PDA vollgeschrieben -- scan notes.png")

        # rec_20171129-0902 A nice recording .wav -> 2017-11-29T09.02 A nice recording.wav
        # rec_20171129-0902 A nice recording.wav  -> 2017-11-29T09.02 A nice recording.wav
        # rec_20171129-0902.wav -> 2017-11-29T09.02.wav
        # rec_20171129-0902.mp3 -> 2017-11-29T09.02.mp3
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("rec_20171129-0902 A nice recording .wav"),
                         "2017-11-29T09.02 A nice recording.wav")
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("rec_20171129-0902 A nice recording.wav"),
                         "2017-11-29T09.02 A nice recording.wav")
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("rec_20171129-0902.wav"),
                         "2017-11-29T09.02.wav")
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("rec_20171129-0902.mp3"),
                         "2017-11-29T09.02.mp3")

        # Screenshot_2017-11-29_10-32-12.png
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("Screenshot_2017-11-29_10-32-12.png"),
                         "2017-11-29T10.32.12 -- screenshots.png")
        # Screenshot_2017-11-07_07-52-59 my description.png
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("Screenshot_2017-11-29_10-32-12 my description.png"),
                         "2017-11-29T10.32.12 my description -- screenshots.png")

        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("2017-11-14_16-10_Tue.gpx"),
                         "2017-11-14T16.10.gpx")
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("2017-12-07_09-23_Thu Went for a walk .gpx"),
                         "2017-12-07T09.23 Went for a walk.gpx")
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("2017-11-03_07-29_Fri Bicycling.gpx"),
                         "2017-11-03T07.29 Bicycling.gpx")

        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("20180510T090000 ORF - ZIB - Signation -ORIGINAL- 2018-05-10_0900_tl_02_ZIB-9-00_Signation__13976423__o__1368225677__s14297692_2__WEB03HD_09000305P_09001400P_Q4A.mp4"),
                         "2018-05-10T09.00.03 ORF - ZIB - Signation -- lowquality.mp4")
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("20180510T090000 ORF - ZIB - Weitere Signale der Entspannung -ORIGINAL- 2018-05-10_0900_tl_02_ZIB-9-00_Weitere-Signale__13976423__o__5968792755__s14297694_4__WEB03HD_09011813P_09020710P_Q4A.mp4"),
                         "2018-05-10T09.01.18 ORF - ZIB - Weitere Signale der Entspannung -- lowquality.mp4")
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("20180520T201500 ORF - Tatort - Tatort_ Aus der Tiefe der Zeit -ORIGINAL- 2018-05-20_2015_in_02_Tatort--Aus-der_____13977411__o__1151703583__s14303062_Q8C.mp4"),
                         "2018-05-20T20.15.00 ORF - Tatort - Tatort  Aus der Tiefe der Zeit -- highquality.mp4")
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("20180521T193000 ORF - ZIB 1 - Parlament bereitet sich auf EU-Vorsitz vor -ORIGINAL- 2018-05-21_1930_tl_02_ZIB-1_Parlament-berei__13977453__o__277886215b__s14303762_2__WEB03HD_19350304P_19371319P_Q4A.mp4"),
                         "2018-05-21T19.35.03 ORF - ZIB 1 - Parlament bereitet sich auf EU-Vorsitz vor -- lowquality.mp4")
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('20190902T220000 ORF - ZIB 2 - Bericht über versteckte ÖVP-Wahlkampfkosten -ORIGINALlow- 2019-09-02_2200_tl_02_ZIB-2_Bericht-ueber-v__14024705__o__71528285d6__s14552793_3__ORF2HD_22033714P_22074303P_Q4A.mp4'),
                         '2019-09-02T22.03.37 ORF - ZIB 2 - Bericht über versteckte ÖVP-Wahlkampfkosten -- lowquality.mp4')
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('20190902T220000 ORF - ZIB 2 - Hinweis _ Verabschiedung -ORIGINALlow- 2019-09-02_2200_tl_02_ZIB-2_Hinweis---Verab__14024705__o__857007705d__s14552799_9__ORF2HD_22285706P_22300818P_Q4A.mp4'),
                         '2019-09-02T22.28.57 ORF - ZIB 2 - Hinweis   Verabschiedung -- lowquality.mp4')
        # NOTE: if you add test cases, you have to add the file name to __init__.py > get_file_size() as well in order to overrule the file size check which would fail in any case!
        # self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename(''),
        #                  '')

        # ORF file not truncated but still without detailed time-stamps
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("20180608T193000 ORF - Österreich Heute - Das Magazin - Österreich Heute - Das Magazin -ORIGINAL- 13979231_0007_Q8C.mp4"),
                         "2018-06-08T19.30.00 ORF - Österreich Heute - Das Magazin - Österreich Heute - Das Magazin -- highquality.mp4")

        # plausibility checks of file sizes: report plausible sizes
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("20180608T170000 ORF - ZIB 17_00 - size okay -ORIGINAL- 2018-06-08_1700_tl__13979222__o__1892278656__s14313181_1__WEB03HD_17020613P_17024324P_Q4A.mp4"),
                         "2018-06-08T17.02.06 ORF - ZIB 17 00 - size okay -- lowquality.mp4")
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename("20180608T170000 ORF - ZIB 17_00 - size okay -ORIGINAL- 2018-06-08_1700_tl__13979222__o__1892278656__s14313181_1__WEB03HD_17020613P_17024324P_Q8C.mp4"),
                         "2018-06-08T17.02.06 ORF - ZIB 17 00 - size okay -- highquality.mp4")

        # plausibility checks of file sizes: report non-plausible sizes
        #FIXXME: 2019-09-03: tests disabled because the function was disabled and never raises the expected exception
        #with self.assertRaises(FileSizePlausibilityException, message='file size is not plausible (too small)'):
        #    self.guess_filename.derive_new_filename_from_old_filename("20180608T170000 ORF - ZIB 17_00 - size not okay -ORIGINAL- 2018-06-08_1700_tl__13979222__o__1892278656__s14313181_1__WEB03HD_17020613P_18024324P_Q4A.mp4")
        #with self.assertRaises(FileSizePlausibilityException, message='file size is not plausible (too small)'):
        #    self.guess_filename.derive_new_filename_from_old_filename("20180608T170000 ORF - ZIB 17_00 - size not okay -ORIGINAL- 2018-06-08_1700_tl__13979222__o__1892278656__s14313181_1__WEB03HD_17020613P_18024324P_Q8C.mp4")

        # You might think that it should be 2018-06-09 instead of 2018-06-10. This is caused by different
        # day of metadata from filename (after midnight) and metadata from time-stamp (seconds before midnight):
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('20180610T000000 ORF - Kleinkunst - Kleinkunst_ Cordoba - Das Rückspiel (2_2) -ORIGINAL- 2018-06-10_0000_sd_06_Kleinkunst--Cor_____13979381__o__1483927235__s14313621_1__ORF3HD_23592020P_00593103P_Q8C.mp4'),
                         '2018-06-10T23.59.20 ORF - Kleinkunst - Kleinkunst  Cordoba - Das Rückspiel (2 2) -- highquality.mp4')

        # Original ORF TV Mediathek download file names (as a fall-back for raw download using wget or curl):
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('2018-06-14_2105_sd_02_Am-Schauplatz_-_Alles für die Katz-_____13979879__o__1907287074__s14316407_7__WEB03HD_21050604P_21533212P_Q8C.mp4'),
                         '2018-06-14T21.05.06 Am Schauplatz - Alles für die Katz -- highquality.mp4')
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('2018-06-14_2155_sd_06_Kottan-ermittelt - Wien Mitte_____13979903__o__1460660672__s14316392_2__ORF3HD_21570716P_23260915P_Q8C.mp4'),
                         '2018-06-14T21.57.07 Kottan ermittelt - Wien Mitte -- highquality.mp4')
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('2018-06-14_2330_sd_06_Sommerkabarett - Lukas Resetarits: Schmäh (1 von 2)_____13979992__o__1310584704__s14316464_4__ORF3HD_23301620P_00302415P_Q8C.mp4'),
                         '2018-06-14T23.30.16 Sommerkabarett - Lukas Resetarits: Schmäh (1 von 2) -- highquality.mp4')
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('2019-09-29_2255_sd_02_Das-Naturhistor_____14027337__o__1412900222__s14566948_8__ORF2HD_23152318P_00005522P_Q8C.mp4/playlist.m3u8'),
                         '2019-09-29T23.15.23 Das Naturhistor -- highquality.mp4')

        # ORF TV Mediathek as of 2018-11-01: when there is no original filename with %N, I have to use the data I've got
        # see https://github.com/mediathekview/MServer/issues/436
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('20181028T201400 ORF - Tatort - Tatort_ Blut -ORIGINALhd- playlist.m3u8.mp4'),
                         '2018-10-28T20.14.00 ORF - Tatort - Tatort_ Blut -- highquality.mp4')
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('20181028T201400 ORF - Tatort - Tatort_ Blut -ORIGINALlow- playlist.m3u8.mp4'),
                         '2018-10-28T20.14.00 ORF - Tatort - Tatort_ Blut -- lowquality.mp4')
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('20181022T211100 ORF - Thema - Das Essen der Zukunft -ORIGINALhd- playlist.m3u8.mp4'),
                         '2018-10-22T21.11.00 ORF - Thema - Das Essen der Zukunft -- highquality.mp4')
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('20181022T211100 ORF - Thema - Das Essen der Zukunft -ORIGINALlow- playlist.m3u8.mp4'),
                         '2018-10-22T21.11.00 ORF - Thema - Das Essen der Zukunft -- lowquality.mp4')
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('20181025T210500 ORF - Am Schauplatz - Am Schauplatz_ Wenn alles zusammenbricht -ORIGINALhd- playlist.m3u8.mp4'),
                         '2018-10-25T21.05.00 ORF - Am Schauplatz - Am Schauplatz_ Wenn alles zusammenbricht -- highquality.mp4')
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('20181025T210500 ORF - Am Schauplatz - Am Schauplatz_ Wenn alles zusammenbricht -ORIGINALlow- playlist.m3u8.mp4'),
                         '2018-10-25T21.05.00 ORF - Am Schauplatz - Am Schauplatz_ Wenn alles zusammenbricht -- lowquality.mp4')

        # Digital camera from Android
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('IMG_20190118_133928.jpg'),
                         '2019-01-18T13.39.28.jpg')
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('IMG_20190118_133928 This is a note.jpg'),
                         '2019-01-18T13.39.28 This is a note.jpg')
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('IMG_20190118_133928_Bokeh.jpg'),
                         '2019-01-18T13.39.28 Bokeh.jpg')
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('IMG_20190118_133928_Bokeh This is a note.jpg'),
                         '2019-01-18T13.39.28 Bokeh This is a note.jpg')

        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('2019-10-10 a file exported by Boox Max 2-Exported.pdf'),
                         '2019-10-10 a file exported by Boox Max 2 -- notes.pdf')
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('2019-10-10 a file exported by Boox Max 2 -- notes-Exported.pdf'),
                         '2019-10-10 a file exported by Boox Max 2 -- notes.pdf')
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('2019-10-10 a file exported by Boox Max 2 -- draft-Exported.pdf'),
                         '2019-10-10 a file exported by Boox Max 2 -- draft notes.pdf')


        # Smartrecorder
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('20190512-1125_Recording_1.wav'),
                         '2019-05-12T11.25 Recording 1.wav')
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('20190512-1125_Recording_1.mp3'),
                         '2019-05-12T11.25 Recording 1.mp3')
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('20190512-1125.wav'),
                         '2019-05-12T11.25.wav')
        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename('20190512-1125.mp3'),
                         '2019-05-12T11.25.mp3')


#        self.assertEqual(self.guess_filename.derive_new_filename_from_old_filename(''),
#                         '')


    def test_film_url_regex(self):

        # check if the defined help text string for a MediathekView film URL matches the corresponding RegEx
        self.assertTrue(re.match(self.guess_filename.FILM_URL_REGEX, self.guess_filename.FILM_URL_EXAMPLE))


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
