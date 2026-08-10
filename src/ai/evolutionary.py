"""Evolutionary Algorithm-based Trading System"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
from copy import deepcopy
import random
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class Chromosome:
    """Trading strategy chromosome (genetic representation)"""
    genes: Dict[str, float]  # Strategy parameters
    fitness: float = 0.0
    
    def __lt__(self, other):
        return self.fitness > other.fitness  # For sorting (higher fitness first)


class EvolutionarySystem:
    """Evolutionary algorithms for optimizing trading strategies"""
    
    def __init__(self, population_size: int = 50, generations: int = 100):
        """
        Initialize evolutionary system.
        
        Args:
            population_size: Size of population
            generations: Number of generations
        """
        self.population_size = population_size
        self.generations = generations
        self.population: List[Chromosome] = []
        self.best_chromosomes: List[Chromosome] = []
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
        self.elite_size = max(2, int(population_size * 0.1))
    
    def initialize_population(self, gene_ranges: Dict[str, Tuple]) -> None:
        """
        Initialize population with random genes.
        
        Args:
            gene_ranges: Dictionary of gene names and (min, max) ranges
        """
        self.population = []
        for _ in range(self.population_size):
            genes = {}
            for gene_name, (min_val, max_val) in gene_ranges.items():
                genes[gene_name] = np.random.uniform(min_val, max_val)
            
            self.population.append(Chromosome(genes=genes))
        
        logger.info(f"Initialized population of {self.population_size} chromosomes")
    
    def evaluate_fitness(self, fitness_func: Callable) -> None:
        """
        Evaluate fitness of all chromosomes.
        
        Args:
            fitness_func: Function to calculate fitness
        """
        for chromosome in self.population:
            chromosome.fitness = fitness_func(chromosome.genes)
    
    def selection(self, tournament_size: int = 3) -> Chromosome:
        """
        Tournament selection.
        
        Args:
            tournament_size: Size of tournament
        
        Returns:
            Selected chromosome
        """
        tournament = random.sample(self.population, tournament_size)
        return max(tournament, key=lambda x: x.fitness)
    
    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """
        Crossover two chromosomes.
        
        Args:
            parent1: First parent
            parent2: Second parent
        
        Returns:
            Tuple of offspring
        """
        if random.random() > self.crossover_rate:
            return deepcopy(parent1), deepcopy(parent2)
        
        offspring1_genes = {}
        offspring2_genes = {}
        
        for gene_name in parent1.genes:
            if random.random() < 0.5:
                offspring1_genes[gene_name] = parent1.genes[gene_name]
                offspring2_genes[gene_name] = parent2.genes[gene_name]
            else:
                offspring1_genes[gene_name] = parent2.genes[gene_name]
                offspring2_genes[gene_name] = parent1.genes[gene_name]
        
        return Chromosome(genes=offspring1_genes), Chromosome(genes=offspring2_genes)
    
    def mutate(self, chromosome: Chromosome, gene_ranges: Dict[str, Tuple]) -> Chromosome:
        """
        Mutate chromosome.
        
        Args:
            chromosome: Chromosome to mutate
            gene_ranges: Gene value ranges
        
        Returns:
            Mutated chromosome
        """
        mutated = deepcopy(chromosome)
        
        for gene_name in mutated.genes:
            if random.random() < self.mutation_rate:
                min_val, max_val = gene_ranges[gene_name]
                mutation = np.random.normal(0, (max_val - min_val) * 0.1)
                mutated.genes[gene_name] = np.clip(
                    mutated.genes[gene_name] + mutation,
                    min_val,
                    max_val
                )
        
        return mutated
    
    def evolve(self, fitness_func: Callable, gene_ranges: Dict[str, Tuple]) -> List[Chromosome]:
        """
        Run evolutionary algorithm.
        
        Args:
            fitness_func: Function to evaluate fitness
            gene_ranges: Gene value ranges
        
        Returns:
            Best chromosomes across generations
        """
        best_generation = []
        
        for generation in range(self.generations):
            # Evaluate fitness
            self.evaluate_fitness(fitness_func)
            
            # Sort by fitness
            self.population.sort()
            
            # Keep best
            self.best_chromosomes.extend(self.population[:self.elite_size])
            
            if (generation + 1) % 10 == 0:
                best_fitness = self.population[0].fitness
                logger.info(f"Generation {generation + 1}: Best Fitness = {best_fitness:.4f}")
            
            # Create new generation
            new_population = self.population[:self.elite_size]  # Elitism
            
            while len(new_population) < self.population_size:
                parent1 = self.selection()
                parent2 = self.selection()
                
                offspring1, offspring2 = self.crossover(parent1, parent2)
                offspring1 = self.mutate(offspring1, gene_ranges)
                offspring2 = self.mutate(offspring2, gene_ranges)
                
                new_population.extend([offspring1, offspring2])
            
            self.population = new_population[:self.population_size]
        
        self.population.sort()
        return self.population[:self.elite_size]
    
    def get_best_strategy(self) -> Dict[str, float]:
        """
        Get the best evolved strategy.
        
        Returns:
            Best strategy genes
        """
        best = max(self.population, key=lambda x: x.fitness)
        return best.genes
    
    def get_convergence_history(self) -> List[float]:
        """
        Get fitness convergence history.
        
        Returns:
            List of best fitness values per generation
        """
        return [c.fitness for c in self.best_chromosomes]
