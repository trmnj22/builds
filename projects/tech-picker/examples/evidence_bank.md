# Evidence bank: Alex Morgan (fictional sample)

Every person, company and project in this file is invented for the demo. One entry per `### TE-NNN` heading.
Fields the picker reads: Employer, When, Tech, Keywords, CV, Detail, Evidence, Ask.
Evidence levels: `reference`, `document`, `public-profile`, `self-confirmed`, `self-asserted`, `cv-claim`, `conflict`, `unsupported`.

### TE-001 Order API for the online store
- **Employer:** Northwind Retail Systems
- **When:** 2024
- **Tech:** C#, ASP.NET, REST, SQL
- **Keywords:** api, ecommerce, headless storefront
- **CV:** Part of the team that designed the REST order API behind a headless storefront for a regional garden supplies chain.
- **Detail:** Wrote the order and stock endpoints and the contract tests.
- **Evidence:** `document` (design document, sign-off email)

### TE-002 Click and collect for 40 stores
- **Employer:** Northwind Retail Systems
- **When:** 2023
- **Tech:** Azure Service Bus, C#
- **Keywords:** omnichannel, click and collect, integration, pos
- **CV:** Led the integration that let online orders be picked up in store, linking the web store to the point of sale in 40 stores.
- **Detail:** Message flow from web store to store tills through a service bus.
- **Evidence:** `reference` (letter from the former delivery manager)

### TE-003 Nightly sales data pipeline
- **Employer:** Northwind Retail Systems
- **When:** 2022
- **Tech:** Python, Azure Data Factory, SQL
- **Keywords:** etl, data warehouse, power bi
- **CV:** Built a nightly ETL pipeline in Python and Data Factory that loads store sales into the data warehouse for Power BI reporting.
- **Evidence:** `self-confirmed`

### TE-004 Returns assistant prototype
- **Employer:** Northwind Retail Systems
- **When:** 2025
- **Tech:** Python, LLM, retrieval
- **Keywords:** generative ai, rag, prompt, evaluation, prototype
- **CV:** Built a prototype returns assistant that answers policy questions with retrieval over the returns policy, measured against a 200-question test set.
- **Detail:** Did not reach production. Paused after the pilot.
- **Evidence:** `self-asserted`
- **Ask:** Was the test set accuracy written down anywhere?

### TE-005 Payment connector upgrade
- **Employer:** Contoso Consulting
- **When:** 2020
- **Tech:** C#, payment connector
- **Keywords:** payments, pci, pos, testing
- **CV:** Part of the team that upgraded the card payment connector for a national pharmacy group, including regression testing across store tills.
- **Evidence:** `public-profile`

### TE-006 Solution architecture for a wholesaler
- **Employer:** Contoso Consulting
- **When:** 2019
- **Tech:** ERP, integration
- **Keywords:** solution architecture, technical discovery, workshops, erp
- **CV:** Ran technical discovery workshops and wrote the solution design for an ERP rollout at a building supplies wholesaler.
- **Evidence:** `document` (solution design, version 1.0)

### TE-007 Pricing and promotions engine
- **Employer:** Contoso Consulting
- **When:** 2018
- **Tech:** SQL, C#
- **Keywords:** pricing engine, promotions, performance
- **CV:** Tuned the promotions pricing engine for a fashion retailer, cutting basket calculation time by 60%.
- **Evidence:** `cv-claim`
- **Ask:** The 60% figure comes from an old CV only. Is there a test report?

### TE-008 CI/CD for the commerce team
- **Employer:** Northwind Retail Systems
- **When:** 2021
- **Tech:** Azure DevOps, YAML pipelines
- **Keywords:** devops, ci/cd, build pipeline, release
- **CV:** Set up CI/CD pipelines in Azure DevOps that took the commerce team from monthly to weekly releases.
- **Evidence:** `conflict` (team wiki says fortnightly, CV says weekly)

### TE-009 Mentoring junior developers
- **Employer:** Northwind Retail Systems
- **When:** 2024
- **Tech:** code review
- **Keywords:** mentoring, code review, design review
- **CV:** Mentored four junior developers through weekly code and design reviews.
- **Evidence:** `reference`

### TE-010 Microservice split of the stock service
- **Employer:** Northwind Retail Systems
- **When:** 2025
- **Tech:** C#, .NET, Kubernetes
- **Keywords:** microservices, api, cloud, performance
- **CV:** Part of the team that split the stock lookup out of the monolith into a microservice on Azure.
- **Evidence:** `self-confirmed`

### TE-011 Mainframe rewrite claim
- **Employer:** Contoso Consulting
- **When:** 2016
- **Tech:** COBOL, SQL
- **Keywords:** data migration, sql
- **CV:** Rewrote the mainframe stock system.
- **Evidence:** `unsupported` (no source found, kept so it is never used)
