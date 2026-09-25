#!/usr/bin/env python
''' phisto.py - Compute foveal histogram for picture set

Drop-in replacement for the original csh script by Greg Ward.
2016 - Georg Mischler
2026 - Chris Deline - updated to use pyradiance library for pfilt, 
       pvalue, total, histo and rcalc functions.  Remove self.tmpfile and
	   use in-memory bytes for intermediate data. 

The MIT License (MIT)

Copyright (c) 2016 Georg Mischler, Munich, Germany

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
__all__ = ('main')
import sys
import os
import argparse
import pyradiance

from pyradlib.pyrad_proc import PIPE, Error, ProcMixin
from pyradiance.anci import BINPATH

SHORTPROGN = os.path.splitext(os.path.basename(sys.argv[0]))[0]

class Phisto(ProcMixin):
	def __init__(self, args):
		self.donothing = args.N
		self.verbose = args.V or self.donothing
		self.imgfiles = args.picture[0]
		self.run()

	def _filter_image(self, image):
		'''Run pfilt then pvalue on one image (path or bytes), return float bytes.'''
		filtered = pyradiance.pfilt(image, xres='128', yres='128',
									pixel_aspect=1, one_pass=True)
		return pyradiance.pvalue(filtered, original=True,
								header=False, resstr=False,
								outform='f', brightness=True)

	def run(self):
		if self.donothing:
			if self.verbose:
				sys.stderr.write(
					'### pfilt -1 -x 128 -y 128 -p 1 [picture]'
					' | pvalue -o -h -H -df -b\n')
			self.tmpdata = b''
		else:
			if not self.imgfiles:
				self.tmpdata = self._filter_image(sys.stdin.buffer.read())
			else:
				for fname in self.imgfiles:
					self.raise_on_error('open file "%s"' % fname,
						'File not found.')
				self.tmpdata = b''
				for fname in self.imgfiles:
					self.tmpdata += self._filter_image(fname)
		self.run_calcprocs()

	def run_calcprocs(self):
		if self.donothing:
			lmin, lmax = '<Lmin>', '<Lmax>'
		else:
			lmin_total = pyradiance.total(self.tmpdata, find_min=True, inform='f')
			lmin = pyradiance.rcalc(lmin_total,
					expr='L=$1*179;$1=if(L-1e-7,log10(L)-.01,-7)').decode().strip()

			lmax_total = pyradiance.total(self.tmpdata, find_max=True, inform='f')
			lmax = pyradiance.rcalc(lmax_total,
					expr='$1=log10($1*179)+.01').decode().strip()

		rc_data = None
		if not self.donothing:
			rc_data = pyradiance.rcalc(self.tmpdata, inform='f',
									   expr='L=$1*179;cond=L-1e-7;$1=log10(L)')
		hi_cmd = [str(BINPATH / 'histo'), lmin, lmax, '777']
		hi_proc = self.call_one(hi_cmd, 'compute histogram', _in=PIPE, out=PIPE)
		if not self.donothing:
			hi_proc.stdin.write(rc_data)
			hi_proc.stdin.close()
			self.histo_lines = [l.decode() for l in hi_proc.stdout.readlines()]
			hi_proc.stdout.close()
			res = hi_proc.wait()
			if res != 0:
				self.raise_on_error('compute histogram',
						'Nonzero exit (%d) from histo' % res)
			sys.stdout.write(''.join(self.histo_lines))
		else:
			self.histo_lines = []

def main():
	''' This is a command line script and not currently usable as a module.
	Use the -H option for instructions.'''
	parser = argparse.ArgumentParser(add_help=False,
		description='Compute foveal histogram for picture set')
	parser.add_argument('-N', action='store_true',
		help='Do nothing (implies -V)')
	parser.add_argument('-V', action='store_true',
		help='Verbose: print commands to execute to stderr')
	parser.add_argument('-H', action='help',
		help='Help: print this text to stderr and exit')
	parser.add_argument('picture', action='append', nargs='*',
		help='HDR image files to analyze (else stdin)')
	Phisto(parser.parse_args())


if __name__ == '__main__':
	try: main()
	except KeyboardInterrupt:
		sys.stderr.write('*cancelled*\n')
		sys.exit(1)
	except Error as e:
		sys.stderr.write('%s: %s\n' % (SHORTPROGN, e))
		sys.exit(-1)

