"""Synthetic Market Psychology & Collective Persona Simulation"""

import random
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

try:
    from src.utils.logger import setup_logger
except ImportError:
    import logging
    def setup_logger(name):
        return logging.getLogger(name)

logger = setup_logger(__name__)


class TraderPersona(Enum):
    """Market trader personas"""
    BULL = "aggressive_bull"
    BEAR = "risk_aware_bear"
    ARBITRAGEUR = "profit_seeking_arbitrageur"
    WHALE = "patient_whale"
    SCALPER = "quick_scalper"
    VALUE_INVESTOR = "fundamental_value_investor"
    FEARFUL_RETAIL = "emotional_retail"
    ALGOS = "emotionless_algorithm"


@dataclass
class Trader:
    """Individual trader persona"""
    persona: TraderPersona
    confidence: float = 0.5
    risk_tolerance: float = 0.5
    time_horizon: int = 60  # minutes
    position_size: float = 0.1
    emotions: Dict[str, float] = field(default_factory=lambda: {
        'fear': 0.3, 'greed': 0.3, 'confidence': 0.5, 'doubt': 0.2
    })


class MarketPsychologySimulator:
    """Simulate collective market psychology"""
    
    def __init__(self, num_traders: int = 100):
        """
        Initialize market psychology simulator.
        
        Args:
            num_traders: Number of simulated traders
        """
        self.traders: List[Trader] = []
        self.market_sentiment_history: List[float] = []
        self.collective_emotions: Dict[str, float] = {
            'fear': 0.0, 'greed': 0.0, 'confidence': 0.0, 'doubt': 0.0
        }
        
        self._initialize_traders(num_traders)
    
    def _initialize_traders(self, num_traders: int) -> None:
        """
        Initialize trader population.
        
        Args:
            num_traders: Number of traders
        """
        personas = list(TraderPersona)
        
        for i in range(num_traders):
            persona = random.choice(personas)
            
            # Adjust parameters based on persona
            if persona == TraderPersona.BULL:
                confidence = random.uniform(0.7, 0.95)
                risk_tolerance = random.uniform(0.7, 0.95)
            elif persona == TraderPersona.BEAR:
                confidence = random.uniform(0.5, 0.8)
                risk_tolerance = random.uniform(0.2, 0.5)
            else:
                confidence = random.uniform(0.4, 0.7)
                risk_tolerance = random.uniform(0.3, 0.7)
            
            trader = Trader(
                persona=persona,
                confidence=confidence,
                risk_tolerance=risk_tolerance,
                time_horizon=random.randint(5, 240),
                position_size=random.uniform(0.01, 0.5)
            )
            
            self.traders.append(trader)
    
    def simulate_market_event(self, event_type: str, 
                             event_strength: float) -> Dict:
        """
        Simulate market event and collective response.
        
        Args:
            event_type: Type of market event
            event_strength: Strength of event (0-1)
        
        Returns:
            Market response dictionary
        """
        # Update emotions based on event
        if event_type == 'positive_news':
            emotion_shift = {'fear': -0.2, 'greed': 0.3, 'confidence': 0.2, 'doubt': -0.1}
        elif event_type == 'negative_news':
            emotion_shift = {'fear': 0.3, 'greed': -0.2, 'confidence': -0.2, 'doubt': 0.2}
        elif event_type == 'price_surge':
            emotion_shift = {'fear': -0.1, 'greed': 0.4, 'confidence': 0.3, 'doubt': -0.2}
        elif event_type == 'price_crash':
            emotion_shift = {'fear': 0.4, 'greed': -0.3, 'confidence': -0.3, 'doubt': 0.3}
        else:
            emotion_shift = {k: 0 for k in self.collective_emotions}
        
        # Apply event strength multiplier
        emotion_shift = {k: v * event_strength for k, v in emotion_shift.items()}
        
        # Update trader emotions
        for trader in self.traders:
            for emotion, shift in emotion_shift.items():
                current = trader.emotions.get(emotion, 0.0)
                trader.emotions[emotion] = max(0.0, min(1.0, current + shift))
        
        # Calculate collective sentiment
        self._update_collective_sentiment()
        
        # Predict trading actions
        actions = self._predict_collective_actions(event_type, event_strength)
        
        return {
            'event_type': event_type,
            'event_strength': event_strength,
            'collective_emotions': self.collective_emotions.copy(),
            'market_sentiment': self.market_sentiment_history[-1] if self.market_sentiment_history else 0.5,
            'predicted_actions': actions
        }
    
    def _update_collective_sentiment(self) -> None:
        """
        Update collective market sentiment.
        """
        if not self.traders:
            return
        
        avg_emotions = {}
        
        for emotion in self.collective_emotions:
            total = sum(t.emotions.get(emotion, 0.0) for t in self.traders)
            avg_emotions[emotion] = total / len(self.traders)
        
        self.collective_emotions = avg_emotions
        
        # Sentiment = (greed - fear) / 2 + confidence / 2
        sentiment = (avg_emotions['greed'] - avg_emotions['fear']) / 2 + avg_emotions['confidence'] / 2
        sentiment = max(-1.0, min(1.0, sentiment))
        
        self.market_sentiment_history.append(sentiment)
    
    def _predict_collective_actions(self, event_type: str, 
                                   event_strength: float) -> Dict[str, float]:
        """
        Predict collective trading actions.
        
        Args:
            event_type: Event type
            event_strength: Event strength
        
        Returns:
            Action probabilities
        """
        buy_pressure = 0.0
        sell_pressure = 0.0
        
        for trader in self.traders:
            # Base decision on emotions and persona
            if trader.persona == TraderPersona.BULL:
                buy_pressure += trader.emotions.get('greed', 0) * 0.8 + trader.emotions.get('confidence', 0) * 0.5
            elif trader.persona == TraderPersona.BEAR:
                sell_pressure += trader.emotions.get('fear', 0) * 0.8 + trader.emotions.get('doubt', 0) * 0.5
            
            # Fear and greed affect all traders
            buy_pressure += trader.emotions.get('greed', 0) * 0.3
            sell_pressure += trader.emotions.get('fear', 0) * 0.3
        
        total_pressure = buy_pressure + sell_pressure
        if total_pressure == 0:
            total_pressure = 1.0
        
        return {
            'buy_probability': buy_pressure / total_pressure,
            'sell_probability': sell_pressure / total_pressure,
            'hold_probability': 1.0 - (buy_pressure + sell_pressure) / (2 * total_pressure),
            'total_buy_volume': buy_pressure,
            'total_sell_volume': sell_pressure
        }
    
    def get_market_psychology_report(self) -> Dict:
        """
        Get market psychology analysis report.
        
        Returns:
            Psychology report
        """
        if not self.traders:
            return {'error': 'No traders initialized'}
        
        return {
            'timestamp': datetime.now().isoformat(),
            'num_traders': len(self.traders),
            'collective_emotions': self.collective_emotions,
            'sentiment_trend': self._calculate_sentiment_trend(),
            'persona_breakdown': self._get_persona_breakdown(),
            'dominant_persona': self._get_dominant_persona()
        }
    
    def _get_dominant_persona(self) -> str:
        """
        Get dominant trader persona.
        
        Returns:
            Dominant persona name
        """
        if not self.traders:
            return 'unknown'
        
        persona_counts = {}
        for trader in self.traders:
            p_name = trader.persona.value
            persona_counts[p_name] = persona_counts.get(p_name, 0) + 1
        
        return max(persona_counts, key=persona_counts.get)
    
    def _calculate_sentiment_trend(self) -> str:
        """
        Calculate sentiment trend.
        
        Returns:
            Trend description
        """
        if len(self.market_sentiment_history) < 2:
            return 'neutral'
        
        recent = self.market_sentiment_history[-5:]
        trend = recent[-1] - recent[0]
        
        if trend > 0.1:
            return 'strongly_bullish'
        elif trend > 0.02:
            return 'bullish'
        elif trend < -0.1:
            return 'strongly_bearish'
        elif trend < -0.02:
            return 'bearish'
        else:
            return 'neutral'
    
    def _get_persona_breakdown(self) -> Dict[str, int]:
        """
        Get breakdown of trader personas.
        
        Returns:
            Persona counts
        """
        breakdown = {}
        for trader in self.traders:
            persona_name = trader.persona.value
            breakdown[persona_name] = breakdown.get(persona_name, 0) + 1
        
        return breakdown
