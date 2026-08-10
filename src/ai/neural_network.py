"""Neural Network-based Trading System"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass
from datetime import datetime
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class NeuronLayer:
    """Neural network layer"""
    weights: np.ndarray
    bias: np.ndarray
    activation: str = "relu"


class NeuralNetworkSystem:
    """Connectionist AI system using neural networks for trading"""
    
    def __init__(self, input_size: int, hidden_layers: List[int], output_size: int = 3):
        """
        Initialize neural network.
        
        Args:
            input_size: Number of input features
            hidden_layers: List of hidden layer sizes
            output_size: Number of output neurons (Buy, Neutral, Sell)
        """
        self.input_size = input_size
        self.hidden_layers = hidden_layers
        self.output_size = output_size
        self.layers: List[NeuronLayer] = []
        self.learning_rate = 0.001
        self.training_history = []
        
        self._initialize_network()
    
    def _initialize_network(self) -> None:
        """
        Initialize network weights and biases.
        """
        layer_sizes = [self.input_size] + self.hidden_layers + [self.output_size]
        
        for i in range(len(layer_sizes) - 1):
            weights = np.random.randn(layer_sizes[i], layer_sizes[i + 1]) * 0.01
            bias = np.zeros((1, layer_sizes[i + 1]))
            activation = "relu" if i < len(layer_sizes) - 2 else "softmax"
            
            self.layers.append(NeuronLayer(weights, bias, activation))
        
        logger.info(f"Initialized neural network: {layer_sizes}")
    
    def _relu(self, x: np.ndarray) -> np.ndarray:
        """ReLU activation"""
        return np.maximum(0, x)
    
    def _relu_derivative(self, x: np.ndarray) -> np.ndarray:
        """ReLU derivative"""
        return (x > 0).astype(float)
    
    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Softmax activation"""
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)
    
    def _forward_pass(self, X: np.ndarray) -> np.ndarray:
        """
        Forward pass through network.
        
        Args:
            X: Input data
        
        Returns:
            Output predictions
        """
        activation = X
        
        for i, layer in enumerate(self.layers):
            z = np.dot(activation, layer.weights) + layer.bias
            
            if layer.activation == "relu":
                activation = self._relu(z)
            elif layer.activation == "softmax":
                activation = self._softmax(z)
        
        return activation
    
    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 100, 
              batch_size: int = 32) -> None:
        """
        Train the neural network.
        
        Args:
            X: Training input data
            y: Training target data
            epochs: Number of training epochs
            batch_size: Batch size for training
        """
        for epoch in range(epochs):
            # Mini-batch training
            indices = np.random.permutation(len(X))
            
            for i in range(0, len(X), batch_size):
                batch_indices = indices[i:i + batch_size]
                X_batch = X[batch_indices]
                y_batch = y[batch_indices]
                
                # Forward pass
                output = self._forward_pass(X_batch)
                
                # Calculate loss
                loss = -np.mean(y_batch * np.log(output + 1e-8))
                
                # Store loss
                self.training_history.append({'epoch': epoch, 'loss': loss})
            
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch + 1}/{epochs}, Loss: {loss:.4f}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Input data
        
        Returns:
            Prediction probabilities
        """
        output = self._forward_pass(X)
        return output
    
    def predict_signal(self, indicators: Dict[str, float]) -> str:
        """
        Predict trading signal from indicators.
        
        Args:
            indicators: Technical indicators
        
        Returns:
            Trading signal ('BUY', 'SELL', 'NEUTRAL')
        """
        # Prepare input features
        features = np.array([
            indicators.get('rsi', 50) / 100,
            indicators.get('macd', 0),
            indicators.get('bb_position', 0.5),
            indicators.get('adx', 25) / 100,
            indicators.get('atr', 0),
            indicators.get('volume_sma_ratio', 1.0),
            indicators.get('price_position', 0.5),
            indicators.get('momentum', 0)
        ]).reshape(1, -1)
        
        prediction = self.predict(features)[0]
        signals = ['SELL', 'NEUTRAL', 'BUY']
        signal_idx = np.argmax(prediction)
        
        return signals[signal_idx], prediction[signal_idx]
    
    def get_network_info(self) -> Dict:
        """
        Get network architecture information.
        
        Returns:
            Network information
        """
        return {
            'input_size': self.input_size,
            'hidden_layers': self.hidden_layers,
            'output_size': self.output_size,
            'total_layers': len(self.layers),
            'learning_rate': self.learning_rate,
            'total_parameters': sum(layer.weights.size + layer.bias.size for layer in self.layers)
        }
