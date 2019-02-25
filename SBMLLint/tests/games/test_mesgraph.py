"""
Tests for Mass Equality Set Graph (MESGraph)
"""
from SBMLLint.common import constants as cn
from SBMLLint.common.reaction import Reaction
from SBMLLint.common.simple_sbml import SimpleSBML
from SBMLLint.games.mesgraph import MESGraph
from SBMLLint.games.som import SOM
from SBMLLint.common import simple_sbml

import numpy as np
import os
import re
import tesbml
import unittest


IGNORE_TEST = False
INITIAL_NODES = 14
INITIAL_EDGES = 0
FINAL_NODES = 6
FINAL_EDGES = 6
UNIUNI0 = 0
UNIUNI1 = 7
UNIUNI2 = 8
UNIMULTI = 2
MULTIUNI = 13
INEQUAL1 = 14
INEQUAL2 = 15
AA = "AA"
CN = "Cn"
DFG = "DFG"
E1 = "E1"
E2 = "E2"
FRU = "Fru"
GLY = "Gly"
MEL = "Mel"
MG = "MG"

#############################
# Tests
#############################
class TestMESGraph(unittest.TestCase):

  def setUp(self):
    self.simple = SimpleSBML()
    self.simple.initialize(cn.TEST_FILE6)
    self.molecules = self.simple.molecules
    self.mesgraph = MESGraph(self.simple)
  
  def testConstructor(self):
    if IGNORE_TEST:
      return
    self.assertEqual(len(self.mesgraph.nodes), INITIAL_NODES)
    self.assertEqual(len(self.mesgraph.edges), INITIAL_EDGES)
    dfg = self.simple.getMolecule(DFG)
    # molecules is a list of one-molecule sets
    molecules = [som.molecules for som in self.mesgraph.nodes]
    self.assertTrue({self.simple.getMolecule(DFG)} in molecules)

  def testInitializeSOMs(self):
    if IGNORE_TEST:
      return
    for node in self.mesgraph.nodes:
      self.assertEqual(type(node), SOM)
  
  def testMakeId(self):
    if IGNORE_TEST:
      return
    identifier = ""
    for key, som in enumerate(self.mesgraph.nodes):
      identifier = identifier + som.identifier
      if key < len(self.mesgraph.nodes)-1:
        identifier = identifier + ";"
    self.assertEqual(identifier, self.mesgraph.identifier)

  def testGetNode(self):
    if IGNORE_TEST:
      return
    aa = self.simple.getMolecule(AA)
    aa_node = self.mesgraph.getNode(aa)
    self.assertEqual(type(aa_node), SOM)
    self.assertEqual(aa_node.molecules, {aa})
  
  def testProcessUniUniReaction(self):
    if IGNORE_TEST:
      return
    self.mesgraph.processUniUniReaction(
        self.simple.reactions[UNIUNI0])
    dfg = self.mesgraph.getNode(self.simple.getMolecule(DFG))
    e1 = self.mesgraph.getNode(self.simple.getMolecule(E1))
    self.assertTrue(self.mesgraph.has_node(dfg))
    self.assertTrue(self.mesgraph.has_node(e1))
    self.assertEqual(dfg, e1)
  
  def testProcessUniMultiReaction(self):
    if IGNORE_TEST:
      return
    unimulti_reaction = self.simple.reactions[UNIMULTI]
    self.mesgraph.processUniMultiReaction(unimulti_reaction)
    prods = [self.mesgraph.getNode(product.molecule) for product in unimulti_reaction.products]
    dfg = self.mesgraph.getNode(self.simple.getMolecule(DFG))
    for prod in prods:
      self.assertTrue(self.mesgraph.has_edge(prod, dfg))
  
  def testProcessMultiUniReaction(self):
    if IGNORE_TEST:
      return
    multiuni_reaction = self.simple.reactions[MULTIUNI]
    self.mesgraph.processMultiUniReaction(multiuni_reaction)
    reacts = [self.mesgraph.getNode(reactant.molecule) for reactant in multiuni_reaction.reactants]
    mel = self.mesgraph.getNode(self.simple.getMolecule(MEL))
    for react in reacts:
      self.assertTrue(self.mesgraph.has_edge(react, mel))
  
  def testAddArc(self):
    if IGNORE_TEST:
      return
    source = [self.simple.getMolecule(FRU), 
        self.simple.getMolecule(GLY)]
    destination = [self.simple.getMolecule(E2)]
    dummy_reaction = self.simple.reactions[INEQUAL2]
    self.mesgraph.addArc(source, destination, dummy_reaction)
    arc1 = [self.mesgraph.getNode(source[0]), 
            self.mesgraph.getNode(destination[0])]
    arc2 = [self.mesgraph.getNode(source[1]), 
            self.mesgraph.getNode(destination[0])]
    self.assertTrue(self.mesgraph.has_edge(arc1[0], arc1[1]))
    self.assertTrue(self.mesgraph.has_edge(arc2[0], arc2[1]))
    reaction_label1 = self.mesgraph.get_edge_data(arc1[0], arc1[1])[cn.REACTION][0]
    reaction_label2 = self.mesgraph.get_edge_data(arc2[0], arc1[1])[cn.REACTION][0]
    self.assertEqual(reaction_label1, dummy_reaction.label)
    self.assertEqual(reaction_label1, reaction_label2)
  
  def testCheckTypeOneError(self):
    if IGNORE_TEST:
      return
    uniuni_reaction1 = self.simple.reactions[UNIUNI1]
    uniuni_reaction2 = self.simple.reactions[UNIUNI2]
    inequality_reaction1 = self.simple.reactions[INEQUAL1]
    inequality_reaction2 = self.simple.reactions[INEQUAL2]
    self.mesgraph.processUniUniReaction(uniuni_reaction1)
    self.mesgraph.processUniUniReaction(uniuni_reaction2)
    aa = self.simple.getMolecule(AA)
    cn = self.simple.getMolecule(CN)
    mg = self.simple.getMolecule(MG)
    self.assertTrue(self.mesgraph.checkTypeOneError((aa, cn), inequality_reaction1))
    self.assertFalse(self.mesgraph.checkTypeOneError((mg, aa), inequality_reaction2))

  # # def testReduce(self):
  # #   if IGNORE_TEST:
  # #     return
  # #   SOM.merge(self.uniuni)
  # #   self.assertFalse(SOM.reduce(self.uniuni))
  # #   self.assertFalse(SOM.reduce(self.multiuni))
  # #   num_reactants = len(self.multimulti.reactants)
  # #   num_products = len(self.multimulti.products)
  # #   reduced_reaction = SOM.reduce(self.multimulti)
  # #   self.assertIsInstance(reduced_reaction, Reaction)
  # #   self.assertEqual(reduced_reaction.category, cn.REACTION_n_n)
  # #   self.assertGreater(num_reactants, len(reduced_reaction.reactants))
  # #   self.assertGreater(num_products, len(reduced_reaction.products))

  # # def _addReactions(self):
  # #   self.simple.add(Reaction(
  # #       self.simple._model.getReaction(UNIUNI)))
  # #   self.simple.add(Reaction(
  # #       self.simple._model.getReaction(MULTIMULTI)))
  # #   self.simple.add(Reaction(
  # #       self.simple._model.getReaction(MULTIUNI)))

  # def testAnalyze(self):
  #   if IGNORE_TEST:
  #     return
  #   self.mesgraph = MESGraph(SOM.soms)
  #   self.mesgraph.analyze(self.simple.reactions)
  #   self.assertEqual(len(self.mesgraph.nodes), FINAL_NODES)
  #   self.assertEqual(len(self.mesgraph.edges), FINAL_EDGES)

if __name__ == '__main__':
  unittest.main()

