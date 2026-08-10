"""Hybrid AI System"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from src.ai.symbolic_ai import SymbolicAISystem, Signal
from src.ai.neural_network import NeuralNetworkSystem
from src.ai.evolutionary import EvolutionarySystem
from src.ai.probabilistic import ProbabilisticSystem
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class HybridPrediction:
    """Hybrid AI prediction"""
    signal: str
    confidence: float
    symbolic_signal: str
    neural_signal: str
    probabilistic_signal: str
    evolutionary_strategy: Dict
    timestamp: datetime
    reasoning: Dict


class HybridAISystem:
    """Hybrid AI system combining multiple AI approaches"""
    
    def __init__(self):
        """
        Initialize hybrid AI system with all sub-systems.
        """
        self.symbolic = SymbolicAISystem()
        self.neural = NeuralNetworkSystem(
            input_size=8,
            hidden_layers=[16, 8],
            output_size=3
        )
        self.evolutionary = EvolutionarySystem(population_size=50, generations=100)
        self.probabilistic = ProbabilisticSystem()
        
        self.weights = {
            'symbolic': 0.2,
            'neural': 0.3,
            'probabilistic': 0.35,
            'evolutionary': 0.15
        }
        
        self.prediction_history: List[HybridPrediction] = []
    
    def predict(self, market_data: pd.DataFrame, 
               indicators: Dict[str, pd.Series]) -> HybridPrediction:
        """
        Make prediction using all AI systems.
        
        Args:
            market_data: Market data
            indicators: Technical indicators
        
        Returns:
            Hybrid prediction
        """
        reasoning = {}
        
        # 1. Symbolic AI prediction
        symbolic_signal, symbolic_details = self.symbolic.evaluate_rules(market_data, indicators)
        reasoning['symbolic'] = symbolic_details
        
        # 2. Neural Network prediction
        latest_indicators = {
            'rsi': indicators.get('rsi', pd.Series()).iloc[-1] if len(indicators.get('rsi', [])) > 0 else 50,
            'macd': indicators.get('macd', pd.Series()).iloc[-1] if len(indicators.get('macd', [])) > 0 else 0,
            'bb_position': 0.5,
            'adx': indicators.get('adx', pd.Series()).iloc[-1] if len(indicators.get('adx', [])) > 0 else 25,
            'atr': indicators.get('atr', pd.Series()).iloc[-1] if len(indicators.get('atr', [])) > 0 else 0,
            'volume_sma_ratio': 1.0,
            'price_position': 0.5,
            'momentum': 0
        }
        neural_signal, neural_confidence = self.neural.predict_signal(latest_indicators)
        reasoning['neural'] = {'signal': neural_signal, 'confidence': neural_confidence}
        
        # 3. Probabilistic prediction
        prob_prediction = self.probabilistic.predict_with_confidence(latest_indicators)
        reasoning['probabilistic'] = prob_prediction
        
        # 4. Evolutionary strategy (best evolved strategy)
        evolutionary_strategy = self.evolutionary.get_best_strategy()
        reasoning['evolutionary'] = evolutionary_strategy
        
        # Combine predictions
        signals_dict = {
            'BUY': self.weights['symbolic'] * (1 if symbolic_signal.value > 0 else 0) +
                   self.weights['neural'] * (1 if neural_signal == 'BUY' else 0) +
                   self.weights['probabilistic'] * prob_prediction['bullish_probability'],
            'SELL': self.weights['symbolic'] * (1 if symbolic_signal.value < 0 else 0) +
                    self.weights['neural'] * (1 if neural_signal == 'SELL' else 0) +
                    self.weights['probabilistic'] * prob_prediction['bearish_probability']
        }
        
        # Determine final signal
        if signals_dict['BUY'] > signals_dict['SELL'] + 0.1:
            final_signal = 'BUY'
            confidence = signals_dict['BUY']
        elif signals_dict['SELL'] > signals_dict['BUY'] + 0.1:
            final_signal = 'SELL'
            confidence = signals_dict['SELL']
        else:
            final_signal = 'NEUTRAL'
            confidence = 0.5 - abs(signals_dict['BUY'] - signals_dict['SELL'])
        
        prediction = HybridPrediction(
            signal=final_signal,
            confidence=min(confidence, 1.0),
            symbolic_signal=symbolic_signal.name,
            neural_signal=neural_signal,
            probabilistic_signal=prob_prediction['signal'],
            evolutionary_strategy=evolutionary_strategy,
            timestamp=datetime.now(),
            reasoning=reasoning
        )
        
        self.prediction_history.append(prediction)
        return prediction
    
    def adjust_weights(self, performance_metrics: Dict[str, float]) -> None:
        """
        Adjust system weights based on performance.
        
        Args:
            performance_metrics: Performance metrics of each system
        """
        total_performance = sum(performance_metrics.values())
        
        if total_performance > 0:
            self.weights = {
                system: performance / total_performance 
                for system, performance in performance_metrics.items()
            }
            logger.info(f"Adjusted weights: {self.weights}")
    
    def get_hybrid_performance(self) -> Dict:
        """
        Get performance metrics of hybrid system.
        
        Returns:
            Performance metrics
        """
        if not self.prediction_history:
            return {}
        
        correct_predictions = 0
        avg_confidence = np.mean([p.confidence for p in self.prediction_history])
        
        return {
            'total_predictions': len(self.prediction_history),
            'average_confidence': avg_confidence,
            'weights': self.weights,
            'last_prediction': self.prediction_history[-1].__dict__ if self.prediction_history else None
        }
