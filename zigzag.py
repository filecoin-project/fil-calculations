# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11, 2019

Based on @nicola's ZigZag calculator: https://observablehq.com/d/51563fc39810b60d

@author: @redransil
"""

# Make a zigzag object and change default settings if desired
# Functions below calculate time 
# Energy requirements include processor but not the rest of system
    # (cooling, memory, disk, etc)

import math as math

class zigzag:
    
    def __init__(self):
        
        # Setting variables to default values
        self.layers = 10
        self.baseDegree = 10
        self.expansionDegree = 6
        self.slothIter = 0
        self.challenges = 200 #challenges per layer
        self.size = 1048576
        self.processorPower = 165 # watts
        
        # Hash functions can be pedersen or blake2s
        self.kdfFunction = 'blake2s'
        self.merkleTreeFunction = 'pedersen'
        
        # These dicts are used to store params for the hash functions
        self.hashConstraints = {
                'pedersen':1324,
                'blake2s':10324
                }
        
        self.time = {
                'pedersen':17.993/1000000,
                'blake2s':104.28/1000000000
                }
        
        self.slothTime = 8.0906/1000000
        
        # Benchmark, @porcuquine system using Bellman SNARK
        # units of seconds per constraint
        self.constraintTime = 0.01469 / 1000

        
    def nodes(self):
        return self.size*1024/32
    
    def merkleTreeTime(self):
        return (self.nodes()-1)*self.time[self.merkleTreeFunction]
    
    def report(self):
        
        # Prints all the variables for this zigzag
        print('Layers: '+ str(self.layers))
        print('Base degree: '+ str(self.baseDegree))
        print('Expansion degree: '+ str(self.expansionDegree))
        print('Sloth iterations: '+ str(self.slothIter))
        print('Challenges per layer: '+ str(self.challenges))
        print('Size: '+ str(self.size)+' KiB')
        print('KDF hash function: '+ self.kdfFunction)
        print('Merkle Tree hash function: '+ self.merkleTreeFunction)
        print('Processor power dissipation: '+ str(self.processorPower)+' W')
        
    def replicate_min(self):
        # time to do the non-parallelizable key derivation (lower bound)
        nodes = self.nodes()
        parents = (self.baseDegree + self.expansionDegree)
        parentsHashing = ((parents + 1) / 2) * self.time[self.kdfFunction]
        kdfTime = parentsHashing * nodes * self.layers
        sloth = self.slothIter * self.slothTime * nodes * self.layers
        return kdfTime + sloth
      
        
    def replicate_max(self):
        # key derivation (replicate_min) plus merkle tree construction
        # is upper bound because assumes no parallelization on merkle tree
        replicationTime = self.replicate_min()
        merkleTree = self.merkleTreeTime() * (self.layers+1)
        return replicationTime + merkleTree
        
    def replicate_energy(self):
        # returns in Wh
        # Use replicate_max time: even if you parallelize, you're still running
        # for this amount of cumulative time across all processors
        # for reference, one BTC transaction uses ~430 kWh
        # one household uses ~10 kWh/year
        replicate_time_hours = self.replicate_max()/3600
        return replicate_time_hours*self.processorPower
        
    def zigZagSNARK_constraints(self):
        # Returns number of constraints to be proved
        # parallel is binary, 1 for parallelized 0 for not
        
        # inclusion proofs
        parents = (self.baseDegree + self.expansionDegree)
        inclusionProofPerChallenge = parents + 2 # 1 is replica, 1 is data
        inclusionProofsPerLayer = inclusionProofPerChallenge * self.challenges
        inclusionProofsTotal = inclusionProofsPerLayer * self.layers
        
        # Find relevant number of inculsion proof constraints, based on parallel vs not
        inclusionProof = math.log2(self.nodes())*self.hashConstraints[self.merkleTreeFunction]
            
        # Total number of inclusion proof constraints
        inclusionProofsConstraints = inclusionProofsTotal * inclusionProof
  
        # kdf  
        parentsHashing = ((parents + 1) / 2) * self.hashConstraints[self.kdfFunction]
        kdfConstraints = parentsHashing * self.challenges * self.layers
        
        # encode
        slothConstraints = self.slothIter * 3 * self.challenges * self.layers
        
        return inclusionProofsConstraints + kdfConstraints + slothConstraints
    
    def zigZagSNARK_time(self):
        
        return self.constraintTime * self.zigZagSNARK_constraints()
    
    def zigZagSNARK_energy(self):
        # returns in Wh
        # Using the non-parallelizable version of constraint estimates
        # This has to be wrong; is giving GWh/GB
        zigZagSNARK_time_hours = self.zigZagSNARK_time()/3600
        return zigZagSNARK_time_hours*self.processorPower
    
    
    
    
    
    
    
    