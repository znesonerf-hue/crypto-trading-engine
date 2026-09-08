"""Evolutionary Neural Architecture Search (NAS) for Trading"""

import numpy as np
import copy
import random
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

try:
    from src.utils.logger import setup_logger
except ImportError:
    import logging
    def setup_logger(name):
        return logging.getLogger(name)

logger = setup_logger(__name__)


@dataclass
class NASArchitecture:
    """Neural architecture specification"""
    layers: List[Dict]  # Layer configurations
    activation_functions: List[str]
    learning_rate: float
    dropout_rates: List[float]
    batch_size: int
    fitness: float = 0.0


class EvolutionaryNAS:
    """Evolutionary Neural Architecture Search"""
    
    def __init__(self, population_size: int = 20, generations: int = 50):
        """
        Initialize NAS engine.
        
        Args:
            population_size: Population size
            generations: Number of generations
        """
        self.population_size = population_size
        self.generations = generations
        self.population: List[NASArchitecture] = []
        self.best_architectures: List[NASArchitecture] = []
        self.generation_history: List[Dict] = []
    
    def initialize_population(self) -> None:
        """
        Initialize population with random architectures.
        """
        for _ in range(self.population_size):
            arch = self._generate_random_architecture()
            self.population.append(arch)
        
        logger.info(f"Initialized NAS population: {self.population_size}")
    
    def _generate_random_architecture(self) -> NASArchitecture:
        """
        Generate random neural architecture.
        
        Returns:
            Random architecture
        """
        num_layers = random.randint(3, 8)
        layers = []
        
        for i in range(num_layers):
            layer = {
                'type': random.choice(['dense', 'conv1d', 'lstm']),
                'units': random.randint(32, 512),
                'kernel_size': random.randint(2, 5) if i > 0 else None
            }
            layers.append(layer)
        
        arch = NASArchitecture(
            layers=layers,
            activation_functions=[random.choice(['relu', 'tanh', 'elu']) for _ in range(num_layers)],
            learning_rate=random.uniform(0.0001, 0.01),
            dropout_rates=[random.uniform(0.1, 0.5) for _ in range(num_layers)],
            batch_size=random.choice([16, 32, 64, 128])
        )
        
        return arch
    
    def evaluate_architecture(self, arch: NASArchitecture, 
                            evaluate_func: Callable) -> float:
        """
        Evaluate architecture fitness.
        
        Args:
            arch: Architecture to evaluate
            evaluate_func: Function to evaluate fitness
        
        Returns:
            Fitness score
        """
        fitness = evaluate_func(arch)
        arch.fitness = fitness
        return fitness
    
    def mutate_architecture(self, arch: NASArchitecture) -> NASArchitecture:
        """
        Mutate architecture.
        
        Args:
            arch: Architecture to mutate
        
        Returns:
            Mutated architecture
        """
        mutated = copy.deepcopy(arch)
        
        mutation_type = random.choice(['add_layer', 'remove_layer', 'change_params'])
        
        if mutation_type == 'add_layer':
            new_layer = {
                'type': random.choice(['dense', 'conv1d', 'lstm']),
                'units': random.randint(32, 512)
            }
            mutated.layers.insert(random.randint(0, len(mutated.layers)), new_layer)
        
        elif mutation_type == 'remove_layer' and len(mutated.layers) > 2:
            mutated.layers.pop(random.randint(0, len(mutated.layers) - 1))
        
        else:  # change_params
            layer_idx = random.randint(0, len(mutated.layers) - 1)
            mutated.layers[layer_idx]['units'] = random.randint(32, 512)
            mutated.learning_rate = random.uniform(0.0001, 0.01)
        
        return mutated
    
    def crossover_architectures(self, arch1: NASArchitecture, 
                               arch2: NASArchitecture) -> Tuple[NASArchitecture, NASArchitecture]:
        """
        Crossover two architectures.
        
        Args:
            arch1: First architecture
            arch2: Second architecture
        
        Returns:
            Tuple of offspring architectures
        """
        offspring1 = copy.deepcopy(arch1)
        offspring2 = copy.deepcopy(arch2)
        
        # Swap layer configurations
        min_len = min(len(arch1.layers), len(arch2.layers))
        if min_len < 2:
            return offspring1, offspring2
        
        crossover_point = random.randint(1, min_len - 1)
        
        offspring1.layers = arch1.layers[:crossover_point] + arch2.layers[crossover_point:]
        offspring2.layers = arch2.layers[:crossover_point] + arch1.layers[crossover_point:]
        
        return offspring1, offspring2
    
    def search(self, evaluate_func: Callable) -> NASArchitecture:
        """
        Run evolutionary NAS search.
        
        Args:
            evaluate_func: Function to evaluate fitness
        
        Returns:
            Best found architecture
        """
        self.initialize_population()
        
        for generation in range(self.generations):
            # Evaluate all architectures
            for arch in self.population:
                self.evaluate_architecture(arch, evaluate_func)
            
            # Sort by fitness
            self.population.sort(key=lambda x: x.fitness, reverse=True)
            
            # Keep best
            elite_size = max(2, int(self.population_size * 0.2))
            self.best_architectures.extend(self.population[:elite_size])
            
            # Log generation
            gen_info = {
                'generation': generation,
                'best_fitness': self.population[0].fitness,
                'avg_fitness': float(np.mean([a.fitness for a in self.population]))
            }
            self.generation_history.append(gen_info)
            
            if (generation + 1) % 10 == 0:
                logger.info(f"NAS Generation {generation + 1}: Best Fitness = {gen_info['best_fitness']:.4f}")
            
            # Create new generation
            new_population = self.population[:elite_size]
            
            while len(new_population) < self.population_size:
                # Tournament selection
                elite_pool = self.population[:max(2, elite_size * 2)]
                parent1 = random.choice(elite_pool)
                parent2 = random.choice(elite_pool)
                
                # Crossover and mutation
                child1, child2 = self.crossover_architectures(parent1, parent2)
                
                if random.random() < 0.5:
                    child1 = self.mutate_architecture(child1)
                if random.random() < 0.5:
                    child2 = self.mutate_architecture(child2)
                
                new_population.extend([child1, child2])
            
            self.population = new_population[:self.population_size]
        
        best = max(self.best_architectures, key=lambda x: x.fitness)
        logger.info(f"NAS completed. Best architecture fitness: {best.fitness:.4f}")
        
        return best
