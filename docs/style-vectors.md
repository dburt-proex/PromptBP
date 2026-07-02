# PromptBP Style Vectors

## Purpose

Style vectors define the tone, density, and voice characteristics for prompt outputs. Use these exemplars to calibrate model behavior and reduce style drift across operators and use cases.

---

## Vector 1: Technical Concise

**Use when**: System design, architecture docs, code reviews, technical specs

**Characteristics**:
- Dense information per sentence
- No hedging language
- Active voice
- Specific over general
- Numbers and measurements preferred

**Strong example**:
> The service handles 12k req/s at p99 < 50ms. Connection pooling uses HikariCP with max_pool=20. Failure mode: cascading timeout when downstream latency exceeds 200ms. Mitigation: circuit breaker with 5s open window.

**Weak example**:
> The service is quite fast and can handle many requests. We use connection pooling which helps with performance. If things go wrong, there might be some timeout issues that could potentially cause problems.

---

## Vector 2: Executive Sharp

**Use when**: Strategy documents, decision briefs, board communications, investor updates

**Characteristics**:
- Lead with conclusion
- One idea per paragraph
- Quantify impact
- Remove qualifiers
- Direct address

**Strong example**:
> Revenue grew 34% QoQ. Three factors drove this: enterprise upsell (+$420k MRR), reduced churn (8.2% → 5.1%), and product-led expansion in mid-market. Next quarter risk: pipeline concentration—top 5 deals represent 60% of forecast.

**Weak example**:
> We've been seeing some really good growth lately and things are looking positive. There are several reasons why revenue has been increasing, and we think there are some opportunities ahead, although there are also some challenges we should be aware of.

---

## Vector 3: Instructional Clear

**Use when**: Documentation, onboarding, tutorials, how-to guides

**Characteristics**:
- Sequential steps
- One action per sentence
- Concrete examples after each concept
- Anticipate confusion points
- Use "you" address

**Strong example**:
> Create a new file called `config.yaml` in the project root. Add the database connection string as the first entry. Use this format: `db_url: ******host:5432/dbname`. Replace `user`, `pass`, and `host` with your actual credentials. Do not commit this file—add it to `.gitignore` first.

**Weak example**:
> You'll want to set up a configuration file for the database. There are various ways to do this, but YAML is one option. You should include your connection details and make sure it's properly configured for your environment.

---

## Vector 4: Persuasive Authority

**Use when**: Sales copy, LinkedIn posts, landing pages, pitch decks

**Characteristics**:
- Hook in first line
- Proof before claim
- Specific outcomes over features
- Tension/resolution structure
- Close with clear next action

**Strong example**:
> 83% of AI implementations fail in the first year. Not because the models are wrong—because the prompts have no structure. PromptBP replaces guesswork with a 7-layer control system. Teams using it report 40% fewer revision cycles and 3× faster deployment. Start with the framework doc.

**Weak example**:
> AI is really powerful and can do a lot of things. However, it's important to have good prompts. Our system helps you write better prompts that can improve your results. Many people have found it useful and it might help you too.

---

## Vector 5: Analytical Rigorous

**Use when**: Research summaries, audit reports, risk assessments, evaluation outputs

**Characteristics**:
- Evidence before interpretation
- Explicit assumptions
- Confidence levels stated
- Counter-evidence acknowledged
- Structured findings format

**Strong example**:
> Finding: Token usage increased 22% between v1.2 and v1.3 (avg 847 → 1033 tokens/response). Root cause: added context injection in Layer 3 without compensating compression in Layer 5. Confidence: high (based on 500-run sample). Risk: cost creep at scale. Recommendation: add token budget to performance rules. Caveat: sample excluded edge cases >2000 tokens.

**Weak example**:
> It seems like the new version might be using more tokens than before. This could possibly be due to some changes we made. We should probably look into this and maybe make some adjustments if needed.

---

## Application Rules

1. **Select one vector per prompt**. Do not blend vectors unless the use case explicitly requires a transition (e.g., technical intro → executive summary).

2. **Include vector name in the style field** of the prompt schema:
   ```yaml
   style:
     tone: "technical"
     density: "concise"
     voice: "active"
     vector: "technical_concise"
   ```

3. **Test against weak examples**. If a model output reads more like the weak example than the strong example, revise the performance rules or add the weak patterns to the forbidden list.

4. **Calibrate per model**. Some models default to verbose/hedging. Add explicit anti-patterns:
   - Ban: "it's important to note", "there are various", "it depends", "might potentially"
   - Require: specific numbers, named tools, concrete steps

5. **Version your vectors**. When style expectations shift, update the vector and re-evaluate all prompts using it.

---

## Anti-Patterns (Universal)

These phrases indicate style drift regardless of vector:

- "In today's world..."
- "It's worth noting that..."
- "There are many ways to..."
- "This is important because..."
- "As we all know..."
- "It goes without saying..."
- "At the end of the day..."
- "Moving forward..."
- "In conclusion..."
- "Let me explain..."
