#!/usr/bin/python
# CSS Test Suite Manipulation Library
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause: <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>

import sys
from os.path import join, exists, abspath
from template import Template
import CSSTestLib

class Section:
  def __init__(self, uri, title, sortstr, numstr):
    self.uri = uri
    self.title = title
    self.sortstr = sortstr # sortable (zero-filled) section number
    self.numstr = numstr
    self.tests = {} # lists indexed by group name
  def __cmp__(self, other):
    return cmp(self.sortstr, other.sortstr)

class Indexer:

  def __init__(self, suite, tocDataPath, splitlevel=0, templatePathList=None):
    """Initialize indexer with CSSTestSuite `suite` toc data file
       `tocDataPath` and additional template paths in list `templatePathList`.

       The toc data file should be list of tab-separated records, one
       per line, of each spec section's sort string, uri, number/letter,
       and title.
       `splitlevel` is the number of prefix characters common to each
       chapter's sort string in the toc data file: set to zero for a
       single-page index; set to two to create chapter indices when
       using two-digit chapter numbers in the sort string.
    """
    self.suite = suite
    self.splitlevel = splitlevel

    # Initialize template engine
    self.templatePath = [join(CSSTestLib.__path__[0], 'templates')]
    if templatePathList:
      self.templatePath.extend(templatePathList)
    self.templatePath = [abspath(path) for path in self.templatePath]
    self.tt = Template({
       'INCLUDE_PATH': self.templatePath,
       'PRE_CHOMP'   : 1,
       'POST_CHOMP'  : 0,
    })

    # Load toc data
    self.sections = {}
    for record in open(tocDataPath):
      sortstr, uri, numstr, title = record.split('\t')
      uri = intern(uri)
      self.sections[uri] = Section(uri, title, sortstr, numstr)

    # Initialize storage
    self.errors = []
    self.contributors = set()

  def indexGroup(self, group):
    for test in group.iterTests():
      data = test.getMetadata()
      if data: # Shallow copy for template output
        data = data.copy()
        data['file'] = '/'.join((group.name, test.name()))
        for uri in data['links']:
          if self.sections.has_key(uri):
            testlist = self.sections[uri].tests.append(data)
        for credit in data['credits']:
          self.contributors.add(credit)
      else:
        self.errors.append(test.error)

  def __writeTemplate(self, template, data, outfile):
    o = self.tt.process(template, data)
    f = open(outfile, 'w')
    f.write(o.encode('utf-8'))
    f.close()

  def writeOverview(self, destDir, errorOut=sys.stderr):
    """Write format-agnostic pages such as test suite overview pages,
       test data files, and error reports.

       Indexed errors are reported to errorOut, which must be either
       an output handle such as sys.stderr, a tuple of
       (template filename string, output filename string)
       or None to suppress error output.
    """

    # Set common values
    data = {}
    data['suitetitle'] = self.suite.title
    data['specroot']   = self.suite.specroot

    # Print 

    # Report errors
    if type(errorOut) is type(('tmpl','out')):
      data['errors'] = self.errors
      self.__writeTemplate(errorOut[0], data, join(destDir, errorOut[1]))
    else:
      for error in self.errors:
        print >> errorOut, "Error in %s: %s" % \
                           (error.CSSTestSourceErrorLocation, error)

  def write(self, format):
    """Write indices into test suite build output through format `format`.
    """

    # Set common values
    data = {}
    data['suitetitle'] = self.suite.title
    data['specroot']   = self.suite.specroot
    data['indexext']   = format.indexExt
    data['isXML']      = format.indexExt.startswith('.x')
    data['formatdir']  = format.formatDirName
    data['extmap']     = format.extMap

    # Generate indices
    sectionlist = sorted(self.sections.values())
    if self.splitlevel:
      # Split sectionlist into chapters
      chapters = []
      lastChapNum = '$' # some nonmatching initial char
      chap = None
      for section in sectionlist:
        if not section.sortstr.startswith(lastChapNum):
          lastChapNum = section.sortstr[:self.splitlevel]
          chap = section
          chap.sections = []
          chap.testcount = 0
          chapters.append(chap)
          if not chap.tests:
            continue;
        chap.testcount += len(section.tests)
        chap.sections.append(section)

      # Generate main toc
      data['chapters'] = chapters
      self.__writeTemplate('chapter-toc.tmpl', data,
                           format.dest('toc%s' % format.indexExt))
      del data['chapters']

      # Generate chapter tocs
      for chap in chapters:
        data['chaptertitle'] = chap.title
        data['testcount']    = chap.testcount
        self.__writeTemplate('test-toc.tmpl', data, format.dest('chapter-%s%s' \
                             % (chap.sortstr, format.indexExt)))

    else: # not splitlevel
      data['chapters'] = sectionlist
      self.__writeTemplate('test-toc.tmpl', data,
                           format.dest('toc%s' % format.indexExt))
      del data['chapters']