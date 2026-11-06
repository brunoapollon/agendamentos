function somenteDigitos(texto) {
  return String(texto || "").replace(/\D/g, "").slice(0, 11);
}

function formatarTelefone(texto) {
  const digitos = somenteDigitos(texto);
  if (digitos.length === 0) return "";
  if (digitos.length <= 2) return `(${digitos}`;
  const ddd = digitos.slice(0, 2);
  const numero = digitos.slice(2);
  if (numero.length <= 4) return `(${ddd}) ${numero}`;
  const corte = digitos.length === 11 ? 5 : 4;
  return `(${ddd}) ${numero.slice(0, corte)}-${numero.slice(corte)}`;
}

function somarMinutos(hora, minutos) {
  const partes = String(hora || "").split(":").map(Number);
  const quantidade = Number(minutos);
  if (partes.length < 2 || partes.some(Number.isNaN) || Number.isNaN(quantidade)) return "";
  const total = partes[0] * 60 + partes[1] + quantidade;
  if (total >= 24 * 60) return "";
  const horas = String(Math.floor(total / 60)).padStart(2, "0");
  const resto = String(total % 60).padStart(2, "0");
  return `${horas}:${resto}`;
}

function formatarPreco(centavos) {
  const valor = Math.round(Number(centavos));
  if (!Number.isFinite(valor)) return "";
  const reais = String(Math.floor(valor / 100)).replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  const resto = String(valor % 100).padStart(2, "0");
  return `R$ ${reais},${resto}`;
}

function descreverPrevisao(hora, duracao, preco) {
  if (!hora || !duracao) return "";
  const fim = somarMinutos(hora, duracao);
  if (!fim) return "";
  return `Término previsto às ${fim}. Valor: ${formatarPreco(preco)}.`;
}

function ligarMascaraTelefone(raiz) {
  raiz.querySelectorAll("input[data-telefone]").forEach((campo) => {
    campo.value = formatarTelefone(campo.value);
    campo.addEventListener("input", () => {
      campo.value = formatarTelefone(campo.value);
    });
  });
}

function ligarConfirmacoes(raiz) {
  raiz.querySelectorAll("form[data-confirmar]").forEach((formulario) => {
    formulario.addEventListener("submit", (evento) => {
      if (!window.confirm(formulario.dataset.confirmar)) evento.preventDefault();
    });
  });
}

function ligarEnvioAutomatico(raiz) {
  raiz.querySelectorAll("form[data-enviar-ao-mudar]").forEach((formulario) => {
    formulario.addEventListener("change", () => formulario.submit());
  });
}

function ligarPrevisao(raiz) {
  const servico = raiz.querySelector("#servico_id");
  const hora = raiz.querySelector("#hora");
  const previsao = raiz.querySelector("[data-previsao]");
  if (!servico || !hora || !previsao) return;
  const atualizar = () => {
    const opcao = servico.selectedOptions[0];
    previsao.textContent = opcao
      ? descreverPrevisao(hora.value, opcao.dataset.duracao, opcao.dataset.preco)
      : "";
  };
  servico.addEventListener("change", atualizar);
  hora.addEventListener("input", atualizar);
  atualizar();
}

function iniciar(raiz) {
  ligarMascaraTelefone(raiz);
  ligarConfirmacoes(raiz);
  ligarEnvioAutomatico(raiz);
  ligarPrevisao(raiz);
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { somenteDigitos, formatarTelefone, somarMinutos, formatarPreco, descreverPrevisao };
} else {
  document.addEventListener("DOMContentLoaded", () => iniciar(document));
}
