from present.cipher import Present80

def hex_dump(value, bits):
    hex_len = bits // 4
    return f"0x{value:0{hex_len}X}"

print("present-80 test")
print()

key = 0x00000000000000000000
plain = 0x0000000000000000

cipher = Present80(key)
enc = cipher.encrypt_block(plain)
dec = cipher.decrypt_block(enc)

print(f"key:   {hex_dump(key, 80)}")
print(f"plain: {hex_dump(plain, 64)}")
print(f"enc:   {hex_dump(enc, 64)}")
print(f"dec:   {hex_dump(dec, 64)}")
print(f"ok:    {plain == dec}")
print()

import random
test_key = random.getrandbits(80)
test_plain = random.getrandbits(64)

cipher2 = Present80(test_key)
enc2 = cipher2.encrypt_block(test_plain)
dec2 = cipher2.decrypt_block(enc2)

print(f"random key:   {hex_dump(test_key, 80)}")
print(f"random plain: {hex_dump(test_plain, 64)}")
print(f"encrypted:    {hex_dump(enc2, 64)}")
print(f"decrypted:    {hex_dump(dec2, 64)}")
print(f"ok:           {test_plain == dec2}")
print()
print(f"round keys generated: {len(cipher.round_keys)}")