"""Probabilistic & Bayesian Trading System"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from scipy import stats
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class BayesianBeliefs:
    """Bayesian beliefs about market state"""
    bullish_probability: float = 0.5
    bearish_probability: float = 0.5
    neutral_probability: float = 0.0
    evidence: Dict[str, float] = None


class ProbabilisticSystem:
    """Probabilistic and Bayesian AI system for trading"""
    
    def __init__(self):
        """
        Initialize probabilistic system.
        """
        self.prior_beliefs = BayesianBeliefs()
        self.observation_history: List[Dict] = []
        self.confidence_threshold = 0.65
    
    def calculate_technical_probabilities(self, indicators: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate probability of bullish/bearish based on technical indicators.
        
        Args:
            indicators: Technical indicators
        
        Returns:
            Dictionary of probabilities
        """
        probabilities = {}
        
        # RSI probability
        rsi = indicators.get('rsi', 50)
        rsi_prob_bull = (rsi - 30) / 40 if rsi > 30 else 0  # Oversold recovery
        rsi_prob_bear = (70 - rsi) / 40 if rsi < 70 else 0  # Overbought reversal
        probabilities['rsi_bull'] = np.clip(rsi_prob_bull, 0, 1)
        probabilities['rsi_bear'] = np.clip(rsi_prob_bear, 0, 1)
        
        # MACD probability
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        macd_histogram = macd - macd_signal
        
        if macd_histogram > 0:
            probabilities['macd_bull'] = min(abs(macd_histogram) / 0.5, 1.0)
            probabilities['macd_bear'] = 0
        else:
            probabilities['macd_bear'] = min(abs(macd_histogram) / 0.5, 1.0)
            probabilities['macd_bull'] = 0
        
        # Bollinger Bands probability
        bb_position = indicators.get('bb_position', 0.5)  # 0=lower, 1=upper
        if bb_position < 0.3:
            probabilities['bb_bull'] = 0.7  # Near lower band = likely bounce
            probabilities['bb_bear'] = 0.1
        elif bb_position > 0.7:
            probabilities['bb_bear'] = 0.7  # Near upper band = likely pullback
            probabilities['bb_bull'] = 0.1
        else:
            probabilities['bb_bull'] = 0.3
            probabilities['bb_bear'] = 0.3
        
        # ADX probability (trend strength)
        adx = indicators.get('adx', 25)
        trend_strength = min(adx / 50, 1.0)  # Normalize to 0-1
        probabilities['trend_strength'] = trend_strength
        
        return probabilities
    
    def bayesian_update(self, prior: float, likelihood_true: float, 
                       likelihood_false: float) -> float:
        """
        Update probability using Bayes' theorem.
        
        Args:
            prior: Prior probability
            likelihood_true: P(evidence | hypothesis true)
            likelihood_false: P(evidence | hypothesis false)
        
        Returns:
            Posterior probability
        """
        posterior = (likelihood_true * prior) / (
            likelihood_true * prior + likelihood_false * (1 - prior)
        )
        return posterior
    
    def calculate_joint_probability(self, probabilities: Dict[str, float], 
                                    weights: Dict[str, float]) -> Tuple[float, float]:
        """
        Calculate joint probability of bullish/bearish.
        
        Args:
            probabilities: Individual probabilities
            weights: Weight for each probability
        
        Returns:
            Tuple of (bullish_prob, bearish_prob)
        """
        bullish_prob = 0
        bearish_prob = 0
        total_weight = 0
        
        for key, prob in probabilities.items():
            if key.endswith('_bull'):
                weight = weights.get(key, 1.0)
                bullish_prob += prob * weight
                total_weight += weight
            elif key.endswith('_bear'):
                weight = weights.get(key, 1.0)
                bearish_prob += prob * weight
                total_weight += weight
        
        if total_weight > 0:
            bullish_prob /= total_weight
            bearish_prob /= total_weight
        
        # Normalize
        total = bullish_prob + bearish_prob
        if total > 0:
            bullish_prob /= total
            bearish_prob /= total
        
        return bullish_prob, bearish_prob
    
    def estimate_market_regime(self, price_history: pd.Series, window: int = 20) -> Dict:
        """
        Estimate current market regime using probability analysis.
        
        Args:
            price_history: Historical prices
            window: Window size for calculation
        
        Returns:
            Market regime analysis
        """
        if len(price_history) < window:
            return {'regime': 'unknown', 'probability': 0}
        
        recent_prices = price_history.iloc[-window:]
        returns = recent_prices.pct_change().dropna()
        
        # Calculate statistics
        mean_return = returns.mean()
        volatility = returns.std()
        
        # Determine regime probabilities
        uptrend_prob = stats.norm.cdf(mean_return, 0, volatility)
        downtrend_prob = 1 - uptrend_prob
        high_vol_prob = 1 - stats.norm.cdf(volatility, returns.std().mean(), returns.std().std())
        
        return {
            'uptrend_probability': uptrend_prob,
            'downtrend_probability': downtrend_prob,
            'high_volatility_probability': high_vol_prob,
            'mean_return': mean_return,
            'volatility': volatility
        }
    
    def monte_carlo_simulation(self, current_price: float, expected_return: float,
                              volatility: float, periods: int = 100, 
                              simulations: int = 1000) -> Dict:
        """
        Monte Carlo simulation for price prediction.
        
        Args:
            current_price: Current asset price
            expected_return: Expected return
            volatility: Price volatility
            periods: Number of periods to simulate
            simulations: Number of simulations
        
        Returns:
            Simulation results
        """
        results = np.zeros((simulations, periods))
        
        for sim in range(simulations):
            price = current_price
            for period in range(periods):
                random_return = np.random.normal(expected_return, volatility)
                price = price * (1 + random_return)
                results[sim, period] = price
        
        # Calculate statistics
        final_prices = results[:, -1]
        
        return {
            'mean_final_price': np.mean(final_prices),
            'median_final_price': np.median(final_prices),
            'std_final_price': np.std(final_prices),
            'percentile_5': np.percentile(final_prices, 5),
            'percentile_95': np.percentile(final_prices, 95),
            'probability_profit': np.mean(final_prices > current_price),
            'simulation_results': results
        }
    
    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR).
        
        Args:
            returns: Historical returns
            confidence_level: Confidence level (0.95 = 95%)
        
        Returns:
            VaR value
        """
        return np.percentile(returns, (1 - confidence_level) * 100)
    
    def calculate_cvar(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (CVaR).
        
        Args:
            returns: Historical returns
            confidence_level: Confidence level
        
        Returns:
            CVaR value
        """
        var = self.calculate_var(returns, confidence_level)
        return returns[returns <= var].mean()
    
    def predict_with_confidence(self, indicators: Dict[str, float],
                               weights: Optional[Dict[str, float]] = None) -> Dict:
        """
        Make prediction with confidence score.
        
        Args:
            indicators: Technical indicators
            weights: Custom weights for indicators
        
        Returns:
            Prediction with confidence
        """
        if weights is None:
            weights = {
                'rsi_bull': 1.0, 'rsi_bear': 1.0,
                'macd_bull': 1.5, 'macd_bear': 1.5,
                'bb_bull': 0.8, 'bb_bear': 0.8
            }
        
        probs = self.calculate_technical_probabilities(indicators)
        bullish_prob, bearish_prob = self.calculate_joint_probability(probs, weights)
        
        # Determine signal and confidence
        if bullish_prob > self.confidence_threshold:
            signal = 'BUY'
            confidence = bullish_prob
        elif bearish_prob > self.confidence_threshold:
            signal = 'SELL'
            confidence = bearish_prob
        else:
            signal = 'NEUTRAL'
            confidence = 1 - (bullish_prob + bearish_prob)
        
        return {
            'signal': signal,
            'confidence': confidence,
            'bullish_probability': bullish_prob,
            'bearish_probability': bearish_prob,
            'probabilities': probs
        }
