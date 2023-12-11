#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) [YEAR] [YOUR NAME], [YOUR EMAIL]
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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
"""
Description of this extension
"""

import inkex
from simplepath import *
from lxml import etree
from inkex.elements import Polyline
from inkex.elements import Rectangle, PathElement


def vdashed(deltay, dashlength, dashgap):
    # counter, dashlength, dashgap are always positive
    # truecounter, on, off can be positive or negative depending on direction
    s = ''
    on = dashlength
    off = dashgap
    counter = deltay
    truecounter = deltay

    if counter < 0:
        on = -on
        off = -off
        counter = -counter

    while True:
        if counter < dashlength:
            s = s + f'v{truecounter}'
            break

        s = s + f'v{on} '
        counter -= dashlength
        truecounter -= on

        if counter < dashgap:
            s = s + f'm0 {truecounter}'
            break

        s = s + f'm0 {on} '
        counter -= dashgap
        truecounter -= off
    return s


def hdashed(deltaX, dashL, dashRatio=.5):
    positiveDelta = deltaX if deltaX > 0 else -deltaX
    numDashes = positiveDelta * dashRatio // dashL
    if numDashes == 0:
        return None
    spaceForGaps = positiveDelta - dashL * numDashes
    gapL = spaceForGaps / (numDashes + 1)

    dashValue = dashL if deltaX > 0 else -dashL
    gapValue = gapL if deltaX > 0 else -gapL

    s = ''
    distanceTraveled = 0
    for index in range(numDashes):
        s += f'm{gapValue},0 h{dashValue} '
        distanceTraveled += dashValue + gapValue

    remainingDistance = deltaX - distanceTraveled
    s += f'm{remainingDistance},0'
    return s


class CardstockBoxExtension(inkex.GenerateExtension):
    def add_arguments(self, pars):
        pars.add_argument("--units", type=str, dest="units", default='cm')
        pars.add_argument("--width", type=float, dest="width", default=10)
        pars.add_argument("--height", type=float, dest="height", default=10)
        pars.add_argument("--depth", type=float, dest="depth", default=10)


    def createLines(self):
        w = self.svg.unittouu(str(self.options.width) + self.options.units)
        h = self.svg.unittouu(str(self.options.height) + self.options.units)
        d = self.svg.unittouu(str(self.options.depth) + self.options.units)
        tabdepth = d * 4/5
        taboffset = d * 1/4
        lidcut = taboffset
        lidradius = tabdepth*2/3
        fingerslotradius = self.svg.unittouu('.85cm')
        # el.set_path(f'M 0,0 {self.getVerticalDashedLine(-h, 1, 1)} h{d + w + d} {self.getVerticalDashedLine(h, 1, 1)} h{-(d + w + d)}')

        leftSideScoreA = PathElement()
        leftSideScoreA.set_path(f'M{d},0 {vdashed(h, 1, 1)} {vdashed(d, 1, 1)}')
        leftSideScoreA.style = self.style
        
        middleFold1 = PathElement()
        middleFold1.set_path(f'M{d},{h + d} {hdashed(w, 1)}')
        middleFold1.style = self.style
        
        middleFold2 = PathElement()
        middleFold2.set_path(f'M{d + w},{h} {hdashed(-w, 1)}')
        middleFold2.style = self.style

        leftSideScoreB = PathElement()
        leftSideScoreB.set_path(f'M{d},{h + d} {vdashed(h - lidcut, 1, 1)} v{lidcut}')
        leftSideScoreB.style = self.style

        topFold2 = PathElement()
        topFold2.set_path(f'M{d},{h + d + h + d} h{lidcut} {hdashed(w - 2*lidcut, 2)} h{lidcut}')
        topFold2.style = self.style

        topFold1 = PathElement()
        topFold1.set_path(f'M{d + w + d},{h + d + h} {hdashed(-d, 3)} {hdashed(-w, 1, 1)} {hdashed(-d, 3)}')
        topFold1.style = self.style
        
        topLidHelperFold = PathElement()
        topLidHelperFold.set_path(f'M{d},{h + d + h - lidcut} {hdashed(w, 4, .3)}')
        topLidHelperFold.style = self.style

        rightSideScore = PathElement()
        rightSideScore.set_path(f'M{d + w},{h + d + h} v{-lidcut} {vdashed(-(h - lidcut), 1, 1)} {vdashed(-d, 1, 1)} {vdashed(-h, 1, 1)}')
        rightSideScore.style = self.style

        cutLine = PathElement()
        cutLine.set_path(f'M{d},0 h{-d} v{h} h{d} l{-tabdepth} {taboffset} v{d - taboffset*2} l{tabdepth} {taboffset} h{-d} v{h + tabdepth} \
                    h{d - taboffset} l{taboffset} {-tabdepth} v{d} \
                    v{tabdepth - lidradius} a{lidradius},{lidradius},0,0,0,{lidradius},{lidradius} h{w - lidradius*2} a{lidradius},{lidradius},0,0,0,{lidradius},{-lidradius} v{-(tabdepth - lidradius)} \
                    v{-d} l{taboffset} {tabdepth} h{d - taboffset} \
                    v{-tabdepth} v{-h} h{-d} l{tabdepth} {-taboffset} v{-d + taboffset*2} l{-tabdepth} {-taboffset} h{d} v{-h} \
                    h{-d} h{-(w/2 - fingerslotradius)} a{fingerslotradius} {fingerslotradius} 0 0 1 {-2*fingerslotradius} 0 h{-(w/2 - fingerslotradius)}')
                    # h{d - taboffset} l{taboffset} {-tabdepth} v{d} l{taboffset} {tabdepth} h{w - taboffset*2} l{taboffset} {-tabdepth} v{-d} l{taboffset} {tabdepth} h{d - taboffset} \
                    # h{-d} h{-(w/2 - taboffset)} v{taboffset} h{-2*taboffset} v{-taboffset} h{-(w/2 - taboffset)}')
        cutLine.style = self.style

        return [leftSideScoreA, middleFold1, middleFold2, leftSideScoreB, topFold2, topFold1, rightSideScore, cutLine]

    def generate(self):
        # https://inkscapetutorial.org/shape-classes.html
        # el1 = Rectangle(x='10', y='60', width='30', height='20')
        # el2 = Rectangle.new(50, 60, 30, 20)

        self.style = {'fill' : 'none', 'stroke' : '#000000', 
                    'stroke-width' : '0.264583'}
        layer = self.svg.get_current_layer()
        for line in self.createLines():
            yield line


if __name__ == '__main__':
    CardstockBoxExtension().run()
