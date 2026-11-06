import re
from decimal import Decimal, InvalidOperation

PADRAO_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PRECO_MAXIMO = Decimal("10000")


class ErroValidacao(Exception):
    def __init__(self, erros):
        super().__init__("; ".join(erros.values()))
        self.erros = erros


def somente_digitos(valor):
    return re.sub(r"\D", "", valor or "")


def validar_nome(valor, campo, erros, maximo=80):
    nome = " ".join((valor or "").split())
    if not 2 <= len(nome) <= maximo:
        erros[campo] = f"Informe um nome entre 2 e {maximo} caracteres."
    return nome


def validar_telefone(valor, campo, erros, obrigatorio=True):
    digitos = somente_digitos(valor)
    if not digitos:
        if obrigatorio:
            erros[campo] = "Informe o telefone com DDD."
        return None
    if len(digitos) not in (10, 11):
        erros[campo] = "O telefone precisa de DDD e 8 ou 9 dígitos."
    return digitos


def validar_email(valor, campo, erros, obrigatorio=False):
    email = (valor or "").strip().lower()
    if not email:
        if obrigatorio:
            erros[campo] = "Informe o e-mail."
        return None
    if len(email) > 120 or not PADRAO_EMAIL.match(email):
        erros[campo] = "Informe um e-mail válido, como nome@exemplo.com."
    return email


def validar_texto_opcional(valor, campo, erros, maximo):
    texto = (valor or "").strip()
    if len(texto) > maximo:
        erros[campo] = f"Use no máximo {maximo} caracteres."
    return texto or None


def converter_preco(valor, campo, erros):
    texto = (valor or "").replace("R$", "").replace(" ", "").strip()
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        numero = Decimal(texto)
    except InvalidOperation:
        numero = None
    if numero is None or not numero.is_finite():
        erros[campo] = "Informe um preço válido, como 35,00."
        return None
    if numero <= 0:
        erros[campo] = "O preço precisa ser maior que zero."
        return None
    if numero > PRECO_MAXIMO:
        erros[campo] = "O preço não pode passar de R$ 10.000,00."
        return None
    return int((numero * 100).quantize(Decimal("1")))


def converter_inteiro(valor, campo, erros, minimo, maximo, mensagem):
    try:
        numero = int(str(valor).strip())
    except (TypeError, ValueError):
        numero = None
    if numero is None or not minimo <= numero <= maximo:
        erros[campo] = mensagem
        return None
    return numero


def converter_id(valor, campo, erros, mensagem):
    return converter_inteiro(valor, campo, erros, 1, 2**63 - 1, mensagem)


def formatar_preco(centavos):
    if centavos is None:
        return ""
    reais, resto = divmod(int(centavos), 100)
    return "R$ " + f"{reais:,}".replace(",", ".") + f",{resto:02d}"


def formatar_preco_campo(centavos):
    reais, resto = divmod(int(centavos), 100)
    return f"{reais},{resto:02d}"


def formatar_telefone(digitos):
    if not digitos:
        return ""
    if len(digitos) == 11:
        return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
    if len(digitos) == 10:
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    return digitos
