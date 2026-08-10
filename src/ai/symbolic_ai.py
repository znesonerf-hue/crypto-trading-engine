"""Symbolic AI / Rule-based Trading System"""

import pandas as pd
from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class Signal(Enum):
    """Trading signals"""
    STRONG_BUY = 2
    BUY = 1
    NEUTRAL = 0
    SELL = -1
    STRONG_SELL = -2


@dataclass
class Rule:
    """Trading rule definition"""
    name: str
    condition: callable
    weight: float = 1.0
    signal: Signal = Signal.NEUTRAL


class SymbolicAISystem:
    """Rule-based trading system using symbolic AI"""
    
    def __init__(self):
        """
        Initialize symbolic AI system.
        """
        self.rules: List[Rule] = []
        self.rule_history: List[Dict] = []
    
    def add_rule(self, rule: Rule) -> None:
        """
        Add a trading rule.
        
        Args:
            rule: Rule to add
        """
        self.rules.append(rule)
        logger.info(f"Added rule: {rule.name}")
    
    def add_technical_rules(self, indicators: Dict) -> None:
        """
        Add common technical analysis rules.
        
        Args:
            indicators: Dictionary of technical indicators
        """
        # RSI Rules
        self.add_rule(Rule(
            name="RSI_Oversold",
            condition=lambda rsi: rsi < 30,
            weight=1.0,
            signal=Signal.BUY
        ))
        
        self.add_rule(Rule(
            name="RSI_Overbought",
            condition=lambda rsi: rsi > 70,
            weight=1.0,
            signal=Signal.SELL
        ))
        
        # MACD Rules
        self.add_rule(Rule(
            name="MACD_Bullish_Crossover",
            condition=lambda macd, signal: (macd > signal) and (macd.shift(1) <= signal.shift(1)),
            weight=1.5,
            signal=Signal.BUY
        ))
        
        self.add_rule(Rule(
            name="MACD_Bearish_Crossover",
            condition=lambda macd, signal: (macd < signal) and (macd.shift(1) >= signal.shift(1)),
            weight=1.5,
            signal=Signal.SELL
        ))
    
    def evaluate_rules(self, market_data: pd.DataFrame, 
                      indicators: Dict[str, pd.Series]) -> Tuple[Signal, Dict]:
        """
        Evaluate all rules on current market data.
        
        Args:
            market_data: Market data DataFrame
            indicators: Technical indicators
        
        Returns:
            Tuple of (Signal, Rule evaluation details)
        """
        buy_weight = 0
        sell_weight = 0
        rule_results = {}
        
        # Get latest values
        rsi = indicators.get('rsi', pd.Series()).iloc[-1] if 'rsi' in indicators else 50
        macd = indicators.get('macd', pd.Series()).iloc[-1] if 'macd' in indicators else 0
        macd_signal = indicators.get('macd_signal', pd.Series()).iloc[-1] if 'macd_signal' in indicators else 0
        bb_upper = indicators.get('bb_upper', pd.Series()).iloc[-1] if 'bb_upper' in indicators else 0
        bb_lower = indicators.get('bb_lower', pd.Series()).iloc[-1] if 'bb_lower' in indicators else 0
        close = market_data['close'].iloc[-1] if 'close' in market_data else 0
        
        # Evaluate each rule
        for rule in self.rules:
            try:
                if 'RSI' in rule.name:
                    triggered = rule.condition(rsi)
                elif 'MACD' in rule.name:
                    triggered = rule.condition(
                        indicators.get('macd', pd.Series()),
                        indicators.get('macd_signal', pd.Series())
                    )
                elif 'BB' in rule.name:
                    triggered = rule.condition(close, bb_upper, bb_lower)
                else:
                    triggered = False
                
                rule_results[rule.name] = triggered
                
                if triggered:
                    if rule.signal == Signal.BUY or rule.signal == Signal.STRONG_BUY:
                        buy_weight += rule.weight
                    elif rule.signal == Signal.SELL or rule.signal == Signal.STRONG_SELL:
                        sell_weight += rule.weight
                
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")
                rule_results[rule.name] = False
        
        # Determine final signal
        if buy_weight > sell_weight * 1.5:
            final_signal = Signal.STRONG_BUY if buy_weight > 3 else Signal.BUY
        elif sell_weight > buy_weight * 1.5:
            final_signal = Signal.STRONG_SELL if sell_weight > 3 else Signal.SELL
        else:
            final_signal = Signal.NEUTRAL
        
        return final_signal, {
            'signal': final_signal,
            'buy_weight': buy_weight,
            'sell_weight': sell_weight,
            'rule_results': rule_results,
            'timestamp': datetime.now()
        }
    
    def add_decision_tree_rule(self, name: str, tree_path: List[Tuple]) -> None:
        """
        Add decision tree rule.
        
        Args:
            name: Rule name
            tree_path: Path through decision tree
        """
        def tree_condition(*args):
            # Evaluate tree path
            result = True
            for condition in tree_path:
                result = result and condition
            return result
        
        self.add_rule(Rule(
            name=name,
            condition=tree_condition,
            weight=1.0
        ))
    
    def get_rule_performance(self) -> Dict:
        """
        Get performance statistics of all rules.
        
        Returns:
            Performance statistics
        """
        stats = {}
        for rule in self.rules:
            stats[rule.name] = {
                'weight': rule.weight,
                'signal': rule.signal.name,
                'triggered_count': sum(1 for h in self.rule_history if h['rule'] == rule.name)
            }
        return stats
