import { describe, expect, it } from 'vitest'
import { formatCpf, isValidCpf } from './cpf'

describe('CPF utilities', () => {
  it('accepts a mathematically valid CPF', () => {
    expect(isValidCpf('529.982.247-25')).toBe(true)
  })

  it('rejects repeated digits and malformed CPF', () => {
    expect(isValidCpf('111.111.111-11')).toBe(false)
    expect(isValidCpf('123')).toBe(false)
  })

  it('formats digits as CPF', () => {
    expect(formatCpf('52998224725')).toBe('529.982.247-25')
  })
})
