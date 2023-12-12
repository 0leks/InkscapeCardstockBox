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


def vdashed(deltaY, dashL, dashRatio=.4):
    positiveDelta = deltaY if deltaY > 0 else -deltaY
    numDashes = int(positiveDelta * dashRatio / dashL)
    if numDashes == 0:
        return None
    spaceForGaps = positiveDelta - dashL * numDashes
    gapL = spaceForGaps / (numDashes + 1)

    dashValue = dashL if deltaY > 0 else -dashL
    gapValue = gapL if deltaY > 0 else -gapL

    s = ''
    distanceTraveled = 0
    for index in range(numDashes):
        s += f'm0,{gapValue} v{dashValue} '
        distanceTraveled += dashValue + gapValue

    remainingDistance = deltaY - distanceTraveled
    s += f'm0,{remainingDistance}'
    return s


def hdashed(deltaX, dashL, dashRatio=.4):
    positiveDelta = deltaX if deltaX > 0 else -deltaX
    numDashes = int(positiveDelta * dashRatio / dashL)
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
        pars.add_argument("--width", type=float, dest="width")
        pars.add_argument("--height", type=float, dest="height")
        pars.add_argument("--depth", type=float, dest="depth")
        pars.add_argument("--fingerslotradius", type=float, dest="fingerslotradius")
        pars.add_argument("--dashlength", type=float, dest="dashlength")
        pars.add_argument("--dashratio", type=float, dest="dashratio")


    def createLines(self):
        w = self.svg.unittouu(str(self.options.width) + self.options.units)
        h = self.svg.unittouu(str(self.options.height) + self.options.units)
        d = self.svg.unittouu(str(self.options.depth) + self.options.units)
        fingerslotradius = self.svg.unittouu(str(self.options.fingerslotradius) + self.options.units)
        dashlength = self.svg.unittouu(str(self.options.dashlength) + 'pt')
        dashratio = self.options.dashratio

        DL = dashlength
        DR = dashratio
        tabdepth = d * 4/5
        taboffset = d * 1/8
        bottomtaboffset = d * 1/8
        lidcut = taboffset * 10/3
        lidhelpercut = tabdepth * 3/5
        lidradius = tabdepth*3/5

        leftSideScoreA = PathElement()
        leftSideScoreA.set_path(f'M{d},0 {vdashed(h, DL, DR)} {vdashed(d, DL, DR)}')
        leftSideScoreA.style = self.style
        
        middleFold1 = PathElement()
        middleFold1.set_path(f'M{d},{h + d} {hdashed(w, DL, DR)}')
        middleFold1.style = self.style
        
        middleFold2 = PathElement()
        middleFold2.set_path(f'M{d + w},{h} {hdashed(-w, DL, DR)}')
        middleFold2.style = self.style

        leftSideScoreB = PathElement()
        leftSideScoreB.set_path(f'M{d},{h + d} {vdashed(h - lidhelpercut, DL, DR)} v{lidhelpercut}')
        leftSideScoreB.style = self.style

        topFold2 = PathElement()
        topFold2.set_path(f'M{d},{h + d + h + d} h{lidcut} {hdashed(w - 2*lidcut, DL, DR)} h{lidcut}')
        topFold2.style = self.style

        topFold1 = PathElement()
        topFold1.set_path(f'M{d + w + d},{h + d + h} {hdashed(-d, DL, DR)} {hdashed(-w, DL, DR)} {hdashed(-d, DL, DR)}')
        topFold1.style = self.style
        
        topLidHelperFold = PathElement()
        topLidHelperFold.set_path(f'M{d},{h + d + h - lidhelpercut} {hdashed(w, DL, DR*3/4)}')
        topLidHelperFold.style = self.style

        rightSideScore = PathElement()
        rightSideScore.set_path(f'M{d + w},{h + d + h} v{-lidhelpercut} {vdashed(-(h - lidhelpercut), DL, DR)} {vdashed(-d, DL, DR)} {vdashed(-h, DL, DR)}')
        rightSideScore.style = self.style

        cutLine = PathElement()
        cutLine.set_path(f'M{d},0 h{-d} v{h} h{d} l{-tabdepth} {bottomtaboffset} v{d - bottomtaboffset*2} l{tabdepth} {bottomtaboffset} h{-d} v{h + tabdepth} \
                    h{d - taboffset} l{taboffset} {-tabdepth} v{d} \
                    v{tabdepth - lidradius} a{lidradius},{lidradius},0,0,0,{lidradius},{lidradius} h{w - lidradius*2} a{lidradius},{lidradius},0,0,0,{lidradius},{-lidradius} v{-(tabdepth - lidradius)} \
                    v{-d} l{taboffset} {tabdepth} h{d - taboffset} \
                    v{-tabdepth} v{-h} h{-d} l{tabdepth} {-bottomtaboffset} v{-d + bottomtaboffset*2} l{-tabdepth} {-bottomtaboffset} h{d} v{-h} \
                    h{-d} h{-(w/2 - fingerslotradius)} a{fingerslotradius} {fingerslotradius} 0 0 1 {-2*fingerslotradius} 0 h{-(w/2 - fingerslotradius)}')
        cutLine.style = self.style

        return [leftSideScoreA, middleFold1, middleFold2, leftSideScoreB, topFold2, topFold1, topLidHelperFold, rightSideScore, cutLine]


    def generate(self):
        # https://inkscapetutorial.org/shape-classes.html
        self.style = {'fill' : 'none', 'stroke' : '#000000', 
                    'stroke-width' : '0.264583'}
        for line in self.createLines():
            yield line


if __name__ == '__main__':
    CardstockBoxExtension().run()
