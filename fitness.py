#!/usr/bin/env python
#
#   Copyright (C) 2008  Don Smiley  ds@sidorof.com

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

#   See the LICENSE file included in this archive
#

"""
This module implements the fitness components for grammatical evolution.

"""
import random
import math

MAX = 'max'
MIN = 'min'
CENTER = 'center'
FITNESS_TYPES = [MAX, MIN, CENTER]

class FitnessList(list):
    """
    This class maintains a list of fitness values per generation.  It is a
    subclassed list to maintain information regarding whether fitness values
    should be maximized, minimized or centered around zero.  By holding that
    information, when the fitness list is given to a fitness evaluation or
    replacement object, it can configure itself automatically to conform to the
    appropropriate characteristics for the class.

    """

    def __init__(self, fitness_type, target_value=None):
        """
        This function initializes and accepts the fitness type.  Optionally it
        accepts the target value.  The target value is the value where
        execution of the evolutionary process halts upon attaining the goal.

        """

        list.__init__(self)
        self._fitness_type = None
        self._target_value = target_value
        self.set_fitness_type(fitness_type)
        if target_value is not None:
            self.set_target_value(target_value)

    def set_fitness_type(self, fitness_type):
        """
        This function sets the fitness type.

        Accepted fitness types are 'min', 'max', or 'center'.

        """

        if fitness_type not in FITNESS_TYPES:
            raise ValueError("""
                Fitness type must be either min, max, or
                center, not %s""" % (fitness_type))

        self._fitness_type = fitness_type

    def get_fitness_type(self):
        """
        This function returns the fitness type, such as 'min',
        'max', or 'center'.

        """

        return self._fitness_type

    def set_target_value(self, target_value):
        """
        This function sets the target value.

        """

        if not isinstance(target_value, float):
            raise ValueError("The target value must be a float")
        self._target_value = target_value

    def get_target_value(self):
        """
        This function returns the target value.

        """

        return self._target_value

    def min_value(self):
        """
        This function returns the minimum value in the list.

        """

        values = [value for value in self]
        return min(values)

    def max_value(self):
        """
        This function returns the maximum value in the list.

        """

        values = [value for value in self]
        return max(values)

    def best_value(self):
        """
        This function returns the best value in the list on the basis of the
        objective of the fitness list. For example, when trying to maximize a
        fitness value, it would return the maximum value.

        """

        if self._fitness_type == MIN:
            return self.min_value()
        elif self._fitness_type == MAX:
            return self.max_value()
        elif self._fitness_type == CENTER:
            sortlist = self.sorted()
            return sortlist[0][0]

    def worst_value(self):
        """
        This function returns the worst value in the list on the basis of the
        objective of the fitness list. For example, when trying to maximize a
        fitness value, it would return the minimum value.

        """

        if self._fitness_type == MIN:
            return self.max_value()
        elif self._fitness_type == MAX:
            return self.min_value()
        elif self._fitness_type == CENTER:
            sortlist = self.sorted()
            return sortlist[-1][0]

    def min_member(self):
        """
        This function returns the member with the minimum value.

        """

        if self._fitness_type == MIN:
            return self.sorted()[0][1]
        elif self._fitness_type == MAX:
            return self.sorted()[-1][1]
        elif self._fitness_type == CENTER:
            return self.sorted()[0][1]

    def max_member(self):
        """
        This function returns the member with the maximum value.

        """

        if self._fitness_type == MIN:
            return self.sorted()[-1][1]
        elif self._fitness_type == MAX:
            return self.sorted()[0][1]
        elif self._fitness_type == CENTER:
            return self.sorted()[-1][1]

    def best_member(self):
        """
        This function returns the member with the best value based upon the
        criteria of the fitness type.

        """

        if self._fitness_type == MIN:
            return self.min_member()
        elif self._fitness_type == MAX:
            return self.max_member()
        elif self._fitness_type == CENTER:
            return self.min_member()

    def worst_member(self):
        """
        This function returns the member with the worst value based upon the
        criteria of the fitness type.

        """

        if self._fitness_type == MIN:
            return self.max_member()
        elif self._fitness_type == MAX:
            return self.min_member()
        elif self._fitness_type == CENTER:
            return self.max_member()

    def mean(self):
        """
        This function returns the mean fitness value.

        """

        total = 0.0
        for item in self:
            total += item[0]
        return total / float(len(self))

    def median(self):
        """
        This function returns the median fitness value.

        """

        sort_list = self.sorted()
        length = len(self)
        half = length / 2
        if half - length % 2 == 0:
            return (sort_list[half - 1][0] + sort_list[half][0]) / 2.0
        else:
            return sort_list[half][0]

    def stddev(self):
        """
        This function returns the standard deviation of fitness values.

        """

        total = 0.0
        mean = self.mean()
        for item in self:
            total += pow(item[0] - mean, 2.0)
        return pow(total / (float(len(self)) - 1.0), .5)

    def sorted(self):
        """
        This function returns the fitness list sorted in fitness order
        according to the fitness type.

        """

        if self._fitness_type == MIN:
            new_list = [i for i in self]
            new_list.sort()
        elif self._fitness_type == MAX:
            new_list = [i for i in self]
            new_list.sort(reverse=True)
        elif self._fitness_type == CENTER:
            new_list = [[abs(i[0]), i[1]] for i in self]
            new_list.sort()
        return new_list


class Selection(object):
    """
    This is the base class for methods appropriate for assessing the fitness
    landscape.  _selection_type refers to the technique associated with the
    selection method that is subclassed.

    """

    def __init__(self, selection_list=None):
        self._selection_type = MAX
        if selection_list:
            self.set_selection_list(selection_list)
        else:
            self._selection_list = None

    def set_selection_list(self, selection_list):
        """
        This function accepts the selection list.  This is the list of fitness
        values that may have been transformed for the selection process.

        """

        if not isinstance(selection_list, list):
            raise ValueError("Selection list is not a list")
        self._selection_list = selection_list

    def set_selection_type(self, selection_type):
        """
        This function accepts the selection type, which must be either 'min'
        or 'max'.  The selection type is used by the subclass to know how to
        manipulate the list to achieve the fitness goals.

        """

        if selection_type not in (MIN, MAX):
            raise ValueError("""
                The selection type must be either '%s' or '%s', not '%s'.
                    """ % (MIN, MAX, selection_type))
        self._selection_type = selection_type

    @staticmethod

    def _roulette_wheel(scale_list):
        """
        This function receives a list that has been scaled so that the sum
        total of the list is 1.0.  This enables a fair use of probability.
        This is a generator that yields a random selection from the list.

        """
        if round(sum(scale_list), 10) != 1.0:
            raise ValueError(
                "The scaled list received does not total 1.0: %s" % (
                    sum(scale_list)))
        cumu = [0.0]
        length = len(scale_list)
        for i in xrange(length):
            cumu.append(scale_list[i] + cumu[-1])

        #   Rewrite for binary search sometime
        for i in xrange(length):
            rand_val = random.random()
            position = 0
            while position < length:
                if cumu[position + 1] > rand_val:
                    yield position
                    break
                position += 1

    def _make_sort_list(self):
        """
        This function sorts the _selection list making it similar to the
        original fitness list, except the the fitness values have been
        adjusted.

        """

        length = len(self._selection_list)
        sort_list = []
        for i in xrange(length):
            sort_list.append([self._selection_list[i], i])
        return sort_list

class Tournament(Selection):
    """
    Selects random tuples and returns either the minimum or maximum.  To speed
    up the rate of selection, use larger tournament sizes, and smaller to slow
    down the process.

    """

    def __init__(self, selection_list=None, tournament_size=None):
        Selection.__init__(self, selection_list)
        self._tournament_size = None
        self.set_tournament_size(tournament_size)
        self._minmax =  None

    def set_tournament_size(self, tournament_size):
        """
        This function accepts the tournament size, which is the number of
        members that will be selected per tournament.

        """

        if tournament_size is not None:
            if not isinstance(tournament_size, int):
                raise ValueError("Tournament size, %s must be an int." % (
                    tournament_size))
            if self._selection_list:
                if tournament_size > len(self._selection_list):
                    raise ValueError("""The tournament size, %s, cannot
                        be larger than the population, %s.""" % (
                        tournament_size, len(self._selection_list)))
        self._tournament_size = tournament_size

    def _set_minmax(self, minmax):
        """
        This function sets whether the selection should minimize or maximize.
        """

        if minmax not in [MIN, MAX]:
            raise ValueError("Must be either 'min' or 'max'")
        self._minmax = minmax

    def select(self):
        """
        The select function provides all the members based upon the class
        algorithm.

        """

        population_size = len(self._selection_list)

        position = 0
        while position < population_size:

            t_list = []
            values = []
            choice = 0
            while choice < self._tournament_size:
                rand_position = random.randint(0, population_size - 1)

                #   Lookup the fitness value
                t_list.append(rand_position)
                values.append(self._selection_list[rand_position])
                choice += 1

            if self._minmax == MAX:
                value = max(values)
            else:
                value = min(values)

            t_winner = t_list[values.index(value)]
            yield t_winner

            position += 1

class Fitness(Selection):
    """
    This class is the prototype for the fitness functions.  The primary job of
    a fitness function is to deal with the list of [fitness value, member no]
    pairs that are generated as a result of a run.

    It also scales and configures the fitness values to be consistent with the
    fitness functions characteristics. For example, if the fitness strategy is
    to minimize values and the Fitness selection strategy maximizes, then the
    fitness values will be converted to -value.  If the fitness strategy
    centers on a value, such as zero, then the values will be converted to the
    absolute distance from that value.

    """

    def __init__(self, fitness_list):
        Selection.__init__(self)
        self._fitness_list = None
        self.set_fitness_list(fitness_list)

    def set_fitness_list(self, fitness_list):
        """
        This function accepts the fitness list.  It is the list of fitness
        values by member number for a population.

        """

        if not isinstance(fitness_list, FitnessList):
            raise ValueError("Fitness_list is not a list")

        self._fitness_list = fitness_list

        if fitness_list.get_fitness_type() == CENTER:
            #   Convert to 1/absolute distance from the target_value
            self._selection_list = []
            length = len(fitness_list)
            for i in xrange(length):
                if fitness_list[i][0] != 0.0:
                    self._selection_list.append(
                        abs(fitness_list[i][0] - \
                        fitness_list.get_target_value()))
                else:
                    self._selection_list.append(0.0)
        else:
            self._selection_list = [item[0] for item in fitness_list]

    @staticmethod

    def _invert(value):
        """
        This method returns the reciprocal of the value.

        """
        if value == 0.0:
            return 0.0
        else:
            return 1.0 / value

    def _scale_list(self):
        """
        This function scales the list to convert for example min to max where
        the selection type warrants it.

        """
        if self._selection_type == MAX and \
            self._fitness_list.get_fitness_type() == MIN:

            inverse = True

        elif self._selection_type == MIN and \
            self._fitness_list.get_fitness_type() == MAX:

            inverse = True

        elif self._selection_type == MAX and \
            self._fitness_list.get_fitness_type() == CENTER:

            inverse = True

        else:
            inverse = False

        if inverse:
            self._selection_list = [self._invert(value)
                for value in self._selection_list]

    def _make_prob_list(self):
        """
        This function aids in calculating probability lists.
        """
        self._scale_list()

        total = sum(self._selection_list)
        if total != 0.0:
            self._selection_list = [value / total
                for value in self._selection_list]


class FitnessProportionate(Fitness):
    """
    The probability of selection is based upon 0.the fitness value of the
    individual relative to the rest of the population.

    Pr(G_i) = f(G_i)/ sum(1 to pop) f(G_i)

    This is the total probability.  Roulette wheel selects individuals
    randomly, highest fitness more likely to be included.

    Note that inherent in this approach is the assumption that the fitness
    value should be as large as possible.

    """

    def __init__(self, fitness_list, scaling_type=None):
        Fitness.__init__(self, fitness_list)
        self.scaling_types = ['linear', 'truncation',
                            'exponential', 'logarithmic']
        self._scaling_type = None
        self.set_scaling_type(scaling_type)
        self._check_minmax()

    def set_scaling_type(self, scaling_type):
        """
        This function accepts the type of scaling that will be performed on
        the data in preparation of building a probability list for the roulette
        selection.

        """
        if not scaling_type in self.scaling_types:
            raise ValueError(
                "Invalid scaling type: %s, valid scaling types are %s" % (
                    scaling_type, self.scaling_types))
        self._scaling_type = scaling_type

    def _check_minmax(self):
        """
        If selection of fitness is with proportions, then they must all be the
        same sign.  Also, negative numbers do not mix with logs.

        """

        if min(self._selection_list) < 0.0 < max(self._selection_list):
            raise ValueError("Inconsistent signs in selection list")

        if min(self._selection_list) < 0.0 and \
                self._scaling_type == 'logarithmic':
            raise ValueError("Negative numbers cannot be used with logs.")

    def select(self, param=None):
        """
        The select function provides all the members based upon the class
        algorithm.

        """

        if not self._selection_list:
            raise ValueError("No fitness list to scale")

        if self._scaling_type == "linear":
            self._make_prob_list()

        elif self._scaling_type == "exponential":
            if param:
                exponent = param[0]
            else:
                exponent = 2.0
            self._selection_list = [pow(item, exponent)
                for item in self._selection_list]
            self._make_prob_list()

        elif self._scaling_type == "logarithmic":
            self._selection_list = [math.log(item)
                for item in self._selection_list]
            self._make_prob_list()

        elif self._scaling_type == "truncation":
            if param:
                trunc = param
            else:
                raise ValueError("""
                    Truncation scaling requires a truncation value""")
            length = len(self._selection_list)
            for i in xrange(length):
                if self._selection_list[i] < trunc:
                    self._selection_list[i] = 0.0

            self._make_prob_list()
        else:
            #   theoretically the raise error would prevent this
            pass

        #   Now apply to othe roulette wheel
        return self._roulette_wheel(self._selection_list)

class FitnessTournament(Fitness, Tournament):
    """
    This class selects the fitness based on a tournament.

    """

    def __init__(self, fitness_list, tournament_size=2):
        Tournament.__init__(self)
        Fitness.__init__(self, fitness_list)
        if self._fitness_list.get_fitness_type() == MAX:
            minmax = MAX
        else:
            minmax = MIN
        self._set_minmax(minmax)
        self.set_tournament_size(tournament_size)

class FitnessElites(Fitness):
    """
    This class selects the highest or lowest fitness depending upon what is
    desired.  The fitness list is put into the selection list in this case so
    that once the sorting for rank takes place, the member numbers are still
    available.

    """

    def __init__(self, fitness_list, rate):
        Fitness.__init__(self, fitness_list)
        self._rate = None
        self.set_rate(rate)
        self.set_selection_type(MIN)

    def set_rate(self, rate):
        """
        This function accepts a value greater than 0 and less than or equal to
        1.0.  It is the percentage of members from a list sorted by best
        values.

        """

        if not isinstance(rate, float) and 0.0 < rate <= 1.0:
            raise ValueError(
                "The rate, %s, should between 0.0 and 1.0" % (
                    rate))
        self._rate = rate

    def select(self):
        """
        The select function provides all the members based upon the class
        algorithm.

        """

        self._scale_list()
        sort_list = self._make_sort_list()

        sort_list.sort()
        elites = int(round(self._rate * float(len(sort_list))))
        for item in sort_list[:elites]:
            yield item[1]


class FitnessLinearRanking(Fitness):
    """
    This class selects fitness on the basis of rank with other members.  Only
    the position in the ranking matters rather than the fitness value.  The
    probability curve is calculated on that basis. Then roulette selection
    takes place.

    This uses the formula for the probability curve of:
    Probability = 1 / population * (worstfactor + (bestfactor -
    worstfactor) * (rank(Member) - 1) / (population - 1))

    When bestfactor + worstfactor = 2 and 1 <= worstfactor <= 2,
    the best individual produces up to twice the children as the average.

    """

    def __init__(self, fitness_list, worstfactor, bestfactor):
        Fitness.__init__(self, fitness_list)
        self._worstfactor = None
        self._bestfactor = None
        self.set_worstfactor(worstfactor)
        self.set_bestfactor(bestfactor)

    def set_worstfactor(self, worstfactor):
        """
        This function sets the worst factor.  See the class description for
        more.

        """
        if not isinstance(worstfactor, float):
            raise ValueError("Worstfactor must be a float value.")
        self._worstfactor = worstfactor

    def set_bestfactor(self, bestfactor):
        """
        This function sets the best factor.  See the class description for
        more.

        """

        if not isinstance(bestfactor, float):
            raise ValueError("Bestfactor must be a float value.")
        self._bestfactor = bestfactor

    def select(self):
        """
        The select function provides all the members based upon the class
        algorithm.

        """

        self._scale_list()

        sort_list = self._make_sort_list()

        prob_list = self._linear_ranking(sort_list)

        #   Now this list needs to sorted back into position order
        select_list = []
        length = len(sort_list)
        for i in xrange(length):
            member_no = sort_list[i][1]
            prob = prob_list[i]
            select_list.append([member_no, prob])
        select_list.sort()

        return self._roulette_wheel([item[1] for item in select_list])

    def _linear_ranking(self, sort_list):
        """
        This applies the best and worst factors and assigns the selection
        probability to each rank.

        """

        scale_list = []
        i = 1.0
        length = float(len(sort_list))
        while i < length + 1.0:
            value = 1.0 / length * (self._worstfactor + \
                (self._bestfactor - self._worstfactor) * \
                (i - 1.0) / (length - 1.0))
            scale_list.append(value)
            i += 1.0

        return scale_list

class FitnessTruncationRanking(Fitness):
    """
    This class selects fitness on the basis of rank with other members if
    above a certain rank.  Once above that rank, any member can be selected
    with an equal probability.  The truncation value is entered as a rate and
    converted to a ranking value. For example, if a population has 100 members
    and a truncation value of .2, the truncated ranking will be converted to a
    rank of 20.

    """

    def __init__(self, fitness_list, trunc_rate):
        Fitness.__init__(self, fitness_list)
        self._trunc_rate = None
        self.set_trunc_rate(trunc_rate)
        self.set_selection_type(MIN)

    def set_trunc_rate(self, trunc_rate):
        """
        This function sets the rate, between 0 and 1 that is a hurdle for
        selection.

        """

        if not isinstance(trunc_rate, float) and 0.0 < trunc_rate <= 1.0:
            raise ValueError("Trunc_rate should between 0.0 and 1.0")
        self._trunc_rate = trunc_rate

    def select(self):
        """
        The select function provides all the members based upon the class
        algorithm.

        """

        self._scale_list()
        sort_list = self._make_sort_list()
        sort_list.sort(reverse=True)
        length = len(sort_list)
        cutoff_rank = int(round(self._trunc_rate * length))
        prob_list = []
        for i in xrange(length):
            if i < cutoff_rank:
                prob_list.append(
                    [sort_list[i][1], 1.0 / float(length - cutoff_rank)])
            else:
                prob_list.append([sort_list[i][1], 0.0])

        #   Sort back to member order, and then make list for use by roulette
        prob_list.sort()
        select_list = [item[1] for item in prob_list]
        total = sum(select_list)
        select_list = [item / total for item in select_list]

        return self._roulette_wheel([item for item in select_list])


class Replacement(Fitness):
    """
    This is the base class for the classes that identify which members are to
    be replaced.  It is basically the same as a fitness class, but attempts to
    identify the worst, not the best.

    """

    def __init__(self, fitness_list):
        Fitness.__init__(self, fitness_list)
        self._replacement_count = 0

class ReplacementDeleteWorst(Replacement):
    """
    This class is the mirror image of FitnessElite.  The worst members are
    returned.

    """

    def __init__(self, fitness_list, replacement_count):
        Replacement.__init__(self, fitness_list)

        self.set_replacement_count(replacement_count)
        self.set_selection_type(MIN)

    def set_replacement_count(self, replacement_count):
        """
        This function accepts the number of members to be replaced.

        """
        length = len(self._selection_list)

        if not isinstance(replacement_count, int) or \
            0.0 < replacement_count <= 1.0:
            raise ValueError(
                "Replacement count, %s should between 0 and %s" % (
                  replacement_count, length))
        self._replacement_count = replacement_count

    def select(self):
        """
        select is a generator that yields the members for
        replacement sorted from worst to best. It halts when the replacemnt
        count has been reached.

        """
        self._scale_list()
        sort_list = self._make_sort_list()
        sort_list.sort(reverse=True)
        for item in sort_list[:self._replacement_count]:
            yield item[1]

class ReplacementTournament(Replacement, Tournament):
    """
    This class selects the fitness based on a tournament.

    """

    def __init__(self, fitness_list, tournament_size):
        Tournament.__init__(self)
        Replacement.__init__(self, fitness_list)
        self.set_tournament_size(tournament_size)
        if self._fitness_list.get_fitness_type() == MAX:
            minmax = MIN
        else:
            minmax = MAX
        self._set_minmax(minmax)

