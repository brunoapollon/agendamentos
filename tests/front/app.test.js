const test = require("node:test");
const assert = require("node:assert/strict");
const {
  somenteDigitos,
  formatarTelefone,
  somarMinutos,
  formatarPreco,
  descreverPrevisao,
} = require("../../app/static/js/app.js");

test("remove tudo que não é dígito e limita a 11", () => {
  assert.equal(somenteDigitos("(85) 98888-7777 ramal 2"), "85988887777");
});

test("aplica máscara de celular e de fixo", () => {
  assert.equal(formatarTelefone("85988887777"), "(85) 98888-7777");
  assert.equal(formatarTelefone("8532110004"), "(85) 3211-0004");
});

test("máscara acompanha a digitação parcial", () => {
  assert.equal(formatarTelefone(""), "");
  assert.equal(formatarTelefone("8"), "(8");
  assert.equal(formatarTelefone("859"), "(85) 9");
  assert.equal(formatarTelefone("8598888"), "(85) 9888-8");
});

test("soma a duração ao horário de início", () => {
  assert.equal(somarMinutos("09:40", 50), "10:30");
  assert.equal(somarMinutos("19:30", 30), "20:00");
});

test("horário inválido ou que vira o dia não gera previsão", () => {
  assert.equal(somarMinutos("", 30), "");
  assert.equal(somarMinutos("23:50", 30), "");
  assert.equal(somarMinutos("10:00", "x"), "");
});

test("formata centavos em reais", () => {
  assert.equal(formatarPreco(3500), "R$ 35,00");
  assert.equal(formatarPreco(120090), "R$ 1.200,90");
});

test("monta a frase de previsão do agendamento", () => {
  assert.equal(descreverPrevisao("10:00", "30", "3500"), "Término previsto às 10:30. Valor: R$ 35,00.");
  assert.equal(descreverPrevisao("", "30", "3500"), "");
});
