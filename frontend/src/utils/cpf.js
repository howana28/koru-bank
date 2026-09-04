export function onlyDigits(value = '') {
  return value.replace(/\D/g, '').slice(0, 11)
}

export function formatCpf(value = '') {
  const digits = onlyDigits(value)
  return digits
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d{1,2})$/, '$1-$2')
}

export function isValidCpf(value = '') {
  const cpf = onlyDigits(value)
  if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) return false

  const calculateDigit = (base, factor) => {
    let total = 0
    for (const digit of base) {
      total += Number(digit) * factor
      factor -= 1
    }
    const remainder = (total * 10) % 11
    return remainder === 10 ? 0 : remainder
  }

  const first = calculateDigit(cpf.slice(0, 9), 10)
  const second = calculateDigit(cpf.slice(0, 10), 11)
  return first === Number(cpf[9]) && second === Number(cpf[10])
}
