from PIL import Image
import numpy as np
import hashlib
import random
import sys

def key_to_seed(key: str) -> int:
    h = hashlib.sha256(key.encode("utf-8")).digest()
    seed = int.from_bytes(h[:8], byteorder="big", signed=False)
    return seed

def build_xor_stream(length: int, key: str) -> np.ndarray:
    seed = key_to_seed(key + "_xor")
    rng = random.Random(seed)
    return np.fromiter((rng.randrange(0, 256) for _ in range(length)), dtype=np.uint8)

def build_permutation(length: int, key: str) -> np.ndarray:
    seed = key_to_seed(key + "_perm")
    idx = list(range(length))
    rng = random.Random(seed)
    rng.shuffle(idx)
    return np.array(idx, dtype=np.int64)

def encrypt_image(input_path: str, output_path: str, key: str):
    img = Image.open(input_path).convert("RGBA")
    arr = np.array(img)
    h, w, c = arr.shape
    flat = arr.reshape(-1).astype(np.uint8)
    xor_stream = build_xor_stream(flat.size, key)
    xored = np.bitwise_xor(flat, xor_stream)
    pixels = xored.reshape(-1, c)
    perm = build_permutation(pixels.shape[0], key)
    permuted = pixels[perm]
    enc_flat = permuted.reshape(-1)
    enc_arr = enc_flat.reshape(h, w, c)
    enc_img = Image.fromarray(enc_arr, mode="RGBA")
    enc_img.save(output_path)
    print(f"Encrypted saved to: {output_path}")

def decrypt_image(input_path: str, output_path: str, key: str):
    img = Image.open(input_path).convert("RGBA")
    arr = np.array(img)
    h, w, c = arr.shape
    flat = arr.reshape(-1).astype(np.uint8)
    pixels = flat.reshape(-1, c)
    perm = build_permutation(pixels.shape[0], key)
    inv_perm = np.empty_like(perm)
    inv_perm[perm] = np.arange(perm.size)
    unpermuted = pixels[inv_perm]
    unpermuted_flat = unpermuted.reshape(-1)
    xor_stream = build_xor_stream(unpermuted_flat.size, key)
    original_flat = np.bitwise_xor(unpermuted_flat, xor_stream)
    orig_arr = original_flat.reshape(h, w, c)
    orig_img = Image.fromarray(orig_arr, mode="RGBA")
    orig_img.save(output_path)
    print(f"Decrypted saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python simple_image_encryptor.py encrypt|decrypt in.png out.png \"your key\"")
        sys.exit(1)

    action, input_path, output_path, key = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    if action == "encrypt":
        encrypt_image(input_path, output_path, key)
    elif action == "decrypt":
        decrypt_image(input_path, output_path, key)
    else:
        print("Unknown action:", action)
