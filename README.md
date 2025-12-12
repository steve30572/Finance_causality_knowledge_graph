# Finance causality knowledge graph
This project aims to construct a **Finance Causality Knowledge Graph** by analyzing global events. Leveraging the **[GDELT (Global Database of Events, Language, and Tone)](https://www.gdeltproject.org/)** dataset, this system detects causal relationships between various events and structures them into knowledge graph triples (Subject, Predicate, Object).

The goal is to provide a structured representation of how global events influence financial dynamics through verified causal links.

## Step 1: Causality Identification
In this phase, we input sequential raw events into an LLM to identify plausible causal pairs. Unlike simple co-occurrence, we enforce strict logical constraints to ensure high-quality edges.

**Core Causal Verification Criteria:**
To determine if Event A caused Event B, the model applies the following three checks:

1.  **Strict Temporal Order ($t_{cause} < t_{effect}$)**
    * The Cause must historically precede the Effect.
    * Future events cannot influence past events; the system strictly respects timestamps.
2.  **Counterfactual Check (Logical Dependency)**
    * *Question:* "If the Cause had not occurred, would the Effect still have happened?"
    * If the answer is **"Yes"**, the pair is discarded as a mere correlation.
    * If **"No"**, it suggests a strong dependency.
3.  **Causal Mechanism**
    * There must be a direct functional link where the Cause *actively* leads to the Effect (e.g., triggers, forces, requires).
    * Vague thematic similarities are ignored.

---


## Step 2 Triple Generation (KG Construction)
Once causal pairs are validated, the system transforms the unstructured text and reasoning into structured Knowledge Graph Triples.

* **Subject:** The primary actor initiating the event (from the Cause).
* **Predicate:** cause
* **Object:** The affected entity or event (from the Effect).

This structured format allows for graph-based queries and multi-hop reasoning in downstream financial analysis.

---

## File structure

Finance_causality_knowledge_graph/
```
├── causal_knowledge_graph/                     
│   ├── prompts/
│   |    └── v7.txt                # Prompts for causality detection
|   └── data /                     # Data obtained by running LLM with prompt written in prompts/v7.txt
├── crawling/                      # Crawling code for GDELT Finance Events
├── causality_test/                # Demo for causality testing
└── README.md     
```
