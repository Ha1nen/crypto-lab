

import random
from collections import Counter

# S-BOX PRESENT

SBOX = [
    0xC, 0x5, 0x6, 0xB,
    0x9, 0x0, 0xA, 0xD,
    0x3, 0xE, 0xF, 0x8,
    0x4, 0x7, 0x1, 0x2
]

# P-BOX PRESENT
PBOX = [
     0, 16, 32, 48,  1, 17, 33, 49,
     2, 18, 34, 50,  3, 19, 35, 51,
     4, 20, 36, 52,  5, 21, 37, 53,
     6, 22, 38, 54,  7, 23, 39, 55,
     8, 24, 40, 56,  9, 25, 41, 57,
    10, 26, 42, 58, 11, 27, 43, 59,
    12, 28, 44, 60, 13, 29, 45, 61,
    14, 30, 46, 62, 15, 31, 47, 63
]

# XOR

def add_round_key(state, round_key):
    return state ^ round_key

# S-BOX Layer

def sbox_layer(state):
    result = 0

    for i in range(16):
        nibble = (state >> (i * 4)) & 0xF
        result |= SBOX[nibble] << (i * 4)

    return result

# P-BOX Layer

def pbox_layer(state):
    result = 0

    for i in range(64):
        bit = (state >> i) & 1
        result |= bit << PBOX[i]

    return result

# Генерация раундовых ключей

def generate_round_keys(key, rounds):
    round_keys = []

    for round_counter in range(1, rounds + 1):

        round_keys.append(key >> 16)

        # циклический сдвиг
        key = ((key << 61) & ((1 << 80) - 1)) | (key >> 19)

        # SBOX
        top4 = (key >> 76) & 0xF
        key &= ~(0xF << 76)
        key |= SBOX[top4] << 76

        # XOR номера раунда
        key ^= round_counter << 15

    return round_keys

# PRESENT-80 шифрование

def present_encrypt(plaintext, key, rounds):

    state = plaintext

    round_keys = generate_round_keys(key, rounds)

    print("\n")
    print("НАЧАЛО ШИФРОВАНИЯ")

    for i in range(rounds):

        print(f"\n----- Раунд {i + 1} -----")

        print("Состояние до XOR:")
        print(hex(state))

        state = add_round_key(state, round_keys[i])

        print("После XOR с ключом:")
        print(hex(state))

        state = sbox_layer(state)

        print("После SBOX:")
        print(hex(state))

        state = pbox_layer(state)

        print("После PBOX:")
        print(hex(state))

    print("\n")
    print("ШИФРОВАНИЕ ЗАВЕРШЕНО")

    return state

# Подсчёт различий битов

def count_bit_difference(a, b):
    return bin(a ^ b).count("1")

# Проверка 1
# Лавинный эффект

def avalanche_test(text, key, rounds):

    print("\n")
    print("ПРОВЕРКА 1: ЛАВИННЫЙ ЭФФЕКТ")

    cipher1 = present_encrypt(text, key, rounds)

    # меняем 1 бит
    modified_text = text ^ 1

    print("\nИзменяем 1 бит исходного текста")

    cipher2 = present_encrypt(modified_text, key, rounds)

    diff = count_bit_difference(cipher1, cipher2)

    print("\nРезультаты:")
    print("Первый шифртекст :", hex(cipher1))
    print("Второй шифртекст :", hex(cipher2))

    print(f"\nКоличество изменённых битов: {diff} из 64")

    percent = diff / 64 * 100

    print(f"Процент изменений: {percent:.2f}%")

    if percent >= 40:
        print("\nПРОВЕРКА ПРОЙДЕНА")
        print("Лавинный эффект хороший.")
        print("Даже изменение 1 бита сильно меняет результат.")
    else:
        print("\nПРОВЕРКА НЕ ПРОЙДЕНА")
        print("Шифр недостаточно чувствителен к изменению данных.")

# Проверка 2
# Частотный анализ битов

def frequency_test(text, key, rounds):

    print("\n")
    print("ПРОВЕРКА 2: ЧАСТОТНЫЙ АНАЛИЗ")

    cipher = present_encrypt(text, key, rounds)

    bits = bin(cipher)[2:].zfill(64)

    counter = Counter(bits)

    zeros = counter['0']
    ones = counter['1']

    print("\nШифртекст:")
    print(hex(cipher))

    print("\nКоличество нулей :", zeros)
    print("Количество единиц:", ones)

    diff = abs(zeros - ones)

    print("\nРазница между количеством битов:", diff)

    if diff <= 10:
        print("\nПРОВЕРКА ПРОЙДЕНА")
        print("Распределение битов близко к случайному.")
    else:
        print("\nПРОВЕРКА НЕ ПРОЙДЕНА")
        print("Есть перекос в распределении битов.")

# Проверка 3
# Чувствительность к ключу

def key_sensitivity_test(text, key, rounds):

    print("\n")
    print("ПРОВЕРКА 3: ЧУВСТВИТЕЛЬНОСТЬ К КЛЮЧУ")
    print("")

    cipher1 = present_encrypt(text, key, rounds)

    # меняем 1 бит ключа
    modified_key = key ^ 1

    print("\nИзменяем 1 бит ключа")

    cipher2 = present_encrypt(text, modified_key, rounds)

    diff = count_bit_difference(cipher1, cipher2)

    print("\nРезультаты:")
    print("Первый шифртекст :", hex(cipher1))
    print("Второй шифртекст :", hex(cipher2))

    print(f"\nКоличество изменённых битов: {diff} из 64")

    percent = diff / 64 * 100

    print(f"Процент изменений: {percent:.2f}%")

    if percent >= 40:
        print("\nПРОВЕРКА ПРОЙДЕНА")
        print("Шифр хорошо реагирует на изменение ключа.")
    else:
        print("\nПРОВЕРКА НЕ ПРОЙДЕНА")
        print("Изменение ключа слабо влияет на результат.")

# Главное меню

def main():

    print("\n")
    print("PRESENT-80")

    text_input = input(
        "\nВведите 16-символьный HEX текст (64 бита):\n"
    )

    key_input = input(
        "\nВведите 20-символьный HEX ключ (80 бит):\n"
    )

    rounds = int(input(
        "\nВведите количество раундов:\n"
    ))

    plaintext = int(text_input, 16)
    key = int(key_input, 16)

    print("\n")
    print("Выберите проверку")
    print("1 - Лавинный эффект")
    print("2 - Частотный анализ")
    print("3 - Чувствительность к ключу")

    choice = input("\nВаш выбор: ")

    if choice == "1":
        avalanche_test(plaintext, key, rounds)

    elif choice == "2":
        frequency_test(plaintext, key, rounds)

    elif choice == "3":
        key_sensitivity_test(plaintext, key, rounds)

    else:
        print("\nНеверный выбор.")


if __name__ == "__main__":
    main()