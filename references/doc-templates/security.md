# SECURITY — <Nome da feature/serviço>

> Modelo de ameaças + controles. Ancore em OWASP Top 10 e LGPD (north library).

## 1. Ativos & dados sensíveis
- O que protegemos (PII, credenciais, tokens). Classificação LGPD (dado pessoal/sensível).

## 2. Superfície & atores
- Entradas (endpoints, filas, uploads), fronteiras de confiança, quem chama o quê.

## 3. Ameaças (STRIDE / OWASP Top 10)
| # | Ameaça | Vetor | Impacto | Mitigação | Status |
|---|---|---|---|---|---|
| 1 | Injeção (SQL/cmd) | ... | alto | parametrização / validação | [ ] |
| 2 | AuthN/AuthZ quebrada | ... | alto | ... | [ ] |
| 3 | Exposição de dados | ... | ... | mascaramento/cripto | [ ] |

## 4. AuthN / AuthZ
- Como autentica/autoriza; fronteira de confiança (ex.: X-Api-Key no gateway); least privilege.

## 5. Segredos & criptografia
- Onde vivem os segredos (nunca no código), em trânsito (TLS) e em repouso.

## 6. LGPD
- Base legal, minimização, retenção, direito do titular, logs sem PII.

## 7. Logging & resposta a incidente
- O que logar (sem vazar PII), alertas, plano de resposta.

## 8. Checklist de saída (DoD de segurança)
- [ ] Sem segredo no código  [ ] Inputs validados  [ ] AuthZ testada
- [ ] Dependências sem CVE crítico  [ ] Headers/CORS revisados

---
*Referências consultadas (north library):* <citar — ex.: 18-cybersecurity.md, OWASP>
