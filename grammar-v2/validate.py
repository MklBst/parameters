#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Test a parameters file to check it follows grammar v2."""


import json
import unittest
import os
import sys
from functools import partial
from random import shuffle
from pprint import pprint


class ParametersFileTestCase(unittest.TestCase):

    def setUp(self):
        self.f = open(filename, 'r')

    def tearDown(self):
        self.f.close()


class JSONTestCase(ParametersFileTestCase):

    description = 'Checking the file is proper JSON'

    def test_is_json(self):
        try:
            json.load(self.f)
        except ValueError:
            self.fail('{} is not valid JSON!'.format(filename))


class LoadedParametersTestCase(ParametersFileTestCase):

    type_names = {int: 'an integer',
                  float: 'a float',
                  unicode: 'a string',
                  dict: 'a JSON object',
                  list: 'a list',
                  bool: 'a boolean'}
    error_in = "{0} has no '{1}' property"
    error_type = "'{1}' (in {0}) is not {2}"
    error_list_type = "'{1}' (in {0}) contains items that are not {2}"
    error_empty_list = "'{1}' (in {0}) is an empty list"
    warn_default = "You defined '{1}' (in {0}) but set it to its default value"

    def setUp(self):
        super(LoadedParametersTestCase, self).setUp()
        self.params = json.load(self.f)

    def _test_presence_and_type(self, container, container_name,
                                attr_name, attr_type, list_attr_type=None,
                                optional=False, default=None):
        # If optional and not present, nothing to do
        if optional and attr_name not in container:
            return

        # Test presence
        error_msg = self.error_in.format(container_name, attr_name)
        self.assertIn(attr_name, container, error_msg)

        # Test type
        error_msg = self.error_type.format(container_name, attr_name,
                                           self.type_names[attr_type])
        self.assertIsInstance(container[attr_name], attr_type, error_msg)

        # If optional and equals default value, it's useless
        if optional and container[attr_name] == default:
            self.fail(self.warn_default.format(container_name, attr_name))

        # Check list item types if we're a list
        if attr_type is list:
            error_msg = self.error_empty_list.format(container_name, attr_name)
            self.assertTrue(len(container[attr_name]), error_msg)

            if list_attr_type is not None:
                error_msg = self.error_list_type.format(
                    container_name, attr_name, self.type_names[list_attr_type])
                for item in container[attr_name]:
                    self.assertIsInstance(item, list_attr_type, error_msg)


class RootTestCase(LoadedParametersTestCase):

    description = 'Checking the root object is properly formatted'

    def test_is_dict(self):
        self.assertIsInstance(self.params, dict,
                              'Root of the file is not a JSON object')

    def test_version(self):
        self._test_presence_and_type(self.params, 'root object',
                                     'version', unicode)

    def test_nSlotsPerProbe(self):
        self._test_presence_and_type(self.params, 'root object',
                                     'nSlotsPerProbe', int)

    def test_questions(self):
        self._test_presence_and_type(self.params, 'root object',
                                     'questions', list, dict)

    def test_schedulingMinDelay(self):
        self._test_presence_and_type(self.params, 'root object',
                                     'schedulingMinDelay', int)

    def test_schedulingMeanDelay(self):
        self._test_presence_and_type(self.params, 'root object',
                                     'schedulingMeanDelay', int)


class QuestionsTestCase(LoadedParametersTestCase):

    description = 'Checking individual questions are properly formatted'

    def setUp(self):
        super(QuestionsTestCase, self).setUp()
        self.questions = self.params['questions']

    def _test_on_all_questions(self, tester):
        for i, q in enumerate(self.questions):
            qname = "question {}".format(i)
            tester(q, qname)

    def _test_presence_and_type_on_all_questions(
            self, attr_name, attr_type, list_attr_type=None,
            optional=False, default=None):
        self._test_on_all_questions(
            partial(self._test_presence_and_type, attr_name=attr_name,
                    attr_type=attr_type, list_attr_type=list_attr_type,
                    optional=optional, default=default))

    def test_name(self):
        self._test_presence_and_type_on_all_questions('name', unicode)

    def test_category(self):
        self._test_presence_and_type_on_all_questions('category', unicode)

    def test_subCategory(self):
        self._test_presence_and_type_on_all_questions('subCategory', unicode)

    def test_slot(self):
        self._test_presence_and_type_on_all_questions('slot', unicode)

    def test_details(self):
        self._test_presence_and_type_on_all_questions('details', dict)


class QuestionDetailsTestCase(LoadedParametersTestCase):

    description = 'Checking question details are properly formatted'
    allowed_types = ['MultipleChoice', 'Slider', 'StarRating']

    def setUp(self):
        super(QuestionDetailsTestCase, self).setUp()
        self.details = [q['details'] for q in self.params['questions']]
        self.names = [q['name'] for q in self.params['questions']]

    def test_type_and_derivatives(self):
        for i, (d, n) in enumerate(zip(self.details, self.names)):

            dname = ("details of question '{0}' "
                     "(number {1} in list)").format(n, i + 1)
            self._test_presence_and_type(d, dname, 'type', unicode)
            self.assertIn(d['type'], self.allowed_types)
            # Test MultipleChoice mandatory properties
            if d['type'] == 'MultipleChoice':
                self._test_presence_and_type(d, dname, 'text', unicode)
                self._test_presence_and_type(d, dname, 'choices',
                                             list, unicode)
            # Test Slider and StarRating mandatory properties
            elif d['type'] == 'Slider' or d['type'] == 'StarRating':
                self._test_presence_and_type(d, dname, 'subQuestions',
                                             list, dict)


class SubQuestionsTestCase(LoadedParametersTestCase):

    description = 'Checking subQuestions are properly formatted'
    default_numStars = 5
    default_stepSize = 0.5
    default_initialRating = 0
    default_initialPosition = 0
    default_showLiveIndication = False
    default_notApplyAllowed = False

    def setUp(self):
        super(SubQuestionsTestCase, self).setUp()
        self.subqss = [q['details']['subQuestions']
                       if (q['details']['type'] == 'Slider'
                           or q['details']['type'] == 'StarRating')
                       else []
                       for q in self.params['questions']]
        self.names = [q['name'] for q in self.params['questions']]
        self.types = [q['details']['type'] for q in self.params['questions']]

    def _test_on_all_subquestions(self, tester):
        for i, (subqs, n) in enumerate(zip(self.subqss, self.names)):
            for j, subq in enumerate(subqs):
                sqname = ("subQuestion {0} in question '{1}' "
                          "(number {2} in list)").format(j + 1, n, i + 1)
                tester(subq, sqname)

    def _test_on_typed_subquestions(self, qtype, tester):
        for i, (subqs, n, t) in enumerate(zip(self.subqss, self.names,
                                              self.types)):
            if not t == qtype:
                continue
            for j, subq in enumerate(subqs):
                sqname = ("subQuestion {0} in question '{1}' "
                          "(number {2} in list)").format(j + 1, n, i + 1)
                tester(subq, sqname)

    def _test_presence_and_type_on_all_subquestions(
            self, attr_name, attr_type, list_attr_type=None,
            optional=False, default=None):
        self._test_on_all_subquestions(
            partial(self._test_presence_and_type, attr_name=attr_name,
                    attr_type=attr_type, list_attr_type=list_attr_type,
                    optional=optional, default=default))

    def _test_presence_and_type_on_typed_subquestions(
            self, qtype, attr_name, attr_type, list_attr_type=None,
            optional=False, default=None):
        self._test_on_typed_subquestions(
            qtype,
            partial(self._test_presence_and_type, attr_name=attr_name,
                    attr_type=attr_type, list_attr_type=list_attr_type,
                    optional=optional, default=default))

    def test_text(self):
        self._test_presence_and_type_on_all_subquestions('text', unicode)

    def test_hints(self):
        self._test_presence_and_type_on_all_subquestions('hints', list,
                                                         unicode)

    def test_notApplyAllowed(self):
        self._test_presence_and_type_on_all_subquestions(
            'notApplyAllowed', bool, optional=True,
            default=self.default_notApplyAllowed)

    def test_showLiveIndication(self):
        self._test_presence_and_type_on_all_subquestions(
            'showLiveIndication', bool, optional=True,
            default=self.default_showLiveIndication)

    def test_slider_initialPosition(self):
        self._test_presence_and_type_on_typed_subquestions(
            'Slider', 'initialPosition', int, optional=True,
            default=self.default_initialPosition)

        # initialPosition is between 0 and 100
        def range_test(subq, subqname):
            error_msg = ("'initialPosition' in {} is not "
                         "between 0 and 100").format(subqname)
            initialPosition = subq.get('initialPosition')
            if initialPosition is None:
                return
            self.assertGreaterEqual(initialPosition, 0, error_msg)
            self.assertLessEqual(initialPosition, 100, error_msg)

        self._test_on_typed_subquestions('Slider', range_test)

    def test_starRating_numStars(self):
        self._test_presence_and_type_on_typed_subquestions(
            'StarRating', 'numStars', int, optional=True,
            default=self.default_numStars)

        # numStars is strictly positive
        def range_test(subq, subqname):
            error_msg = ("'numStars' in {} is not "
                         "strictly positive").format(subqname)
            numStars = subq.get('numStars')
            if numStars is None:
                return
            self.assertGreaterEqual(numStars, 1, error_msg)

        self._test_on_typed_subquestions('StarRating', range_test)

    def test_starRating_stepSize(self):
        self._test_presence_and_type_on_typed_subquestions(
            'StarRating', 'stepSize', float, optional=True,
            default=self.default_stepSize)

        # stepSize is strictly positive
        def range_test(subq, subqname):
            error_msg = ("'stepSize' in {} is not "
                         "strictly positive").format(subqname)
            stepSize = subq.get('stepSize')
            if stepSize is None:
                return
            self.assertGreater(stepSize, 0.0, error_msg)

        self._test_on_typed_subquestions('StarRating', range_test)

    def test_starRating_initialRating(self):
        self._test_presence_and_type_on_typed_subquestions(
            'StarRating', 'initialRating', float, optional=True,
            default=self.default_initialRating)

        # initialRating is between 0.0 and numStars
        def range_test(subq, subqname):
            error_msg = ("'initialRating' in {} is not "
                         "between 0.0 and numStars").format(subqname)
            initialRating = subq.get('initialRating')
            numStars = subq.get('numStars', self.default_numStars)
            if initialRating is None:
                return
            self.assertGreaterEqual(initialRating, 0.0, error_msg)
            self.assertLessEqual(initialRating, numStars, error_msg)

        self._test_on_typed_subquestions('StarRating', range_test)


class ConsistencyTestCase(LoadedParametersTestCase):

    description = "Checking general consistency of parameters"

    def test_unique_names(self):
        # Question names are unique across questions
        names = set([])
        for q in self.params['questions']:
            n = q['name']
            if n in names:
                self.fail(("'{}' appears multiple times as a "
                           "question name").format(n))
            names.add(n)

    def test_slots(self):
        # Gather some information
        nSlotsPerProbe = self.params['nSlotsPerProbe']
        slots = set([])
        positioned = set([])
        random = set([])
        for q in self.params['questions']:
            s = q['slot']
            slots.add(s)
            try:
                int(s)
            except ValueError:
                random.add(s)
            else:
                positioned.add(int(s))

        # There are enough groups to fill all the slots
        self.assertGreaterEqual(
            len(slots), nSlotsPerProbe,
            ("There are too few defined groups of questions ({0}) compared "
             "to nSlotsPerProbe ({1})").format(len(slots), nSlotsPerProbe))

        # There aren't too many positioned groups
        self.assertLessEqual(
            len(positioned), nSlotsPerProbe,
            ("There are strictly more predefined-position groups ({0}) than "
             "nSlotsPerProbe ({1}), that's too many, they won't "
             "fit").format(len(positioned), nSlotsPerProbe))

        # If there are some random groups, they will be used eventually
        if len(random):
            self.assertLess(len(positioned), nSlotsPerProbe,
                            ("There are as many as or more "
                             "predefined-position groups of questions ({0}) "
                             "than nSlotsPerProbe ({1}): none of the "
                             "random-position groups will ever be "
                             "used").format(len(positioned), nSlotsPerProbe))

        # Positioned groups don't wrap around the number of slots, and don't
        # overlap each other when defined negatively versus positively
        corrected_positions = set([])
        for s in positioned:
            if s >= 0:
                self.assertLess(s, nSlotsPerProbe,
                                ("Some group positions are greater than the "
                                 "number of slots (remember indices start "
                                 "at 0)"))
                self.assertNotIn(s, corrected_positions,
                                 ("Some positive and negative group "
                                  "positions represent the same position "
                                  "({0} and {1}), use either one or the "
                                  "other").format(s, s - nSlotsPerProbe))
                corrected_positions.add(s)
            else:
                self.assertGreaterEqual(s, - nSlotsPerProbe,
                                        ("Some group positions are lower than"
                                         " -nSlotsPerProbe, don't try to wrap "
                                         "around backwards"))
                self.assertNotIn(s + nSlotsPerProbe, corrected_positions,
                                 ("Some positive and negative group "
                                  "positions represent the same position "
                                  "({0} and {1}), use either one or the "
                                  "other").format(s, s + nSlotsPerProbe))
                corrected_positions.add(s + nSlotsPerProbe)

    def test_delays(self):
        minDelay = self.params['schedulingMinDelay']
        meanDelay = self.params['schedulingMeanDelay']

        # meanDelay is greater than minDelay
        self.assertGreater(meanDelay, minDelay,
                           ("schedulingMeanDelay ({0}) is less than (or "
                            "equal to) schedulingMinDelay "
                            "({1})").format(meanDelay, minDelay))

        # meanDelay is reasonably large
        self.assertGreater(meanDelay, 5 * 60,
                           ("schedulingMeanDelay ({}) is very small! "
                            "(Less than 5 minutes)"))


class bcolors(object):

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def strip_stacktrace(trace):
    trace = trace[trace.index('\n'):]
    trace = trace[trace.index('\n'):]
    trace = trace[trace.index('\n'):]
    return trace[trace.index(':') + 2:].rstrip('\n')


def green(s):
    return bcolors.OKGREEN + s + bcolors.ENDC


def red(s):
    return bcolors.FAIL + s + bcolors.ENDC


def blue(s):
    return bcolors.OKBLUE + s + bcolors.ENDC


if __name__ == '__main__':
    # Make sure we have a single argument
    if len(sys.argv) != 2:
        sys.exit('Usage: {} file-to-validate'.format(
            os.path.split(sys.argv[0])[1]))
    filename = sys.argv[1]
    basefilename = os.path.split(filename)[1]
    # Don't pass on the argument to unittest
    sys.argv = sys.argv[:1]

    # Our test cases and encouragements
    test_cases = [JSONTestCase, RootTestCase, QuestionsTestCase,
                  QuestionDetailsTestCase, SubQuestionsTestCase,
                  ConsistencyTestCase]
    ok_texts = ['Yep!', 'Ok!', 'Great!', 'Brilliant!', 'Fantastic!',
                'Perfect!', 'Good!', 'Right you are!', 'Well done!']
    shuffle(ok_texts)

    # Error flag
    error = False

    # Say hello
    hello = "Validating '{}' against grammar version 2".format(basefilename)
    print
    print hello
    print "-" * len(hello)
    print

    for tc, ok in zip(test_cases, ok_texts):
        sys.stdout.write(tc.description + " ... ")
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(tc)
        res = unittest.TestResult()
        suite.run(res)
        if len(res.errors) or len(res.failures):
            error = True
            sys.stdout.write(red('Arg, wrong') + '\r\n')
            print
            sys.stdout.write(blue("Here's all the information "
                                  "I've got for you:") + '\r\n')

            for k, e in enumerate(res.errors):
                print
                print "Error #{}".format(k + 1)
                print "--------"
                pprint(e)

            for k, f in enumerate(res.failures):
                print
                print "Failure #{}".format(k + 1)
                print "----------"
                print strip_stacktrace(f[1])

            break
        else:
            sys.stdout.write(green(ok) + '\r\n')

    print
    if error:
        sys.stdout.write(red("*** Well, there was an error.") + '\r\n')
        sys.stdout.write(red("*** It happens. Try again :-)") + '\r\n')
        sys.exit(1)
    else:
        sys.stdout.write(green("*** You're good to go!") + '\r\n')
        sys.exit(0)
