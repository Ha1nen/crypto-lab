"""
Вспомогательные функции для работы с битовыми операциями
"""

def bit_permutation(input_value, permutation_table, input_bits=64):
    """
    Выполняет перестановку бит согласно таблице
    
    Args:
        input_value: целое число (до input_bits бит)
        permutation_table: список новой позиции для каждого бита
        input_bits: количество бит во входном значении
    
    Returns:
        целое число с переставленными битами
    """
    output = 0
    for new_pos, old_pos in enumerate(permutation_table):
        # Забираем бит из старой позиции
        bit = (input_value >> old_pos) & 1
        # Устанавливаем его в новую позицию
        output |= (bit << new_pos)
    return output


def bytes_to_int(data):
    """Преобразует байтовую строку в целое число (little-endian)"""
    return int.from_bytes(data, byteorder='little')


def int_to_bytes(value, length=8):
    """Преобразует целое число в байтовую строку (little-endian)"""
    return value.to_bytes(length, byteorder='little')


def hamming_distance(x, y, bits=64):
    """Вычисляет расстояние Хэмминга (количество различных бит)"""
    xor = x ^ y
    return bin(xor).count('1')  # считаем единицы в XOR


def hex_dump(value, bits=64):
    """Красивый вывод hex-значения с заданной битностью"""
    hex_len = bits // 4
    return f"0x{value:0{hex_len}X}"


def split_nibbles(state):
    """
    Разбивает 64-битное состояние на 16 нибблов (по 4 бита)
    
    Returns:
        список из 16 чисел от 0 до 15
    """
    nibbles = []
    for i in range(16):
        nibble = (state >> (4 * i)) & 0xF
        nibbles.append(nibble)
    return nibbles


def combine_nibbles(nibbles):
    """
    Объединяет 16 нибблов в 64-битное состояние
    """
    state = 0
    for i, nibble in enumerate(nibbles):
        state |= (nibble & 0xF) << (4 * i)
    return state