import hashlib
import re


def digits_only(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def is_valid_cpf(value: str) -> bool:
    cpf = digits_only(value)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calculate_digit(base: str, factor: int) -> int:
        total = 0
        for char in base:
            total += int(char) * factor
            factor -= 1
        remainder = (total * 10) % 11
        return 0 if remainder == 10 else remainder

    first = calculate_digit(cpf[:9], 10)
    second = calculate_digit(cpf[:10], 11)
    return first == int(cpf[9]) and second == int(cpf[10])


def mask_cpf(value: str) -> str:
    cpf = digits_only(value)
    if len(cpf) != 11:
        return "***.***.***-**"
    return f"***.***.***-{cpf[-2:]}"


def hash_cpf(value: str, secret: str) -> str:
    cpf = digits_only(value)
    return hashlib.sha256(f"{secret}:{cpf}".encode("utf-8")).hexdigest()
