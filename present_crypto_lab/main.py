import sys
import os

def main():
    print("present-80 cryptanalysis")
    print("1. avalanche effect")
    print("2. nist statistical tests")
    print("3. differential analysis (todo)")
    print("0. exit")
    
    choice = input("\nselect: ").strip()
    
    if choice == '1':
        from tests.test_avalanche import main as avalanche_main
        avalanche_main()
    elif choice == '2':
        from tests.test_nist import main as nist_main
        nist_main()
    elif choice == '3':
        print("not implemented yet")
    elif choice == '0':
        sys.exit(0)
    else:
        print("invalid choice")

if __name__ == "__main__":
    main()