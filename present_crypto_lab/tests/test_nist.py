import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import math
from present.cipher import Present80
from present.utils import int_to_bytes


def generate_ciphertext_samples(key, rounds, num_blocks=50000):
    cipher = Present80(key, rounds=rounds)
    output = bytearray()
    
    print(f"generating {num_blocks} blocks...")
    for i in range(num_blocks):
        plaintext = random.getrandbits(64)
        ct = cipher.encrypt_block(plaintext)
        output.extend(int_to_bytes(ct, 8))
        
        if (i + 1) % 10000 == 0:
            print(f"  {i + 1}/{num_blocks} blocks")
    
    return bytes(output)


def run_frequency_test(data):
    bits = 0
    for byte in data:
        bits += bin(byte).count('1')
    
    total_bits = len(data) * 8
    ones_ratio = bits / total_bits
    
    # для 3.2M бит, 95% доверительный интервал: 0.5 ± 0.00055
    return {
        'name': 'frequency',
        'ones_ratio': ones_ratio,
        'pass': 0.499 < ones_ratio < 0.501
    }


def run_runs_test(data):
    bits = []
    for byte in data:
        for i in range(8):
            bits.append((byte >> i) & 1)
    
    total_runs = 1
    for i in range(1, len(bits)):
        if bits[i] != bits[i-1]:
            total_runs += 1
    
    total_bits = len(bits)
    ones = sum(bits)
    pi = ones / total_bits
    
    expected_runs = 2 * total_bits * pi * (1 - pi) + 1
    # допустимое отклонение 1%
    deviation = abs(total_runs - expected_runs) / expected_runs
    
    return {
        'name': 'runs',
        'total_runs': total_runs,
        'expected_runs': expected_runs,
        'deviation': deviation,
        'pass': deviation < 0.01
    }


def run_longest_run_test(data):
    bits = []
    for byte in data:
        for i in range(8):
            bits.append((byte >> i) & 1)
    
    max_run = 0
    current_run = 1
    
    for i in range(1, len(bits)):
        if bits[i] == bits[i-1]:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 1
    
    # для 3.2M бит, ожидаемый максимум ~ 22-25, порог 35
    return {
        'name': 'longest_run',
        'max_run': max_run,
        'pass': max_run < 35
    }


def run_autocorrelation_test(data):
    bits = []
    for byte in data:
        for i in range(8):
            bits.append((byte >> i) & 1)
    
    max_deviation = 0
    worst_shift = 0
    
    for shift in range(1, 33):
        matches = 0
        for i in range(len(bits) - shift):
            if bits[i] == bits[i + shift]:
                matches += 1
        ratio = matches / (len(bits) - shift)
        deviation = abs(ratio - 0.5)
        if deviation > max_deviation:
            max_deviation = deviation
            worst_shift = shift
    
    # порог 0.005 ~ 0.5%
    return {
        'name': 'autocorrelation',
        'max_deviation': max_deviation,
        'worst_shift': worst_shift,
        'pass': max_deviation < 0.005
    }


def run_serial_test(data):
    bits = []
    for byte in data:
        for i in range(8):
            bits.append((byte >> i) & 1)
    
    patterns = ['00', '01', '10', '11']
    counts = {p: 0 for p in patterns}
    
    for i in range(len(bits) - 1):
        pattern = f"{bits[i]}{bits[i+1]}"
        counts[pattern] += 1
    
    total = len(bits) - 1
    expected = total / 4
    
    chi_square = sum((counts[p] - expected)**2 / expected for p in patterns)
    
    # порог 7.815 для p=0.05
    return {
        'name': 'serial',
        'chi_square': chi_square,
        'pass': chi_square < 7.815
    }


def run_entropy_test(data):
    from collections import Counter
    from math import log2
    
    byte_counts = Counter(data)
    total = len(data)
    
    entropy = 0
    for count in byte_counts.values():
        p = count / total
        if p > 0:
            entropy -= p * log2(p)
    
    # идеал 8, допустимо 7.99
    return {
        'name': 'entropy',
        'entropy': entropy,
        'pass': entropy > 7.99
    }


def run_chi_square_test(data):
    from collections import Counter
    
    byte_counts = Counter(data)
    total = len(data)
    expected = total / 256
    
    chi_square = 0
    for count in byte_counts.values():
        chi_square += ((count - expected) ** 2) / expected
    
    # для 255 степеней свободы, p=0.05 -> 293
    threshold = 293
    
    return {
        'name': 'chi_square',
        'chi_square': chi_square,
        'pass': chi_square < threshold
    }


def run_monobit_test(data):
    deviations = []
    for byte in data:
        ones = bin(byte).count('1')
        deviations.append(abs(ones - 4))
    
    avg_deviation = sum(deviations) / len(deviations)
    
    # среднее отклонение для случайных данных ~1.0
    return {
        'name': 'monobit_per_byte',
        'avg_deviation': avg_deviation,
        'pass': avg_deviation < 1.1
    }


def run_differential_test(data):
    diffs = []
    for i in range(1, len(data)):
        diff = abs(data[i] - data[i-1])
        diffs.append(diff)
    
    avg_diff = sum(diffs) / len(diffs)
    expected = 85.33
    
    return {
        'name': 'differential',
        'avg_diff': avg_diff,
        'pass': 84 < avg_diff < 86.5
    }


def run_bit_imbalance_test(data):
    bit_counts = [0] * 8
    
    for byte in data:
        for i in range(8):
            if (byte >> i) & 1:
                bit_counts[i] += 1
    
    total = len(data)
    max_deviation = 0
    for i in range(8):
        ratio = bit_counts[i] / total
        deviation = abs(ratio - 0.5)
        max_deviation = max(max_deviation, deviation)
    
    # для 400KB, ожидаемое отклонение ~0.001-0.002
    return {
        'name': 'bit_imbalance',
        'max_deviation': max_deviation,
        'bit_counts': bit_counts,
        'pass': max_deviation < 0.003
    }


def run_all_tests(data, rounds):
    print(f"\ndata size: {len(data)} bytes ({len(data)*8} bits)")
    
    tests = [
        run_frequency_test(data),
        run_runs_test(data),
        run_longest_run_test(data),
        run_autocorrelation_test(data),
        run_serial_test(data),
        run_entropy_test(data),
        run_chi_square_test(data),
        run_monobit_test(data),
        run_differential_test(data),
        run_bit_imbalance_test(data)
    ]
    
    passed = sum(1 for t in tests if t.get('pass', False))
    total = len(tests)
    
    print(f"\nresults (rounds={rounds}):")
    print("-" * 45)
    for t in tests:
        status = "PASS" if t.get('pass', False) else "FAIL"
        print(f"  {t['name']:20s}: {status}")
    
    print("-" * 45)
    print(f"  score: {passed}/{total} tests passed")
    
    # детальный вывод
    print("\ndetails:")
    for t in tests:
        if not t['pass']:
            if t['name'] == 'frequency':
                print(f"  frequency: ratio = {t['ones_ratio']:.6f}")
            elif t['name'] == 'runs':
                print(f"  runs: deviation = {t['deviation']:.6f}")
            elif t['name'] == 'longest_run':
                print(f"  longest_run: max = {t['max_run']}")
            elif t['name'] == 'autocorrelation':
                print(f"  autocorrelation: max deviation = {t['max_deviation']:.6f}")
            elif t['name'] == 'serial':
                print(f"  serial: chi_square = {t['chi_square']:.3f}")
            elif t['name'] == 'entropy':
                print(f"  entropy: {t['entropy']:.6f}")
            elif t['name'] == 'chi_square':
                print(f"  chi_square: {t['chi_square']:.1f}")
            elif t['name'] == 'monobit_per_byte':
                print(f"  monobit: avg_deviation = {t['avg_deviation']:.4f}")
            elif t['name'] == 'differential':
                print(f"  differential: avg_diff = {t['avg_diff']:.2f}")
            elif t['name'] == 'bit_imbalance':
                print(f"  bit_imbalance: max_deviation = {t['max_deviation']:.6f}")
    
    # оценка
    print()
    if passed == total:
        print("  strong - statistically random")
    elif passed >= 8:
        print("  good - minor statistical biases")
    elif passed >= 6:
        print("  moderate - some statistical weaknesses")
    elif passed >= 4:
        print("  weak - significant biases")
    else:
        print("  very weak - cipher may be broken")
    
    return passed, total, tests


def main():
    print("nist statistical tests for present-80")
    print("available rounds: 1-31")
    
    try:
        rounds_input = input("enter rounds (default 31): ").strip()
        if rounds_input == "":
            rounds = 31
        else:
            rounds = int(rounds_input)
            rounds = max(1, min(31, rounds))
    except:
        rounds = 31
    
    key = 0x0123456789ABCDEF0123
    num_blocks = 50000
    
    print(f"\nusing {num_blocks} test blocks (400KB data)")
    
    data = generate_ciphertext_samples(key, rounds, num_blocks=num_blocks)
    
    passed, total, tests = run_all_tests(data, rounds)
    
    os.makedirs('results', exist_ok=True)
    
    with open(f'results/nist_r{rounds}.txt', 'w') as f:
        f.write(f"present-80 nist statistical tests\n")
        f.write(f"rounds: {rounds}\n")
        f.write(f"blocks: {num_blocks}\n")
        f.write(f"bytes: {len(data)}\n\n")
        f.write(f"score: {passed}/{total}\n\n")
        for t in tests:
            status = "PASS" if t.get('pass', False) else "FAIL"
            f.write(f"{t['name']}: {status}\n")
    
    print(f"\nreport saved: results/nist_r{rounds}.txt")


if __name__ == "__main__":
    main()