"""Cryptographic Data Integrity & Verifiable Oracle Feed"""

import hashlib
import hmac
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class VerifiedData:
    """Cryptographically verified data"""
    data: Dict
    hash: str
    signature: str
    timestamp: datetime
    oracle_address: str
    proof: str


class CryptoDataIntegrity:
    """Cryptographic data integrity verification"""
    
    def __init__(self):
        """
        Initialize crypto integrity manager.
        """
        self.verified_data: Dict[str, VerifiedData] = {}
        self.oracle_keys: Dict[str, rsa.RSAPublicKey] = {}
    
    def hash_data(self, data: Dict) -> str:
        """
        Hash data with SHA-256.
        
        Args:
            data: Data to hash
        
        Returns:
            Hash hexdigest
        """
        import json
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def generate_hmac(self, data: Dict, secret: str) -> str:
        """
        Generate HMAC signature.
        
        Args:
            data: Data to sign
            secret: Secret key
        
        Returns:
            HMAC signature
        """
        import json
        data_str = json.dumps(data, sort_keys=True)
        return hmac.new(secret.encode(), data_str.encode(), hashlib.sha256).hexdigest()
    
    def verify_hmac(self, data: Dict, signature: str, secret: str) -> bool:
        """
        Verify HMAC signature.
        
        Args:
            data: Data to verify
            signature: Signature to verify
            secret: Secret key
        
        Returns:
            True if signature is valid
        """
        expected_signature = self.generate_hmac(data, secret)
        return hmac.compare_digest(signature, expected_signature)
    
    def register_oracle(self, oracle_address: str, public_key: rsa.RSAPublicKey) -> None:
        """
        Register oracle public key.
        
        Args:
            oracle_address: Oracle address
            public_key: Oracle public key
        """
        self.oracle_keys[oracle_address] = public_key
        logger.info(f"Registered oracle: {oracle_address}")
    
    def verify_oracle_data(self, data: Dict, signature: bytes, 
                          oracle_address: str) -> bool:
        """
        Verify data signed by oracle.
        
        Args:
            data: Data to verify
            signature: Digital signature
            oracle_address: Oracle address
        
        Returns:
            True if signature is valid
        """
        if oracle_address not in self.oracle_keys:
            logger.error(f"Unknown oracle: {oracle_address}")
            return False
        
        try:
            public_key = self.oracle_keys[oracle_address]
            data_hash = self.hash_data(data).encode()
            
            public_key.verify(
                signature,
                data_hash,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def create_merkle_tree(self, data_list: List[Dict]) -> str:
        """
        Create Merkle tree for data list.
        
        Args:
            data_list: List of data
        
        Returns:
            Merkle root hash
        """
        if not data_list:
            return ''
        
        # Hash each item
        hashes_list = [self.hash_data(item) for item in data_list]
        
        # Build tree
        while len(hashes_list) > 1:
            if len(hashes_list) % 2 != 0:
                hashes_list.append(hashes_list[-1])  # Duplicate last if odd
            
            new_level = []
            for i in range(0, len(hashes_list), 2):
                combined = hashes_list[i] + hashes_list[i + 1]
                new_hash = hashlib.sha256(combined.encode()).hexdigest()
                new_level.append(new_hash)
            
            hashes_list = new_level
        
        return hashes_list[0]
    
    def verify_merkle_proof(self, data: Dict, proof: List[Tuple[str, str]], 
                           root: str) -> bool:
        """
        Verify Merkle proof.
        
        Args:
            data: Data to verify
            proof: Merkle proof path
            root: Merkle root
        
        Returns:
            True if proof is valid
        """
        current_hash = self.hash_data(data)
        
        for sibling_hash, position in proof:
            if position == 'left':
                combined = sibling_hash + current_hash
            else:
                combined = current_hash + sibling_hash
            
            current_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        return current_hash == root
