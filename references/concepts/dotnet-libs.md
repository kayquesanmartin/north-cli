# Catálogo de bibliotecas & ferramentas — .NET / C#

Mapa lib/ferramenta → categoria → dificuldade (jr/pl/sr) usado pelos **insights
passivos** do north para ensinar não só linguagem, mas as **bibliotecas, frameworks e
ferramentas** que aparecem no código (`using`, `<PackageReference>`, `dotnet add package`).
A IA casa o que usou contra esta tabela; libs fora dela recebem dificuldade julgada pela
IA (default `pl`). Namespace do ledger: **`dotnet-libs`**.

`Aliases` ajuda o casamento (símbolos/sinônimos/pacote), separados por vírgula.

| Conceito | Categoria | Dificuldade | Aliases |
|---|---|---|---|
| MediatR | mediator / CQRS | pl | mediator, IRequest, IRequestHandler, INotification, pipeline behavior, FreeMediator |
| FluentValidation | validação | pl | AbstractValidator, RuleFor, validator |
| EF Core | ORM / dados | sr | Entity Framework, DbContext, migration, LINQ-to-Entities, Include |
| Dapper | micro-ORM | pl | dapper, QueryAsync, micro-orm |
| Npgsql | driver de banco | pl | postgres driver, NpgsqlConnection, npgsql |
| AutoMapper | mapeamento de objetos | pl | mapper, CreateMap, ProjectTo |
| Polly | resiliência | sr | retry, circuit breaker, policy, resilience pipeline |
| MassTransit | mensageria | sr | bus, consumer, saga, RabbitMQ, message broker |
| NATS | mensageria | sr | nats, jetstream, pub/sub, message bus |
| Serilog | logging estruturado | pl | structured logging, sink, ILogger, Seq |
| Swashbuckle / Swagger | documentação de API | jr | swagger, openapi, swashbuckle, swaggergen |
| xUnit | framework de testes | jr | fact, theory, test framework |
| Moq | mock de testes | pl | mock, Setup, Verify, It.IsAny |
| FluentAssertions | asserções de teste | jr | Should(), BeEquivalentTo, assertions |
| Testcontainers | testes de integração | sr | testcontainer, container de teste, docker test |
| Gotenberg | geração de PDF | pl | html to pdf, gotenberg, pdf api, chromium pdf |
| QuestPDF | geração de PDF | pl | pdf, document, fluent pdf, questpdf |
| PuppeteerSharp | automação / PDF headless | sr | headless chrome, chromium, puppeteer, puppeteer-sharp |
| Hangfire | jobs em background | pl | background job, recurring job, scheduler, fire-and-forget |
| Microsoft.Identity.Web | auth / OIDC | sr | OIDC, Azure AD, Entra, JWT bearer, identity.web |
| AspNetCoreRateLimit | rate limiting | pl | rate limit, throttling, IpRateLimit |
| YARP | reverse proxy / gateway | sr | gateway, reverse proxy, yarp |
| Refit | cliente HTTP tipado | pl | typed http client, rest client, refit |
| Scrutor | DI / assembly scanning | sr | decorate, assembly scanning, DI registration |
| HttpClientFactory | cliente HTTP | pl | IHttpClientFactory, named client, typed client, DelegatingHandler |
