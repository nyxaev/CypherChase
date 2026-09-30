# Cypherchase

A random substitution cipher for text messages, written in pure Python.

Cypherchase generates a random key, replaces every character with one of several randomly chosen codes, and turns the result back into the original text with the same key. No dependencies, no setup, one file.

## Features

- **Truly random key:** the mapping is generated with the operating system's secure random source (`random.SystemRandom`). There is no pattern like `a -> @` to recognize.
- **Multiple codes per character:** frequent characters (`a`, `e`, `o`, space) get more codes, so letter frequencies do not show in the output.
- **Different output every time:** encrypting the same message twice produces two different results, and both decrypt to the original.
- **Lossless round trip:** all codes have the same length, so decryption is exact and unambiguous. Emojis, accents, CJK text and any character outside the alphabet are handled through an escape code.
- **Key file you can share:** the key lives in a plain `chave.json` file. Copy it to decrypt on another machine.
- **Validation and errors:** a malformed key or a message made with a different key produces a clear error instead of garbage.
- **Built-in self-test:** checks the round trip against fixed and random texts.

## Requirements

- Python 3.8 or newer
- Nothing else (standard library only)

## Quick start

```bash
python cypherchase.py
```

On the first run a new key is generated and saved as `key.json` next to the script. After that, the menu appears:

```
1 - Encrypt a message
2 - Decrypt a message
3 - Show demo
4 - Show current key
5 - Generate a new random key
6 - Run self-test
0 - Exit
```

The menu text is currently in Portuguese.

## How it works

1. **Key generation.** Every character of the alphabet (letters, digits, punctuation, space, common Portuguese accents) receives 2 to 6 unique random codes. Codes are short strings of symbols, 2 characters long by default. One extra code is reserved as the escape marker.
2. **Encryption.** Each character is replaced by one of its codes, picked at random. A character with no code (an emoji, for example) becomes the escape code followed by the character itself.
3. **Decryption.** The message is read in fixed-size chunks and each chunk is looked up in the reversed table. After an escape chunk, the next character is copied as is.

Example (your output will be different, and different again on every run):

```
Original : Hello, world!
Encrypted: Rd!R;>DcHM2aqIFmSP@t#2cpGBVC...
Decrypted: Hello, world!
```

## The key file

`chave.json` holds the whole key:

```json
{
  "tamanho": 2,
  "escape": "..",
  "codigos": { "a": ["..", "..", ".."], "b": ["..", ".."] }
}
```

- **Keep it safe.** Anyone with this file can decrypt your messages. Do not commit it to a public repository (see `.gitignore` below).
- **Do not lose it.** Without the key, encrypted messages cannot be recovered.
- **Replacing it.** Deleting the file or using menu option 5 creates a new key, and messages made with the old one can no longer be decrypted.
- **Editing it.** You can edit the file by hand. It is validated on load: codes must be unique, all the same length, and different from the escape code.

## Security notes

Cypherchase is a homophonic substitution cipher. It is much harder to break than a simple letter-for-letter cipher, but it is a hobby project and is **not** a replacement for modern cryptography. For anything sensitive, use a vetted tool such as AES-GCM (for example through the `cryptography` package) or age.

## Suggested `.gitignore`

```
chave.json
__pycache__/
```

## Project structure

```
cypherchase/
├── cypherchase.py   # the whole program
├── README.md
└── .gitignore
```

## License

Choose a license (for example MIT) and add a `LICENSE` file.
