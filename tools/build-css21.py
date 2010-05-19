#!/usr/bin/python
# CSS 2.1 Test Suite Build Script
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause: <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>

import os.path
print "Building CSS2.1 Test Suite from repository %s into %s" % \
      (os.path.abspath('.'), os.path.abspath(os.path.join('.', 'dist', 'css2.1')))

skipDirs = ('support')
reftestPath = os.path.join('reftest', 'reftest.list')
groupmap = {
    'http://www.w3.org/TR/CSS21/about.html'    : 'about',
    'http://www.w3.org/TR/CSS21/box.html#box-dimensions'              : 'box-model',
    'http://www.w3.org/TR/CSS21/box.html#mpb-examples'                : 'box-model',
    'http://www.w3.org/TR/CSS21/box.html#margin-properties'           : 'box-margins',
    'http://www.w3.org/TR/CSS21/box.html#collapsing-margins'          : 'box-margins',
    'http://www.w3.org/TR/CSS21/box.html#padding-properties'          : 'box-padding',
    'http://www.w3.org/TR/CSS21/box.html#border-properties'           : 'box-borders',
    'http://www.w3.org/TR/CSS21/box.html#border-width-properties'     : 'box-borders',
    'http://www.w3.org/TR/CSS21/box.html#border-color-properties'     : 'box-borders',
    'http://www.w3.org/TR/CSS21/box.html#border-style-properties'     : 'box-borders',
    'http://www.w3.org/TR/CSS21/box.html#border-shorthand-properties' : 'box-borders',
    'http://www.w3.org/TR/CSS21/box.html#bidi-box-model'              : 'box-model',
    'http://www.w3.org/TR/CSS21/cascade.html'  : 'cascade',
    'http://www.w3.org/TR/CSS21/colors.html'   : 'colors',
    'http://www.w3.org/TR/CSS21/conform.html'  : 'conform',
    'http://www.w3.org/TR/CSS21/fonts.html'    : 'fonts',
    'http://www.w3.org/TR/CSS21/generate.html' : 'generate',
    'http://www.w3.org/TR/CSS21/intro.html'    : 'intro',
    'http://www.w3.org/TR/CSS21/media.html'    : 'media',
    'http://www.w3.org/TR/CSS21/page.html'     : 'page',
    'http://www.w3.org/TR/CSS21/selector.html' : 'selector',
    'http://www.w3.org/TR/CSS21/syndata.html'  : 'syndata',
    'http://www.w3.org/TR/CSS21/tables.html'   : 'tables',
    'http://www.w3.org/TR/CSS21/text.html'     : 'text',
    'http://www.w3.org/TR/CSS21/visudet.html'  : 'visudet',
    'http://www.w3.org/TR/CSS21/visufx.html'   : 'visufx',
    'http://www.w3.org/TR/CSS21/visuren.html'  : 'visuren',
    'http://www.w3.org/TR/CSS21/zindex.html'   : 'zindex',
  }

import sys
from os.path import join, exists
from CSSTestLib.Suite import CSSTestSuite
from CSSTestLib.Indexer import Indexer
from CSSTestLib.Groups import SelftestGroup

# run from css test suite repo root

# Set up
suite = CSSTestSuite('css2.1', 'CSS2.1 Test Suite', 'http://www.w3.org/TR/CSS21/')

# Add approved tests
root = join('approved', 'css2.1', 'src')
_,dirs,_ = os.walk(root).next()
for dir in dirs:
  if dir in skipDirs: continue
  testroot = join(root, dir)
  suite.addSelftestsByExt(testroot, '.xht')
  if exists(join(testroot, reftestPath)):
    suite.addReftests(testroot, reftestPath)

# Add unreviewed tests
for path in sys.argv[1:]:
  if path.endswith('reftest.list'):
    suite.addReftests(os.path.split(path)[0], 'reftest.list')
  else:
    def grep(file):
      if not file.endswith('.xht'):
        return False
      for line in open(join(path, file)):
        if line.find(suite.specroot) != -1:
          return True
      return False
    _,_,files = os.walk(path).next()
    files = filter(grep, files)
    suite.addSelftestsByList(path, files)

# Build
data = join('approved', 'css2.1', 'data')
indexer = Indexer(suite, join(data, 'sections.dat'), 2, templatePathList=[data],
                  extraData={ 'devel' : True, 'official' : True })
suite.buildInto(join('dist', 'css2.1'), indexer)