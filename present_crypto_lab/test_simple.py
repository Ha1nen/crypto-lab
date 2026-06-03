import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from present.cipher import Present80
import random

def simple_test():
    key = 0x1234567890ABCDEF1234
    plain = 0x0000000000000001
    
    print("simple encryption test")
    print("-" * 40)
    
    for rounds in [5, 15, 31]:
        cipher = Present80(key, rounds=rounds)
        ct1 = cipher.encrypt_block(plain)
        ct2 = cipher.encrypt_block(plain ^ 1)
        
        diff = bin(ct1 ^ ct2).count('1')
        print(f"rounds={rounds:2d}: ciphertext diff = {diff:2d}/64 bits ({diff/64*100:.1f}%)")
    
    print()
    print("comparing ciphertexts for same plaintext:")
    
    ciphers = {r: Present80(key, rounds=r) for r in [5, 15, 31]}
    cts = {r: ciphers[r].encrypt_block(plain) for r in [5, 15, 31]}
    
    for r in [5, 15, 31]:
        print(f"  rounds={r:2d}: {cts[r]:016X}")
    
    print()
    if cts[5] == cts[15] == cts[31]:
        print("ERROR: all rounds produce same ciphertext!")
    else:
        print("OK: different rounds produce different ciphertext")

if __name__ == "__main__":
    simple_test()