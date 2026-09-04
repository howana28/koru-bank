from app.services.cpf import hash_cpf, is_valid_cpf, mask_cpf


def test_valid_cpf():
    assert is_valid_cpf("529.982.247-25") is True


def test_invalid_cpf():
    assert is_valid_cpf("111.111.111-11") is False
    assert is_valid_cpf("123") is False


def test_mask_and_hash_do_not_store_plain_value():
    cpf = "529.982.247-25"
    assert mask_cpf(cpf) == "***.***.***-25"
    digest = hash_cpf(cpf, "secret")
    assert len(digest) == 64
    assert "52998224725" not in digest
