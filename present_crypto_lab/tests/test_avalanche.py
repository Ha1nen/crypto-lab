import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import matplotlib.pyplot as plt
import numpy as np
from present.cipher import Present80
from present.utils import hamming_distance


class AvalancheTester:
    def __init__(self, num_tests=200, rounds=31):
        self.num_tests = num_tests
        self.rounds = rounds
        self.avalanche_scores = []
        self.results = {}
    
    def test_single_bit_avalanche(self, plaintext, key, bit_position):
        cipher = Present80(key, rounds=self.rounds)  # исправлено: Present80, не Present
        ciphertext1 = cipher.encrypt_block(plaintext)
        plaintext2 = plaintext ^ (1 << bit_position)
        ciphertext2 = cipher.encrypt_block(plaintext2)
        return hamming_distance(ciphertext1, ciphertext2)
    
    def run_avalanche_test(self):
        print(f"avalanche test: {self.num_tests} samples x 64 bits, rounds={self.rounds}")
        
        all_changes = []
        
        for test_id in range(self.num_tests):
            plaintext = random.getrandbits(64)
            key = random.getrandbits(80)
            
            for bit_pos in range(64):
                changed_bits = self.test_single_bit_avalanche(plaintext, key, bit_pos)
                all_changes.append(changed_bits)
            
            if (test_id + 1) % 50 == 0:
                print(f"  progress: {test_id + 1}/{self.num_tests}")
        
        self.avalanche_scores = all_changes
        self._calculate_statistics()
        self._print_results()
        
        return self.results
    
    def _calculate_statistics(self):
        changes = np.array(self.avalanche_scores)
        
        self.results = {
            'total_samples': len(changes),
            'mean': np.mean(changes),
            'median': np.median(changes),
            'std_dev': np.std(changes),
            'min': np.min(changes),
            'max': np.max(changes),
            'ideal': 32.0,
            'deviation_from_ideal': abs(np.mean(changes) - 32.0),
            'percentage': (np.mean(changes) / 64) * 100
        }
    
    def _print_results(self):
        print()
        print("results:")
        print(f"  rounds: {self.rounds}")
        print(f"  samples: {self.results['total_samples']}")
        print(f"  mean: {self.results['mean']:.2f} / 64 ({self.results['percentage']:.1f}%)")
        print(f"  ideal: 32.00 / 64 (50.0%)")
        print(f"  deviation: {self.results['deviation_from_ideal']:.3f}")
        print(f"  median: {self.results['median']:.1f}")
        print(f"  std dev: {self.results['std_dev']:.3f}")
        print(f"  min: {self.results['min']}")
        print(f"  max: {self.results['max']}")
        
        if self.results['deviation_from_ideal'] < 1.0:
            print("  grade: excellent")
        elif self.results['deviation_from_ideal'] < 2.0:
            print("  grade: good")
        elif self.results['deviation_from_ideal'] < 3.0:
            print("  grade: pass")
        else:
            print("  grade: poor")
    
    def plot_histogram(self, save_path=None):
        os.makedirs('results', exist_ok=True)
        if save_path is None:
            save_path = f'results/avalanche_r{self.rounds}.png'
        
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        plt.hist(self.avalanche_scores, bins=range(65), alpha=0.7, color='blue', edgecolor='black')
        plt.axvline(x=32, color='red', linestyle='--', linewidth=1)
        plt.axvline(x=self.results['mean'], color='green', linestyle='-', linewidth=1)
        plt.xlabel('changed bits')
        plt.ylabel('frequency')
        plt.title(f'avalanche distribution (rounds={self.rounds})')
        
        plt.subplot(1, 2, 2)
        plt.hist(self.avalanche_scores, bins=30, alpha=0.7, color='purple', edgecolor='black', density=True)
        x = np.linspace(0, 64, 100)
        from scipy.stats import norm
        y = norm.pdf(x, self.results['mean'], self.results['std_dev'])
        plt.plot(x, y, 'r-', linewidth=1)
        plt.xlabel('changed bits')
        plt.ylabel('density')
        plt.title('normalized distribution')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        print(f"plot saved: {save_path}")
    
    def generate_report(self):
        os.makedirs('results', exist_ok=True)
        filename = f'results/avalanche_r{self.rounds}.txt'
        with open(filename, 'w') as f:
            f.write(f"present-80 avalanche test\n")
            f.write(f"rounds: {self.rounds}\n")
            f.write(f"blocks: {self.num_tests}\n")
            f.write(f"samples: {self.results['total_samples']}\n\n")
            f.write(f"mean: {self.results['mean']:.2f} / 64\n")
            f.write(f"ideal: 32.00 / 64\n")
            f.write(f"deviation: {self.results['deviation_from_ideal']:.3f}\n")
            f.write(f"std dev: {self.results['std_dev']:.3f}\n")
            f.write(f"min: {self.results['min']}\n")
            f.write(f"max: {self.results['max']}\n")
        
        print(f"report saved: {filename}")


def main():
    print("avalanche test with selectable rounds")
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
    
    num_tests = 200
    print(f"using {num_tests} test blocks\n")
    
    tester = AvalancheTester(num_tests=num_tests, rounds=rounds)
    results = tester.run_avalanche_test()
    tester.plot_histogram()
    tester.generate_report()


if __name__ == "__main__":
    main()