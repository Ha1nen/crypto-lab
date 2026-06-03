from .constants import *
from .utils import bit_permutation, split_nibbles, combine_nibbles


class Present80:
    def __init__(self, key, rounds=31):
        """
        PRESENT-80 шифр с возможностью выбора количества раундов
        
        Args:
            key: 80-битный ключ (целое число или 10 байт)
            rounds: количество раундов (1..31, по умолчанию 31)
        """
        if isinstance(key, bytes):
            self.master_key = int.from_bytes(key, byteorder='little')
        else:
            self.master_key = key & ((1 << KEY_SIZE) - 1)
        
        self.rounds = min(rounds, MAX_ROUNDS)
        if self.rounds < 1:
            self.rounds = 1
        
        self.round_keys = self._key_schedule()
    
    def _apply_sbox(self, state):
        nibbles = split_nibbles(state)
        substituted = [SBOX[n] for n in nibbles]
        return combine_nibbles(substituted)
    
    def _apply_inv_sbox(self, state):
        nibbles = split_nibbles(state)
        substituted = [INV_SBOX[n] for n in nibbles]
        return combine_nibbles(substituted)
    
    def _apply_player(self, state):
        return bit_permutation(state, P_LAYER, BLOCK_SIZE)
    
    def _apply_inv_player(self, state):
        inv_player = [0] * BLOCK_SIZE
        for new_pos, old_pos in enumerate(P_LAYER):
            inv_player[old_pos] = new_pos
        return bit_permutation(state, inv_player, BLOCK_SIZE)
    
    def _key_schedule(self):
        """
        Генерирует раундовые ключи.
        Нужно (rounds + 1) ключей: rounds для каждого раунда + 1 для начального XOR
        """
        round_keys = []
        current_key = self.master_key
        
        # Нужно rounds+1 ключей (индексы 0..rounds)
        for round_num in range(1, self.rounds + 2):
            round_key = (current_key >> (KEY_SIZE - BLOCK_SIZE)) & ((1 << BLOCK_SIZE) - 1)
            round_keys.append(round_key)
            
            if round_num < self.rounds + 1:
                # Сдвиг влево на 61 бит
                current_key = ((current_key << 61) | (current_key >> (KEY_SIZE - 61))) & ((1 << KEY_SIZE) - 1)
                
                # S-блок к старшим 4 битам
                high_nibble = (current_key >> (KEY_SIZE - 4)) & 0xF
                new_high_nibble = SBOX[high_nibble]
                current_key = (current_key & ((1 << (KEY_SIZE - 4)) - 1)) | (new_high_nibble << (KEY_SIZE - 4))
                
                # XOR с раундовой константой
                round_const = ROUND_CONSTANTS[round_num - 1] if round_num - 1 < len(ROUND_CONSTANTS) else 0
                current_key ^= (round_const << 15)
        
        return round_keys
    
    def encrypt_block(self, plaintext):
        if isinstance(plaintext, bytes):
            state = int.from_bytes(plaintext, byteorder='little')
        else:
            state = plaintext & ((1 << BLOCK_SIZE) - 1)
        
        # начальный XOR
        state ^= self.round_keys[0]
        
        # раунды 1..rounds-1 (с перестановкой)
        for round_num in range(1, self.rounds):
            state = self._apply_sbox(state)
            state = self._apply_player(state)
            state ^= self.round_keys[round_num]
        
        # последний раунд (без перестановки)
        if self.rounds > 0:
            state = self._apply_sbox(state)
            state ^= self.round_keys[self.rounds]
        
        return state
    
    def decrypt_block(self, ciphertext):
        if isinstance(ciphertext, bytes):
            state = int.from_bytes(ciphertext, byteorder='little')
        else:
            state = ciphertext & ((1 << BLOCK_SIZE) - 1)
        
        # последний раунд обратно
        state ^= self.round_keys[self.rounds]
        state = self._apply_inv_sbox(state)
        
        # остальные раунды обратно
        for round_num in range(self.rounds - 1, 0, -1):
            state ^= self.round_keys[round_num]
            state = self._apply_inv_player(state)
            state = self._apply_inv_sbox(state)
        
        # начальный XOR обратно
        state ^= self.round_keys[0]
        
        return state