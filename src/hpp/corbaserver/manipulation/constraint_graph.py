#!/usr/bin/env python
#
# Copyright (c) 2014 CNRS
# Author: Joseph Mirabel
#
# This file is part of hpp-manipulation-corba.
# hpp-manipulation-corba is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version.
#
# hpp-manipulation-corba is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Lesser Public License for more details.  You should have
# received a copy of the GNU Lesser General Public License along with
# hpp-manipulation-corba.  If not, see
# <http://www.gnu.org/licenses/>.

## Definition of a constraint graph.
#
#  This class wraps the Corba client to the server implemented by
#  libhpp-manipulation-corba.so
#
#  Some method implemented by the server can be considered as private. The
#  goal of this class is to hide them and to expose those that can be
#  considered as public.

from subprocess import Popen

class ConstraintGraph (object):
    dotCmd = ['dot', '-Tpdf']
    pdfviewCmd = ['evince']

    def __init__ (self, robot, graphName):
        self.client = robot.client.manipulation
        self.clientBasic = robot.client.basic
        self.graph = robot.client.manipulation.graph
        self.name = graphName
        self.nodes = dict ()
        self.edges = dict ()
        self.graphId = self.graph.createGraph (graphName)
        self.subGraphId = self.graph.createSubGraph (graphName + "_sg")

    def display (self, dotOut = '/tmp/constraintgraph.dot', pdfOut = '/tmp/constraintgraph.pdf'):
        self.client.manipulation.graph.display (dotOut)
        dotCmd = self.dotCmd[:]
        dotCmd.append ('-o' + dotOut)
        dotCmd.append (pdfOut)
        dot = Popen (self.dotCmd)
        dot.wait ()
        pdfviewCmd = self.pdfviewCmd[:]
        pdfviewCmd.append (pdfOut)
        Popen (pdfviewCmd)

    def createNode (self, node)
        '''
        Create one node if node is a string and several if node is a list of string.
        The order is important. The first should be the most restrictive one as a configuration
        will be in the first node for which the constraint are satisfied.
        '''
        if type (node) is str:
            node = [node]
        for n in node:
            self.nodes [n] = self.graph.createNode (self.subGraphId, n)

    def createEdge (self, nodeFrom, nodeTo, name, weight = 1, isInNodeFrom = None):
        if isInNodeFrom is None:
            isInNodeFrom = (self.nodes[nodeFrom] > self.nodes[nodeTo])
        self.edges [name] =\
            self.graph.createEdge (self.nodes[nodeFrom], self.nodes[nodeTo], name, weight, isInNodeFrom)

    def createWaypointEdge (self, nodeFrom, nodeTo, name, nb = 1, weight = 1, isInNodeFrom = None):
        if isInNodeFrom is None:
            isInNodeFrom = (self.nodes[nodeFrom] > self.nodes[nodeTo])
        elmts = self.graph.createWaypointEdge (self.nodes[nodeFrom], self.nodes[nodeTo], name, nb, weight, isInNodeFrom)
        for e in elmts.edges:
            self.edges [e.name] = e.id
        for n in elmts.nodes:
            self.nodes [n.name] = n.id
        return elmts

    def createGrasp (self, name, gripper, handle, passiveJoints = None):
        self.client.problem.createGrasp (name, gripper, handle)
        if passiveJoints is not None:
            self.client.problem.createGrasp (name + "_passive", gripper, handle)
            self.clientBasic.problem.setPassiveDofs (name + "_passive", passiveJoints)
