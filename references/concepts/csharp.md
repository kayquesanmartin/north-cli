# Catálogo de conceitos — C# / .NET

Mapa conceito → categoria → dificuldade (jr/pl/sr) usado pelos **insights passivos**
do north para ranquear o que ensinar. A IA mapeia o que usou no código contra esta
tabela; conceitos fora dela recebem dificuldade julgada pela IA (default `pl`).

`Aliases` ajuda o casamento (símbolos/sinônimos), separados por vírgula.

| Conceito | Categoria | Dificuldade | Aliases |
|---|---|---|---|
| variáveis e tipos | fundamentos | jr | var, tipos primitivos, int, string, bool |
| if/else | controle-de-fluxo | jr | condicional, if, else, ternário |
| switch / switch expression | controle-de-fluxo | pl | switch, switch expression, case |
| loops | controle-de-fluxo | jr | for, foreach, while, do-while |
| arrays | coleções | jr | array, vetor |
| List e coleções | coleções | jr | List, Dictionary, HashSet, IEnumerable |
| nullable operators | null-safety | pl | ?., ??, ??=, null-conditional, null-coalescing |
| nullable reference types | null-safety | sr | NRT, #nullable, string? |
| string interpolation | fundamentos | jr | $"...", interpolação |
| métodos e parâmetros | fundamentos | jr | método, função, parâmetro, return |
| classes e objetos | OOP | jr | class, objeto, propriedade, campo |
| herança e polimorfismo | OOP | pl | herança, override, virtual, base |
| interfaces | OOP | pl | interface, contrato, abstração |
| records | OOP | pl | record, init, with-expression |
| generics | tipos | sr | generic, T, where, restrição de tipo |
| LINQ | coleções | pl | Where, Select, FirstOrDefault, GroupBy, query |
| lambda e delegates | funcional | pl | lambda, =>, Func, Action, delegate |
| pattern matching | controle-de-fluxo | sr | is, switch pattern, when, deconstruction |
| async/await | concorrência | sr | async, await, Task, ConfigureAwait |
| exceções | robustez | pl | try/catch, throw, finally, exception |
| using e IDisposable | recursos | pl | using, IDisposable, Dispose, using declaration |
| injeção de dependência | arquitetura | sr | DI, IServiceCollection, construtor injection |
| EF Core | dados | sr | DbContext, migration, LINQ-to-Entities, Include |
| extension methods | tipos | pl | this method, método de extensão |
| enum | fundamentos | jr | enumeração, enum |
| imutabilidade | design | sr | readonly, init, immutable, const |
| tuplas e desconstrução | tipos | pl | tuple, (a, b), deconstruct |
| spans e Memory | performance | sr | Span, Memory, stackalloc |
