# music_sync - Sync music library to external device
# Copyright (C) 2013-2015 Christian Fetzer
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

""" Tests the transcoding implementation """

import os
import shutil

from nose.tools import eq_
from nose.tools import raises

from sync_music.sync_music import Transcode

from . import util


class TestTranscode(util.TemporaryOutputPathFixture):
    """ Tests the transcoding implementation """

    in_filename_flac = 'withtags.flac'
    in_filename_flacall = 'withalltags.flac'
    in_filename_flacempty = 'stripped.flac'
    in_filename_ogg = 'withtags.ogg'
    in_filename_oggall = 'withalltags.ogg'
    in_filename_oggempty = 'stripped.ogg'
    in_filename_mp3 = 'withtags.mp3'
    in_filename_mp3all = 'withalltags.mp3'
    in_filename_mp3empty = 'stripped.mp3'
    in_filename_aiff = 'withtags.aiff'
    out_filename = 'withtags.mp3'
    img_filename = 'folder.jpg'
    input_path = 'tests/reference_data/audiofiles'
    output_path = '/tmp/sync_music'

    def __init__(self):
        super(TestTranscode, self).__init__(self.output_path)

    def test_filename(self):
        """ Tests retrieving the output file name """
        transcode = Transcode()
        out_filename = transcode.get_out_filename(self.in_filename_flac)
        eq_(self.out_filename, out_filename)

    def execute_transcode(self, transcode,
                          in_filename=in_filename_flac,
                          out_filename=out_filename):
        """ Helper method to run transcoding tests """
        transcode.execute(
            os.path.join(self.input_path, in_filename),
            os.path.join(self.output_path, out_filename))

    def test_transcode_default(self):
        """ Test transcoding with default options """
        self.execute_transcode(Transcode(),
                               in_filename=self.in_filename_flac)
        self.execute_transcode(Transcode(),
                               in_filename=self.in_filename_flacall)
        self.execute_transcode(Transcode(),
                               in_filename=self.in_filename_flacempty)
        self.execute_transcode(Transcode(),
                               in_filename=self.in_filename_ogg)
        self.execute_transcode(Transcode(),
                               in_filename=self.in_filename_oggall)
        self.execute_transcode(Transcode(),
                               in_filename=self.in_filename_oggempty)

    def test_transcode_copy(self):
        """ Tests transcoding with copying instead of transcoding """
        self.execute_transcode(Transcode(),
                               in_filename=self.in_filename_mp3)
        self.execute_transcode(Transcode(),
                               in_filename=self.in_filename_mp3all)
        self.execute_transcode(Transcode(),
                               in_filename=self.in_filename_mp3empty)

    def test_transcode_notranscode(self):
        """ Tests transcoding with transcoding (only update tags) """
        shutil.copy(
            os.path.join(self.input_path, self.in_filename_mp3empty),
            os.path.join(self.output_path, self.out_filename))
        self.execute_transcode(Transcode(transcode=False))

    def test_transcode_nocopytags(self):
        """ Tests transcoding without copying of tags """
        self.execute_transcode(Transcode(copy_tags=False))

    def test_transcode_folderimage(self):
        """ Tests transcoding without folder image """
        # Copy input file to a folder without folder.jpg (output folder)
        in_filename = os.path.join(self.output_path, self.in_filename_flac)
        shutil.copy(
            os.path.join(self.input_path, self.in_filename_flac),
            in_filename)
        self.execute_transcode(Transcode(), in_filename=in_filename)

    def test_transcode_composer_hack(self):
        """ Tests transcoding with composer hack enabled """
        self.execute_transcode(Transcode(composer_hack=True))
        self.execute_transcode(Transcode(composer_hack=True),
                               in_filename=self.in_filename_mp3empty)

    def test_transcode_discnumber_hack(self):
        """ Tests transcoding with disc number hack enabled """
        self.execute_transcode(Transcode(discnumber_hack=True))
        self.execute_transcode(Transcode(discnumber_hack=True),
                               in_filename=self.in_filename_mp3all)

    def test_transcode_tracknumber_hack(self):
        """ Tests transcoding with track number hack enabled """
        self.execute_transcode(Transcode(tracknumber_hack=True))
        self.execute_transcode(Transcode(tracknumber_hack=True),
                               in_filename=self.in_filename_mp3empty)
        self.execute_transcode(Transcode(tracknumber_hack=True),
                               in_filename='brokentag_tracknumber.mp3')

    @raises(IOError)
    def test_transcodeerror_transcode(self):
        """ Tests transcoding failure """
        # IOError is raised on audiotools.EncodingError. The easiest way that
        # leads into this exception is writing to a non writable path.
        self.execute_transcode(Transcode(), out_filename='/')

    @raises(IOError)
    def test_transcodeerror_copytags(self):
        """ Tests copying tag failure """
        # Copy tags expects the output file to be an MP3 file.
        # Don't transcode as this would rewrite the output file.
        shutil.copy(
            os.path.join(self.input_path, self.img_filename),
            os.path.join(self.output_path, self.out_filename))
        self.execute_transcode(Transcode(transcode=False))

    @raises(IOError)
    def test_transcodingerror_format(self):
        """ Tests transcoding a non supported format """
        self.execute_transcode(Transcode(transcode=True),
                               in_filename=self.in_filename_aiff)