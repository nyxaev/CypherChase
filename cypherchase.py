import json
import random
import string
from pathlib import Path

KEY_FILE = Path(__file__).with_name("key.json")
CODE_LENGTH = 2
CODE_ALPHABET = string.ascii_letters + string.digits + "!@#$%&*+=?<>^~;:/|_-"
ORIGINAL_ALPHABET = (
    string.ascii_letters + string.digits + string.punctuation
    + " \n\t" + "áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ"
)
VERY_FREQUENT_LETTERS = "aeo "
FREQUENT_LETTERS = "srindmutcl"
COUNT_HIGH, COUNT_MEDIUM, COUNT_LOW = 6, 4, 2

class CipherError(ValueError):
    """Invalid key or invalid message error."""
_rng = random.SystemRandom()
def _code_count(c):
    if c.lower() in VERY_FREQUENT_LETTERS:
        return COUNT_HIGH
    if c.lower() in FREQUENT_LETTERS:
        return COUNT_MEDIUM
    return COUNT_LOW
def generate_key(length=CODE_LENGTH):

    characters = list(dict.fromkeys(ORIGINAL_ALPHABET))
    total = sum(_code_count(c) for c in characters) + 1
    if total > len(CODE_ALPHABET) ** length:
        raise CipherError("CODE_LENGTH is too small for the number of codes.")
    used = set()

    def new_code():
        while True:
            code = "".join(_rng.choice(CODE_ALPHABET) for _ in range(length))
            if code not in used:
                used.add(code)
                return code

    escape = new_code()
    codes = {c: [new_code() for _ in range(_code_count(c))]
             for c in characters}
    return {"length": length, "escape": escape, "codes": codes}
class Cipher:
    def __init__(self, key):
        self._validate(key)
        self.length = key["length"]
        self.escape = key["escape"]
        self.codes = key["codes"]

        self.reverse = {code: c for c, codes_list in self.codes.items() for code in codes_list}
    @staticmethod
    def _validate(key):
        errors = []
        try:
            length, esc, codes = key["length"], key["escape"], key["codes"]
        except (KeyError, TypeError):
            raise CipherError("Invalid key: missing 'length', 'escape' or 'codes'.")
        if not isinstance(length, int) or length < 1:
            errors.append("'length' must be an integer >= 1.")
        seen = {esc}
        if not isinstance(esc, str) or len(esc) != length:
            errors.append("'escape' must be a string with the length of one code.")
        for c, codes_list in codes.items():
            if len(c) != 1:
                errors.append(f"Character {c!r}: must be a single character.")
            if not codes_list:
                errors.append(f"Character {c!r}: no codes.")
            for code in codes_list:
                if not isinstance(code, str) or len(code) != length:
                    errors.append(f"Code {code!r} of {c!r}: length is not {length}.")
                elif code in seen:
                    errors.append(f"Duplicate code: {code!r}.")
                seen.add(code)
        if errors:
            raise CipherError("\n".join(errors))

    def encrypt(self, message):
        output = []
        for c in message:
            if c in self.codes:
                output.append(_rng.choice(self.codes[c]))
            else:
                output.append(self.escape + c)
        return "".join(output)

    def decrypt(self, message):
        output = []
        i, n, t = 0, len(message), self.length
        while i < n:
            chunk = message[i:i + t]
            if len(chunk) < t:
                raise CipherError("Invalid message: ends with an incomplete code.")
            if chunk == self.escape:
                if i + t >= n:
                    raise CipherError("Invalid message: escape with no character after it.")
                output.append(message[i + t])
                i += t + 1
            elif chunk in self.reverse:
                output.append(self.reverse[chunk])
                i += t
            else:
                raise CipherError(f"Unknown code at position {i}: {chunk!r} "
                                  f"(wrong key?).")
        return "".join(output)

    def self_test(self, rounds=500):

        fixed = ["", " ", "Hello, World! 123 @#", "😀 emoji and 日本語", "line1\nline2\ttab",
                 self.escape, "".join(self.codes)]
        alphabet = ORIGINAL_ALPHABET + "😀日本語" + self.escape
        random_texts = ["".join(_rng.choices(alphabet, k=_rng.randint(0, 40)))
                        for _ in range(rounds)]
        failures = []
        for text in fixed + random_texts:
            try:
                got = self.decrypt(self.encrypt(text))
            except CipherError as error:
                failures.append((text, f"error: {error}"))
                continue
            if got != text:
                failures.append((text, got))
        return failures



def save_key(key, path=KEY_FILE):
    path.write_text(json.dumps(key, ensure_ascii=False, indent=1), encoding="utf-8")


def load_or_create_key(path=KEY_FILE):

    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise CipherError(f"{path.name} is not valid JSON: {error}")
    key = generate_key()
    save_key(key, path)
    print(f"New key generated and saved to: {path}\n")
    return key

def demo(cipher):
    example = "Hello, World! This is my secret message 123."
    print("\n--- Demo (note that each encrypted line is different) ---")
    print(f"Original : {example}")
    for _ in range(3):
        encoded = cipher.encrypt(example)
        print(f"Encrypted: {encoded}")
        print(f"Decrypted: {cipher.decrypt(encoded)}")
    print()

def show_key(cipher):
    print("\n--- Current key (character -> possible codes) ---")
    for c, codes_list in cipher.codes.items():
        print(f"  {c!r:6} -> {' '.join(codes_list)}")
    print(f"Escape: {cipher.escape} | Code length: {cipher.length}\n")

def run_self_test(cipher):
    failures = cipher.self_test()
    if not failures:
        print("\nSelf-test: all cases passed.\n")
    else:
        print(f"\nSelf-test: {len(failures)} failure(s). First ones:")
        for text, got in failures[:5]:
            print(f"  input={text!r}  got={got!r}")
        print()

def generate_new_key():
    print("\nWARNING: a new key makes it IMPOSSIBLE to decrypt messages "
          "made with the current key.")
    if input("Type 'yes' to confirm: ").strip().lower() != "yes":
        print("Cancelled.\n")
        return None
    key = generate_key()
    save_key(key)
    print(f"New key saved to {KEY_FILE}\n")
    return Cipher(key)

def menu(cipher):
    while True:
        print("=" * 42)
        print("  RANDOM SUBSTITUTION CIPHER")
        print("=" * 42)
        print("  1 - Encrypt a message")
        print("  2 - Decrypt a message")
        print("  3 - Show demo")
        print("  4 - Show current key")
        print("  5 - Generate new random key")
        print("  6 - Run self-test")
        print("  0 - Exit")
        choice = input("Choose an option: ").strip()
        try:
            if choice == "0":
                print("Goodbye!")
                return
            elif choice == "1":
                print(f"Encrypted: {cipher.encrypt(input('Original message: '))}\n")
            elif choice == "2":
                print(f"Decrypted: {cipher.decrypt(input('Encrypted message: '))}\n")
            elif choice == "3":
                demo(cipher)
            elif choice == "4":
                show_key(cipher)
            elif choice == "5":
                cipher = generate_new_key() or cipher
            elif choice == "6":
                run_self_test(cipher)
            else:
                print("Invalid option.\n")
        except CipherError as error:
            print(f"Error: {error}\n")

def main():
    try:
        cipher = Cipher(load_or_create_key())
    except CipherError as error:
        print("Problem with the key:")
        print(error)
        return
    try:
        menu(cipher)
    except (EOFError, KeyboardInterrupt):
        print("\nExited.")


if __name__ == "__main__":
    main()
