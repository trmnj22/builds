#!/usr/bin/env python3
"""Pick the strongest technical evidence for a job ad.

Reads an evidence bank (a Markdown file of past technical work, one entry per `### TE-NNN` heading) and a
job ad (any text file), finds the technical terms the ad uses, and ranks bank entries by how many of those
terms they honestly support, weighted by evidence strength and recency. Prints, and with --out writes, a
pick list: the CV-ready line for each entry, the terms it covers, its evidence level and any open
question, plus a coverage table of every term the ad uses (supported or gap).

Usage:
  python3 pick.py examples/job_ad.md
  python3 pick.py examples/job_ad.md --top 8 --out pick_output.md
  python3 pick.py --terms "microservices, APIs, POS, Python"

Rules the picker enforces:
- entries with evidence `unsupported` are never picked. `conflict` and `cv-claim` entries are picked but
  flagged, so a person confirms them before they go into a CV.
- the CV line is the bank's own wording, never strengthened.
- a term no entry supports is reported as a gap, never papered over.
"""
import argparse, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, "examples", "evidence_bank.md")

# Canonical term -> phrases that count as that term, in a job ad or in a bank entry.
# Keep these honest: a synonym only belongs here if doing one is doing the other.
SYNONYMS = {
    "APIs": ["api", "apis", "rest", "restful", "odata", "soap", "web service", "web services", "endpoint", "retail server", "graphql", "aif", "custom service"],
    "microservices": ["microservice", "microservices", "commerce scale unit", "csu", "service-oriented", "soa", "distributed services"],
    "integration": ["integration", "integrations", "integrate", "integrated", "middleware", "edi", "logic apps", "service bus", "interface", "interfaces", "data exchange", "cdx"],
    "POS": ["pos", "point of sale", "point-of-sale", "mpos", "cpos", "epos", "store commerce", "modern pos", "cloud pos", "till"],
    "ecommerce": ["ecommerce", "e-commerce", "online store", "webstore", "web store", "b2b portal", "b2c", "d2c", "headless", "storefront", "digital commerce"],
    "headless commerce": ["headless"],
    "omnichannel retail": ["omnichannel", "omni-channel", "click and collect", "bopis", "store fulfilment", "loyalty"],
    "payments": ["payment", "payments", "payment connector", "adyen", "pci"],
    "D365 Commerce": ["dynamics 365 commerce", "d365 commerce", "dynamics 365 retail", "d365 retail", "commerce runtime", "crt", "retail sdk", "commerce sdk"],
    "D365 F&O / AX": ["dynamics 365 finance", "finance and operations", "f&o", "d365fo", "dynamics ax", "ax 2012", "ax 2009", "axapta", "dynamics 365 supply chain", "erp"],
    "SAP": ["sap"],
    "X++": ["x++"],
    "C# / .NET": ["c#", ".net", "dotnet", "asp.net"],
    "Python": ["python"],
    "SQL": ["sql", "t-sql", "stored procedure", "query", "queries"],
    "data pipelines / ETL": ["data pipeline", "data pipelines", "etl", "elt", "data migration", "data load", "dmf", "data entities", "data factory", "synapse", "fabric"],
    "data systems / warehouse": ["data warehouse", "data systems", "data model", "data modelling", "data modeling", "database", "data design", "lakehouse"],
    "reporting / BI": ["ssrs", "power bi", "reporting", "report", "dashboard", "analytics"],
    "cloud / Azure": ["azure", "cloud", "cloud infrastructure", "aws", "gcp"],
    "DevOps / CI-CD": ["devops", "ci/cd", "ci-cd", "continuous integration", "deployment pipeline", "lcs", "lifecycle services", "release", "build pipeline"],
    "performance": ["performance", "optimisation", "optimization", "tuning", "latency", "scalab"],
    "security / identity": ["security", "identity", "azure ad", "entra", "b2c", "sso", "privacy", "pci"],
    "testing / QA": ["testing", "test case", "test cases", "test automation", "qa", "uat", "regression"],
    "solution architecture": ["solution architecture", "architect", "architecture", "solution design", "technical design", "reference architecture"],
    "technical discovery": ["technical discovery", "discovery", "requirements", "workshop", "workshops", "fit-gap", "fit gap"],
    "agents / agentic AI": ["agent", "agents", "agentic", "copilot studio", "autonomous"],
    "LLM / generative AI": ["llm", "llms", "large language model", "generative ai", "genai", "gpt", "openai", "foundation model", "model integration", "prompt"],
    "evaluation": ["evaluation", "evals", "eval", "test set", "accuracy", "human-in-the-loop", "human in the loop"],
    "retrieval / search": ["retrieval", "rag", "search", "vector", "embedding", "ai search"],
    "pricing / rebates engines": ["pricing engine", "pricing", "rebate", "rebates", "trade promotion", "promotions"],
    "algorithms": ["algorithm", "algorithms", "optimisation model", "optimization model", "scheduling"],
    "mentoring engineers": ["mentor", "mentoring", "coach", "player-coach", "code review", "design review"],
    "prototype to production": ["prototype", "production", "go-live", "go live", "productionise", "productionize"],
}
# How much to trust each evidence level. Unknown levels get 0.5.
LEVEL_WEIGHT = {"reference": 1.0, "document": 1.0, "public-profile": 0.95, "self-confirmed": 0.95,
                "self-asserted": 0.8, "cv-claim": 0.7, "conflict": 0.4, "unsupported": 0.0}

def term_hits(text):
    t = " " + re.sub(r"\s+", " ", text.lower()) + " "
    hits = {}
    for term, phrases in SYNONYMS.items():
        n = 0
        for p in phrases:
            pat = r"(?<![a-z0-9])" + re.escape(p) + (r"" if p.endswith("scalab") else r"(?![a-z0-9])")
            n += len(re.findall(pat, t))
        if n:
            hits[term] = n
    return hits

def parse_bank(path):
    if not os.path.exists(path):
        sys.exit(f"FAILED: bank not found: {path}")
    entries, cur = [], None
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^### (TE-\d+)\s+(.*)$", line.strip())
        if m:
            cur = {"id": m.group(1), "title": m.group(2), "fields": {}}
            entries.append(cur); continue
        if cur is None:
            continue
        m = re.match(r"^- \*\*(\w[\w ]*):\*\*\s*(.*)$", line.strip())
        if m:
            cur["fields"][m.group(1).lower()] = m.group(2).strip()
    for e in entries:
        f = e["fields"]
        e["level"] = f.get("evidence", "cv-claim").split()[0].strip("`")
        e["year"] = max((int(y) for y in re.findall(r"(?:19|20)\d\d", f.get("when", ""))), default=2015)
        blob = " ".join([e["title"], f.get("tech", ""), f.get("keywords", ""), f.get("cv", ""), f.get("detail", "")])
        e["terms"] = set(term_hits(blob))
    return entries

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jd", nargs="?", help="job ad file (any text or Markdown)")
    ap.add_argument("--terms", help="comma-separated terms instead of a file")
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--out", help="write the pick list as a markdown note here")
    ap.add_argument("--bank", default=BANK)
    a = ap.parse_args()
    if a.terms:
        jd_text = a.terms
    elif a.jd:
        jd_text = open(a.jd, encoding="utf-8").read()
        # Score the posting only: anything after a "## Notes" heading is the reader's own notes.
        jd_text = re.split(r"\n## Notes", jd_text)[0]
    else:
        ap.error("give a JD file or --terms")
    jd = term_hits(jd_text)
    if not jd:
        sys.exit("No technical terms found in the job ad.")
    entries = [e for e in parse_bank(a.bank) if LEVEL_WEIGHT.get(e["level"], 0.5) > 0]
    for e in entries:
        covered = e["terms"] & set(jd)
        recency = 1.0 + max(0, e["year"] - 2011) / 30          # 2011 = 1.0, 2026 = 1.5
        e["covered"] = sorted(covered, key=lambda t: -jd[t])
        e["score"] = sum(1 + min(jd[t], 5) / 5 for t in covered) * LEVEL_WEIGHT.get(e["level"], 0.5) * recency
    picks = sorted([e for e in entries if e["covered"]], key=lambda e: -e["score"])[: a.top]

    support = {t: [e["id"] for e in entries if t in e["terms"]] for t in jd}
    lines = ["# Technical pick", "", f"Job ad terms (count): " + " · ".join(f"{t} ({n})" for t, n in sorted(jd.items(), key=lambda x: -x[1])), "",
             "## Ranked evidence", ""]
    for i, e in enumerate(picks, 1):
        f = e["fields"]
        flag = {"cv-claim": "  ⚠ from old CVs only: confirm any metric before outward use",
                "conflict": "  ⚠ conflict between sources: resolve the flag first",
                "self-asserted": "  (self-asserted: use the wording as given)"}.get(e["level"], "")
        lines += [f"{i}. **{e['id']} {e['title']}** ({f.get('employer', '')}, {f.get('when', '')}) score {e['score']:.1f}{flag}",
                  f"   - CV line: {f.get('cv', '')}",
                  f"   - Covers: {', '.join(e['covered'])}"]
        if f.get("ask"):
            lines.append(f"   - Open question: {f['ask']}")
    lines += ["", "## Coverage of the ad's terms", "", "| Term | In ad | Supported by |", "|---|---|---|"]
    for t, n in sorted(jd.items(), key=lambda x: -x[1]):
        ids = support[t]
        lines.append(f"| {t} | {n} | {', '.join(ids) if ids else '**gap: do not claim**'} |")
    out = "\n".join(lines) + "\n"
    print(out)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(out)
        print(f"written: {a.out}")

if __name__ == "__main__":
    main()
