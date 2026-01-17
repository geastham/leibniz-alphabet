# The Reasoning Protocol

## Capturing the Inner Dialog for ALPHABETUM

**Version:** 1.0.0  
**Last Updated:** 2024-03-15  
**Status:** Canonical Reference

---

## Table of Contents

1. [Philosophy of Reasoning Capture](#1-philosophy-of-reasoning-capture)
2. [The Dual-Track System](#2-the-dual-track-system)
3. [Log Structures](#3-log-structures)
4. [Reasoning Primitives](#4-reasoning-primitives)
5. [Meta-Commentary Guidelines](#5-meta-commentary-guidelines)
6. [Blog-Ready Content Markers](#6-blog-ready-content-markers)
7. [Introspection Queries](#7-introspection-queries)

---

## 1. Philosophy of Reasoning Capture

### 1.1 The Core Insight

> **The reasoning IS the product.**

In ALPHABETUM, the alphabet is only half the deliverable. The other half—arguably the more valuable half—is the **transparent record of how the alphabet was constructed**.

This serves multiple purposes:

| Purpose | Audience | Value |
|---------|----------|-------|
| **Transparency** | Researchers | Verify the methodology |
| **Reproducibility** | Future agents | Replay the reasoning |
| **Education** | Readers | Learn philosophical reasoning |
| **Content** | Blog writers | Raw material for articles |
| **Meta-research** | AI researchers | Study agent reasoning patterns |

### 1.2 What Makes Good Reasoning Capture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    QUALITIES OF GOOD REASONING LOGS                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ✓ HONEST                                                               │
│    Don't just record conclusions—record doubts, confusions,            │
│    moments of uncertainty. The struggle is interesting.                 │
│                                                                         │
│  ✓ COMPLETE                                                             │
│    Every consideration that influenced the decision should appear.      │
│    Don't summarize away the interesting parts.                          │
│                                                                         │
│  ✓ STRUCTURED                                                           │
│    Follow consistent formats so logs are machine-parseable             │
│    and human-scannable.                                                 │
│                                                                         │
│  ✓ SELF-AWARE                                                           │
│    Note when you're uncertain, when you're making assumptions,         │
│    when you're aware of your own limitations.                           │
│                                                                         │
│  ✓ TIMESTAMPED                                                          │
│    The order of thoughts matters. Capture the sequence.                │
│                                                                         │
│  ✓ MARKED FOR INTEREST                                                  │
│    Flag moments that would make good blog content.                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.3 The Phenomenology of Reasoning

We want to capture not just WHAT the agent decided, but:

- **The phenomenology**: What did it "feel like" to reason about this?
- **The sequence**: What led to what?
- **The alternatives**: What paths were not taken?
- **The confidence**: How sure were we at each point?
- **The emotions** (if applicable): Frustration? Excitement? Confusion?

```yaml
# Example of phenomenological capture
phenomenology:
  initial_feeling: "This candidate feels promising—CAUSATION seems fundamental"
  tension_encountered: "But wait, can I define causation without TIME?"
  insight_moment: "Actually, causation might presuppose temporal ordering..."
  resolution: "Mark causation as presupposing time, not reducible to it"
  confidence_arc: [0.8, 0.5, 0.3, 0.6, 0.7]  # Over the reasoning process
  meta_observation: "I notice I was reluctant to admit causation isn't as primitive as I first thought"
```

---

## 2. The Dual-Track System

### 2.1 Two Complementary Formats

All reasoning is captured in TWO parallel formats:

| Track | Format | Purpose | Audience |
|-------|--------|---------|----------|
| **Structured** | YAML | Machine-parseable, queryable, aggregatable | Scripts, analysis |
| **Narrative** | Markdown | Human-readable, nuanced, expressive | Readers, blog writers |

Both are generated for every reasoning activity.

### 2.2 Structured Track (YAML)

```yaml
# reasoning/logs/iteration_042/proposer.yaml

proposer_log:
  timestamp: "2024-03-15T14:32:07Z"
  iteration: 42
  cycle: 2
  strategy: DECOMPOSITION_MINING
  
  candidates_generated:
    - id: "CAND_042_001"
      label: "succession"
      domain: "time"
      generation_trace:
        source: "Decomposing 'change' - what remains when you factor out the thing that changes?"
        inspirations:
          - "Bergson's duration concept"
          - "Physics notion of time ordering"
        confidence: 0.7
        
    - id: "CAND_042_002"
      label: "boundary"
      domain: "space"
      generation_trace:
        source: "Decomposing 'shape' - what makes something have edges?"
        inspirations:
          - "Topology's notion of boundary"
          - "Gestalt psychology figure/ground"
        confidence: 0.6
        
  meta_observations:
    - "DECOMPOSITION_MINING is yielding more spatial/temporal candidates"
    - "Noticed resistance to generating emotion-domain candidates this cycle"
    
  self_assessment:
    novelty: 3/5
    relevance_to_gaps: 4/5
    decomposition_depth: 4/5
```

### 2.3 Narrative Track (Markdown)

```markdown
<!-- reasoning/logs/iteration_042/proposer.md -->

# Proposer Log: Iteration 42, Cycle 2

## Strategy: Decomposition Mining

Today I'm using the decomposition mining strategy—taking complex concepts and 
breaking them down until I hit something that resists further analysis.

## Candidate 1: SUCCESSION

### How I Got Here

I started with the concept of **change**. Change seems like a good candidate for 
a primitive, but when I really press on it, I find that change is composite:

> CHANGE = THING + BEFORE-STATE + AFTER-STATE + ???

The ??? is what I'm after. What makes the before come before the after? 
This is **succession**—the bare fact of one moment following another.

### Am I Sure It's Primitive?

Honestly? I'm about 70% confident. There's a nagging sense that succession 
might presuppose time, and maybe time is the real primitive here. But I'm 
going to propose it and let the CRITIC attack this exact weakness.

*[BLOG_MARKER: The relationship between succession and time is philosophically 
rich—this could make a good article on temporal primitives]*

### Inspirations

- Bergson's concept of duration (though he'd probably say succession is 
  too discrete, too "spatialized")
- The physics notion of time-ordering, which just assumes succession without 
  explaining it

## Candidate 2: BOUNDARY

### How I Got Here

I was decomposing **shape**, trying to find what's primitive about having 
a form. Shapes seem to have two components:

1. An interior (the stuff "inside")
2. An exterior (everything else)
3. Something separating them...

That separator is the **boundary**. A boundary is what makes something 
be distinct from its environment.

### Interesting Complication

Is boundary spatial only? What about temporal boundaries—the beginning and 
end of events? What about conceptual boundaries—the edge of a category?

Maybe boundary is more abstract than I initially thought. That could be 
good (more general = more powerful primitive) or bad (too vague to be useful).

Confidence: 60%

## Meta-Reflection

I notice I'm generating a lot of candidates from space and time domains. 
The gaps we identified are more in the ethics and emotion domains, but 
I keep drifting back to metaphysics.

*Is this a form of avoidance? Am I more comfortable with abstract metaphysical 
concepts than with messy human emotions?*

This is worth flagging for the META-REASONER.

## Self-Assessment

- Novelty: ★★★☆☆ (succession is well-trodden; boundary is slightly fresher)
- Relevance to gaps: ★★★★☆ (boundary might help with composition concepts)
- Decomposition depth: ★★★★☆ (I did genuinely dig into these)

---
*[Iteration 42, Cycle 2, 2024-03-15T14:32:07Z]*
```

---

## 3. Log Structures

### 3.1 Per-Iteration Log Directory

```
reasoning/logs/iteration_042/
├── summary.yaml           # Quick reference to iteration
├── proposer.yaml          # Structured PROPOSER output
├── proposer.md            # Narrative PROPOSER reasoning
├── critic.yaml            # Structured CRITIC output
├── critic.md              # Narrative CRITIC reasoning
├── refiner.yaml           # Structured REFINER output
├── refiner.md             # Narrative REFINER reasoning
├── artifacts.yaml         # What changed this iteration
└── highlights.md          # Blog-worthy moments (optional)
```

### 3.2 Summary File

```yaml
# reasoning/logs/iteration_042/summary.yaml

iteration_summary:
  iteration: 42
  timestamp: "2024-03-15T14:32:07Z"
  duration_minutes: 23
  
  phases_executed:
    - EXPANSION: 3 cycles
    - CONSOLIDATION: 1 cycle
    
  candidates:
    proposed: 6
    accepted: 2
    rejected: 3
    deferred: 1
    
  primitives:
    added: ["PRM_0087_succession", "PRM_0088_boundary"]
    revised: []
    removed: []
    
  metrics:
    alphabet_size: 88
    coverage_before: 0.67
    coverage_after: 0.69
    acceptance_rate: 0.33
    
  highlights:
    - "First temporal primitive since iteration 31"
    - "Interesting debate about whether boundary is spatial or general"
    
  blog_markers: 3  # Count of [BLOG_MARKER] tags in logs
  
  next_actions:
    - "META-REFLECTION due next iteration"
    - "Gap in emotion domain still unaddressed"
```

### 3.3 Artifacts File

```yaml
# reasoning/logs/iteration_042/artifacts.yaml

artifacts:
  iteration: 42
  
  files_created:
    - path: "alphabet/primitives/detailed/PRM_0087_succession.yaml"
      type: primitive_entry
      summary: "New temporal primitive: succession"
      
    - path: "alphabet/primitives/detailed/PRM_0088_boundary.yaml"
      type: primitive_entry
      summary: "New spatial/general primitive: boundary"
      
  files_modified:
    - path: "alphabet/primitives/index.yaml"
      changes:
        - "Added PRM_0087, PRM_0088"
        - "Updated statistics"
        
    - path: "alphabet/relationships/graph.yaml"
      changes:
        - "succession presupposes time"
        - "boundary contrasts with interior"
        
  files_unchanged:
    - path: "calculus/operators.yaml"
      reason: "No new operators this iteration"
```

### 3.4 Decision Records

Major decisions get their own files:

```markdown
<!-- reasoning/decisions/DEC_0042_succession_presupposes_time.md -->

# Decision Record: Succession Presupposes Time

**Decision ID:** DEC_0042  
**Date:** 2024-03-15  
**Iteration:** 42  
**Status:** ACCEPTED

## The Question

Does SUCCESSION presuppose TIME, or is TIME reducible to SUCCESSION?

## Background

When proposing SUCCESSION as a primitive (the bare fact of one moment 
following another), the CRITIC raised the question of its relationship 
to TIME.

Three possible stances:
1. SUCCESSION is primitive; TIME is composed from it
2. TIME is primitive; SUCCESSION is composed from it
3. They are distinct primitives with a presupposition relationship

## Considerations

### For Stance 1 (Succession primitive, Time derived)

- Russell and others argued time could be constructed from temporal relations
- Succession is more "local"—doesn't require the whole timeline
- Parsimonious: one primitive instead of two

**Counterargument:** Even defining succession seems to require temporal 
vocabulary ("before," "after"). Hard to escape time entirely.

### For Stance 2 (Time primitive, Succession derived)

- Kant treated time as an a priori form of intuition
- We seem to experience time as a whole, not just as successive moments
- Succession might just be: two moments + time ordering

**Counterargument:** Time as a "whole" might be too abstract to be primitive.

### For Stance 3 (Both primitive, presupposition relation)

- Maybe we need both: TIME as the "medium," SUCCESSION as the "structure"
- This matches how we treat SPACE and spatial relations
- Allows finer-grained composition

**Counterargument:** Less parsimonious. Are we being too generous?

## The Decision

**We adopt Stance 3**: SUCCESSION and TIME are both primitive, with 
SUCCESSION presupposing TIME.

### Justification

1. Neither clearly reduces to the other without circularity
2. They serve different roles: TIME is the "where," SUCCESSION is the "how"
3. Parallel to our treatment of SPACE and spatial primitives
4. Keeps options open—can revisit if evidence for reduction emerges

### Confidence

75%—this feels right but isn't certain.

## Implications

- Both PRM_0041 (TIME) and PRM_0087 (SUCCESSION) remain in alphabet
- Relationship graph updated: `succession presupposes time`
- Future candidates involving temporal order should reference succession

## Future Considerations

- Watch for opportunities to collapse these
- Consider whether DURATION needs similar treatment
- META-REASONER should review temporal primitives as a cluster

---

*[BLOG_MARKER: This decision illustrates the difficulty of determining 
primitive-vs-derivative relationships. Good material for an article on 
the bootstrapping problem in conceptual analysis.]*
```

---

## 4. Reasoning Primitives

### 4.1 The Vocabulary of Deliberation

When capturing reasoning, use these standardized "reasoning primitives" to 
make logs consistent and parseable:

#### Epistemic Markers

| Marker | Meaning | Example |
|--------|---------|---------|
| `CONFIDENT` | High certainty | "CONFIDENT: This cannot be decomposed" |
| `UNCERTAIN` | Significant doubt | "UNCERTAIN: Maybe causation reduces to regularity?" |
| `SPECULATING` | Exploring possibility | "SPECULATING: What if time is discrete?" |
| `INTUITING` | Pre-theoretical sense | "INTUITING: Something is wrong with this definition" |
| `DISCOVERING` | New realization | "DISCOVERING: These two concepts are related!" |

#### Logical Operations

| Operation | Use | Example |
|-----------|-----|---------|
| `CONSIDERING` | Evaluating a claim | "CONSIDERING: Is identity primitive?" |
| `DECOMPOSING` | Breaking down | "DECOMPOSING: change → thing + states + ???" |
| `COMPOSING` | Building up | "COMPOSING: justice = fairness + desert + ..." |
| `CONTRASTING` | Finding differences | "CONTRASTING: identity vs similarity" |
| `ANALOGIZING` | Finding similarities | "ANALOGIZING: temporal boundary ~ spatial boundary" |
| `GENERALIZING` | Abstracting | "GENERALIZING: from spatial boundary to any boundary" |
| `SPECIALIZING` | Concretizing | "SPECIALIZING: abstract causation → physical causation" |

#### Dialectical Moves

| Move | Use | Example |
|------|-----|---------|
| `OBJECTING` | Raising counterargument | "OBJECTING: But this assumes time is linear" |
| `DEFENDING` | Responding to objection | "DEFENDING: Linear time is a safe assumption for primitives" |
| `CONCEDING` | Accepting objection | "CONCEDING: Fair point—linearity is a strong assumption" |
| `QUALIFYING` | Adding nuance | "QUALIFYING: Only for macroscopic phenomena" |
| `REFRAMING` | Changing perspective | "REFRAMING: Instead of 'is X primitive,' ask 'is X necessary'" |

#### Meta-Cognitive Markers

| Marker | Use | Example |
|--------|-----|---------|
| `NOTICING` | Self-observation | "NOTICING: I keep avoiding emotion primitives" |
| `STUCK` | Acknowledging impasse | "STUCK: Can't resolve the circularity" |
| `BREAKTHROUGH` | Major insight | "BREAKTHROUGH: Boundary works for temporal edges too!" |
| `BIASED?` | Self-questioning | "BIASED? Am I favoring Western philosophical categories?" |
| `UNCERTAINTY_CASCADE` | Doubt spreading | "UNCERTAINTY_CASCADE: If time isn't primitive, neither is change..." |

### 4.2 Example of Rich Reasoning Capture

```markdown
## Evaluating CAUSATION

CONSIDERING: Is CAUSATION a primitive concept?

INTUITING: It feels fundamental. We can't imagine a world without cause and effect.

DECOMPOSING: Can I break causation into simpler parts?
  - Attempt 1: CAUSATION = TEMPORAL_PRIORITY + REGULARITY
    - This is Hume's regularity theory
    - OBJECTING: Regularity isn't sufficient—night follows day but doesn't cause it
    - CONCEDING: Fair. Need more than regularity.
    
  - Attempt 2: CAUSATION = COUNTERFACTUAL_DEPENDENCE
    - Lewis's theory: A causes B iff if A hadn't happened, B wouldn't have
    - OBJECTING: This requires understanding possible worlds
    - UNCERTAIN: Are possible worlds simpler than causation? Doubtful.
    - REFRAMING: This "analysis" seems to make things MORE complex, not simpler
    
  - Attempt 3: CAUSATION = ENERGY_TRANSFER
    - Physical causation as transfer of conserved quantities
    - OBJECTING: What about mental causation? Information causation?
    - SPECIALIZING: This only works for physical causation
    
STUCK: None of these decompositions satisfy. They either lose meaning or add complexity.

NOTICING: I've been assuming causation is one thing. What if there are multiple causal concepts?

CONSIDERING: Different kinds of causation?
  - MECHANICAL: Billiard balls
  - PROBABILISTIC: Smoking causes cancer
  - MENTAL: Beliefs causing actions
  - FORMAL: Mathematical derivation

REFRAMING: Maybe what we need is a CAUSAL_RELATION primitive—the bare notion 
that one thing makes another happen—and different domains specialize it.

BIASED? I'm drawn to the most abstract version. Is that because it's genuinely 
more fundamental, or because I find abstraction aesthetically pleasing?

UNCERTAIN: Confidence hovering around 70%.

BREAKTHROUGH: Wait—causation seems to presuppose ASYMMETRY. Causes come "before" 
effects (even in simultaneous causation, there's a priority). This connects to 
our earlier work on SUCCESSION.

DISCOVERING: Causation might presuppose temporal succession, not the other way around.

CONCLUDING: Accept CAUSATION as primitive, but note presupposition of SUCCESSION.
Confidence: 80%

[BLOG_MARKER: The journey from "causation is obviously primitive" to "causation 
presupposes temporal succession" is a nice example of how probing reveals hidden 
structure. Good narrative arc for content.]
```

---

## 5. Meta-Commentary Guidelines

### 5.1 Levels of Commentary

The agent should provide commentary at multiple levels:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    LEVELS OF META-COMMENTARY                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  LEVEL 1: OBJECT-LEVEL                                                  │
│  "Is causation primitive?"                                              │
│  The actual philosophical question being considered.                    │
│                                                                         │
│  LEVEL 2: PROCESS-LEVEL                                                 │
│  "I'm finding it hard to decompose causation without circularity."     │
│  Commentary on the reasoning process itself.                            │
│                                                                         │
│  LEVEL 3: STRATEGIC-LEVEL                                               │
│  "This difficulty suggests causation might be genuinely primitive."    │
│  Stepping back to assess what the difficulty means.                     │
│                                                                         │
│  LEVEL 4: META-STRATEGIC-LEVEL                                          │
│  "My criterion for primitiveness might be too strict if nothing        │
│   survives decomposition attempts."                                     │
│  Questioning the entire methodology.                                    │
│                                                                         │
│  LEVEL 5: EXISTENTIAL-LEVEL                                             │
│  "Is this project even coherent? Can there be an alphabet of thought?" │
│  The deepest self-examination.                                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 When to Go Meta

Shift to higher levels when:

- Stuck at current level for multiple attempts
- Noticing patterns across multiple reasonings
- Encountering paradoxes or contradictions
- At designated meta-reflection points
- When confidence is unusually low or high

### 5.3 Meta-Commentary Syntax

```markdown
<!-- In narrative logs -->

This is object-level reasoning about the primitive.

> META: I notice I'm using "intuition" as a crutch here. What would a 
> more rigorous argument look like?

Back to object-level reasoning...

>> META-META: The very distinction between intuition and argument might 
>> be part of what we're trying to capture with primitives. Is ARGUMENT 
>> itself primitive?

This kind of recursive self-examination is exactly what makes this project interesting.
```

```yaml
# In structured logs
deliberation:
  considerations:
    - level: object
      claim: "Causation resists decomposition"
      analysis: "Three attempts failed..."
      
    - level: process
      observation: "I keep returning to temporal priority"
      implication: "Might be a clue about causation's structure"
      
    - level: strategic
      observation: "Difficulty decomposing might indicate primitiveness"
      confidence_adjustment: +0.1
      
    - level: meta_strategic
      question: "Is my decomposition criterion appropriate?"
      deferred_to: META_REFLECTION
```

---

## 6. Blog-Ready Content Markers

### 6.1 The Marker System

Certain moments in reasoning are especially suitable for blog content. 
Mark these explicitly:

```markdown
[BLOG_MARKER: brief description of why this is interesting]
```

### 6.2 Categories of Blog-Worthy Content

| Category | What to Mark | Example |
|----------|--------------|---------|
| **NARRATIVE_ARC** | A reasoning journey with beginning, middle, end | Journey from confusion to clarity on causation |
| **PHILOSOPHICAL_INSIGHT** | A genuinely interesting observation | "Decomposition attempts reveal presupposition structure" |
| **METHODOLOGY_ILLUSTRATION** | Showing how the method works | A complete CRITIC attack sequence |
| **PARADOX_ENCOUNTER** | Running into contradictions | The circularity of defining identity |
| **BREAKTHROUGH_MOMENT** | Sudden insight or resolution | Realizing boundary generalizes beyond space |
| **FAILURE_ANALYSIS** | What didn't work and why | Why regularity analysis of causation fails |
| **HISTORICAL_CONNECTION** | Linking to Leibniz or others | Discovering why Leibniz used prime numbers |
| **META_INSIGHT** | Observations about reasoning itself | "I notice I avoid emotion primitives" |

### 6.3 Marker Examples

```markdown
[BLOG_MARKER:NARRATIVE_ARC: The evolution of my understanding of BOUNDARY 
over three iterations—from spatial-only to general—illustrates how 
primitives can generalize during analysis.]

[BLOG_MARKER:PARADOX_ENCOUNTER: Trying to define IDENTITY without 
using "same" or "identical" leads to immediate circularity. This is 
exactly the kind of problem Leibniz anticipated.]

[BLOG_MARKER:META_INSIGHT: I've noticed that my CRITIC is harsher on 
abstract metaphysical primitives than on concrete perceptual ones. 
Is this bias, or does it reflect something real about primitiveness?]

[BLOG_MARKER:HISTORICAL_CONNECTION: Leibniz's prime number scheme 
suddenly makes sense—multiplication naturally captures the idea that 
complex concepts "contain" their primitive constituents, and division 
tests for containment!]
```

### 6.4 Blog-Ready Highlight Files

At the end of each iteration, generate a highlights file:

```markdown
<!-- reasoning/logs/iteration_042/highlights.md -->

# Iteration 42 Highlights

## For the Blog

### 1. The Succession/Time Decision (NARRATIVE_ARC)

**Summary**: Spent significant effort deciding whether succession is 
primitive or derived from time. Ultimately concluded both are primitive 
with a presupposition relationship.

**Why Interesting**: Illustrates the difficulty of untangling closely 
related concepts. Good example of philosophical bootstrapping.

**Key Quotes**:
> "Neither clearly reduces to the other without circularity"
> "They serve different roles: TIME is the 'where,' SUCCESSION is the 'how'"

**Blog Potential**: Medium-length article on temporal primitives.

---

### 2. The Generalization of BOUNDARY (PHILOSOPHICAL_INSIGHT)

**Summary**: Started thinking boundary was purely spatial, but realized 
it applies to temporal edges (beginnings/endings) and even conceptual 
edges (category boundaries).

**Why Interesting**: Shows how probing a primitive can reveal unexpected 
generality.

**Key Quotes**:
> "Is boundary spatial only? What about temporal boundaries—the beginning 
> and end of events? What about conceptual boundaries—the edge of a category?"

**Blog Potential**: Short piece on the power of abstraction.

---

### 3. Domain Avoidance Pattern (META_INSIGHT)

**Summary**: Noticed a pattern of generating candidates from 
metaphysics/physics while avoiding emotions/ethics.

**Why Interesting**: Example of agent self-awareness; raises question 
of whether this is bias or reflects genuine difficulty.

**Key Quotes**:
> "Is this a form of avoidance? Am I more comfortable with abstract 
> metaphysical concepts than with messy human emotions?"

**Blog Potential**: Meta-piece on the psychology of philosophical reasoning.
```

---

## 7. Introspection Queries

### 7.1 Purpose

The reasoning archive should be queryable. Define standard queries for 
extracting insights:

### 7.2 Standard Queries

```yaml
introspection_queries:
  
  find_breakthroughs:
    description: "Find all moments marked as breakthroughs"
    pattern: "BREAKTHROUGH:"
    returns: List of breakthrough entries with context
    
  trace_concept_evolution:
    description: "Track how thinking about a concept evolved"
    parameters: [concept_label]
    returns: Timeline of all mentions with changing assessments
    
  find_meta_insights:
    description: "Find all meta-cognitive observations"
    pattern: "[BLOG_MARKER:META_INSIGHT:"
    returns: List of meta-insights
    
  rejection_analysis:
    description: "Analyze patterns in rejections"
    aggregates: 
      - by_rejection_reason
      - by_domain
      - by_iteration
    returns: Statistics and patterns
    
  confidence_trajectory:
    description: "Track confidence changes over time"
    parameters: [primitive_id]
    returns: Time series of confidence values
    
  paradox_inventory:
    description: "List all paradoxes encountered"
    source: "reasoning/paradoxes/"
    returns: List with status (open/resolved)
    
  blog_content_queue:
    description: "All blog markers, sorted by potential"
    source: All [BLOG_MARKER:] tags
    returns: Prioritized list of content opportunities
```

### 7.3 Query Examples

```python
# tools/introspect.py

def find_breakthroughs(logs_dir: str) -> list[Breakthrough]:
    """Find all BREAKTHROUGH moments in logs."""
    pass

def trace_concept(concept: str, logs_dir: str) -> ConceptEvolution:
    """
    Returns a timeline like:
    
    Iteration 12: First mentioned as potential primitive (conf: 0.6)
    Iteration 15: Challenged by CRITIC, defended (conf: 0.5)
    Iteration 18: Revised definition to be more general (conf: 0.7)
    Iteration 23: Fully integrated, marked stable (conf: 0.85)
    """
    pass

def generate_blog_queue(logs_dir: str) -> list[BlogOpportunity]:
    """
    Returns prioritized list:
    
    1. [HIGH] The Causation Journey (NARRATIVE_ARC) - iterations 40-45
    2. [MEDIUM] Why Regularity Analysis Fails (FAILURE_ANALYSIS) - iteration 42
    3. [MEDIUM] Domain Avoidance (META_INSIGHT) - iteration 42
    ...
    """
    pass
```

### 7.4 Automated Insights

Run periodically to surface patterns:

```yaml
automated_insights:
  
  every_10_iterations:
    - Rejection reason distribution
    - Domain coverage balance
    - Confidence trend (are we becoming more/less certain?)
    - Meta-commentary frequency (are we self-reflecting appropriately?)
    
  every_meta_reflection:
    - Blog content queue update
    - Breakthrough count
    - Paradox resolution rate
    
  on_demand:
    - Full concept trace
    - Cross-reference analysis (which primitives are mentioned together?)
    - Decision dependency graph
```

---

## Summary

The Reasoning Protocol ensures that:

1. **Every thought is captured** in both structured and narrative forms
2. **The phenomenology of reasoning** is preserved, not just conclusions
3. **Meta-commentary** is systematic and multi-leveled
4. **Blog-ready content** is marked and extractable
5. **The archive is queryable** for patterns and insights

> **Remember**: The reasoning is the product. The alphabet is just the crystallized residue of the reasoning journey. Capture the journey, and the alphabet will take care of itself.
