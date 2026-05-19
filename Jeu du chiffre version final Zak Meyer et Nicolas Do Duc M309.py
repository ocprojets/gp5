from machine import Pin, SPI
import utime, urandom

# ── MAX7219 ──────────────────────────────────────────────────
spi = SPI(0, baudrate=1_000_000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(19))
cs = Pin(17, Pin.OUT)
cs.value(1)

def w(reg, val):
    cs.value(0)
    spi.write(bytes([reg, val]))
    cs.value(1)

def max_init():
    w(0x0F, 0x00)
    w(0x09, 0x00)
    w(0x0A, 0x08)
    w(0x0B, 0x07)
    w(0x0C, 0x01)
    cls()

def cls():
    for r in range(1, 9):
        w(r, 0x00)

def show(sprite):
    for i, val in enumerate(sprite):
        w(i + 1, val)

# ── Sprites ──────────────────────────────────────────────────
ARROW_UP = [
    0b00010000,
    0b00110000,
    0b01110000,
    0b11111111,
    0b11111111,
    0b01110000,
    0b00110000,
    0b00010000,
]
ARROW_DOWN = [
    0b00001000,
    0b00001100,
    0b00001110,
    0b11111111,
    0b11111111,
    0b00001110,
    0b00001100,
    0b00001000,
]
SMILEY = [
    0b00111100,
    0b01000010,
    0b10101001,
    0b10000101,
    0b10000101,
    0b10101001,
    0b01000010,
    0b00111100,
]

QUESTION = [
    0b00000000,
    0b01100000,
    0b10010000,
    0b10011101,
    0b10000000,
    0b01           000000,
    0b00000000,
    0b00000000,
]

# ── Clavier ──────────────────────────────────────────────────
KEYS = [
    ['1','2','3'],
    ['4','5','6'],
    ['7','8','9'],
    ['*','0','#'],
]
rows_k = [Pin(p, Pin.OUT) for p in (0, 1, 2, 3)]
cols_k = [Pin(p, Pin.IN, Pin.PULL_DOWN) for p in (4, 5, 6)]
for r in rows_k:
    r.value(0)

def read_key():
    for i, row in enumerate(rows_k):
        row.value(1)
        for j, col in enumerate(cols_k):
            if col.value() == 1:
                row.value(0)
                utime.sleep_ms(300)
                return KEYS[i][j]
        row.value(0)
    return None

def input_number():
    """Saisie du nombre, affiché uniquement dans Thonny. # pour valider, * pour effacer."""
    digits = []
    show(QUESTION)
    print("Entrez un nombre (1-100), # pour valider, * pour effacer")

    while True:
        key = read_key()
        if key is None:
            utime.sleep_ms(20)
            continue

        if key == '#':
            if digits:
                val = int(''.join(digits))
                if 1 <= val <= 100:
                    print(">> Validé :", val)
                    return val
                else:
                    print("!! Hors limite (1-100), recommence")
                    digits = []
                    print("Entrez un nombre :")

        elif key == '*':
            if digits:
                digits.pop()
            print("Effacé →", ''.join(digits) if digits else '(vide)')

        elif key.isdigit() and len(digits) < 3:
            digits.append(key)
            print(''.join(digits))

# ── Jeu ──────────────────────────────────────────────────────
def play():
    secret = urandom.randint(1, 100)
    attempts = 0
    print("\n=== NOUVEAU JEU === (secret:", secret, ")")

    while True:
        guess = input_number()
        attempts += 1

        if guess == secret:
            show(SMILEY)
            print("GAGNÉ en", attempts, "essais !")
            utime.sleep_ms(3000)
            return

        elif guess < secret:
            show(ARROW_UP)
            print("Trop petit ↑")
            utime.sleep_ms(1500)
            show(QUESTION)

        else:
            show(ARROW_DOWN)
            print("Trop grand ↓")
            utime.sleep_ms(1500)
            show(QUESTION)

# ── Boucle ───────────────────────────────────────────────────
def main():
    max_init()
    show(QUESTION)
    print("=== Devine le nombre ! ===")

    while True:
        play()
        utime.sleep_ms(1000)
        print("\nAppuie sur une touche pour rejouer...")
        show(QUESTION)
        while read_key() is None:
            utime.sleep_ms(20)

main()