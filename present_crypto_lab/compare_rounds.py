from present.cipher import Present80
import random
from present.utils import hamming_distance

def test_rounds_count():
    plain = random.getrandbits(64)
    key = random.getrandbits(80)
    bit_pos = 0
    
    print(f"plain: 0x{plain:016X}")
    print(f"key: 0x{key:020X}")
    print()
    
    for rounds in [5, 10, 15, 20, 25, 31]:
        cipher = Present80(key, rounds=rounds)
        c1 = cipher.encrypt_block(plain)
        c2 = cipher.encrypt_block(plain ^ (1 << bit_pos))
        diff = hamming_distance(c1, c2)
        
        print(f"rounds={rounds:2d}: {diff:2d}/64 bits changed ({diff/64*100:5.1f}%)")

if __name__ == "__main__":
    test_rounds_count()