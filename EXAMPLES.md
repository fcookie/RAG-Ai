# RAG Document Assistant - Usage Examples

This document provides practical examples of using the RAG Document Assistant for various use cases.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Medical Research](#medical-research)
3. [Financial Analysis](#financial-analysis)
4. [Legal Documents](#legal-documents)
5. [Technical Documentation](#technical-documentation)
6. [Comparative Analysis](#comparative-analysis)
7. [Advanced Queries](#advanced-queries)

---

## Basic Usage

### Upload and Query

```python
from src import VectorStore, RAGChain, DocumentProcessor

# Initialize
vector_store = VectorStore()
rag_chain = RAGChain(vector_store)
processor = DocumentProcessor()

# Process document
docs = processor.process_pdf("research_paper.pdf")
vector_store.add_documents(docs)

# Query
response = rag_chain.query("What are the main findings?")
print(response.answer)
```

### Example Questions

**General Understanding:**
- "What is this document about?"
- "Summarize the key points"
- "Who are the authors?"

**Specific Information:**
- "What methodology was used?"
- "What are the limitations of the study?"
- "What are the main conclusions?"

---

## Medical Research

### Use Case: Analyzing Clinical Studies

**Upload:** Medical research papers, clinical trial reports

**Sample Questions:**

1. **Study Design:**
   ```
   Q: "What type of study design was used?"
   A: "This was a multi-center prospective study conducted across 150 
      healthcare facilities. [Source: sample_paper.pdf, Page: 3, Section: Methodology]"
   ```

2. **Patient Outcomes:**
   ```
   Q: "What were the improvements in patient outcomes?"
   A: "The study found several key improvements:
      - 15% reduction in hospital readmissions
      - 20% faster time to treatment
      - 8% improvement in survival rates for critical conditions
      [Source: sample_paper.pdf, Page: 5, Section: Results]"
   ```

3. **Adverse Events:**
   ```
   Q: "Were there any safety concerns or adverse events reported?"
   A: "The document reports significant improvements in safety:
      - 42% reduction in diagnostic errors
      - 55% reduction in medication errors
      [Source: sample_paper.pdf, Page: 6, Section: Error Reduction]"
   ```

4. **Comparison Questions:**
   ```
   Q: "How does AI-assisted diagnosis compare to traditional methods?"
   A: "AI-assisted diagnosis showed superior performance:
      - Accuracy: 94.2% vs 76.8% (traditional)
      - 23% overall improvement
      - 35% reduction in false negatives
      [Source: sample_paper.pdf, Page: 5]"
   ```

---

## Financial Analysis

### Use Case: Analyzing Company Reports

**Upload:** Annual reports (10-K), quarterly earnings (10-Q), investor presentations

**Sample Questions:**

1. **Revenue Analysis:**
   ```
   Q: "What was the company's total revenue in Q4?"
   A: [Extracts specific revenue figures with source citations]
   ```

2. **Year-over-Year Comparison:**
   ```
   Q: "How did revenue growth compare to the previous year?"
   A: [Provides comparative analysis with citations from both years]
   ```

3. **Risk Factors:**
   ```
   Q: "What are the main risk factors mentioned?"
   A: [Lists risk factors with page references]
   ```

4. **Management Discussion:**
   ```
   Q: "What does management say about future outlook?"
   A: [Summarizes MD&A section with citations]
   ```

### Document Comparison Example

```python
# Compare multiple quarterly reports
response = rag_chain.compare_documents(
    "Compare revenue growth across Q1, Q2, and Q3",
    doc_ids=['q1_report_id', 'q2_report_id', 'q3_report_id']
)
```

---

## Legal Documents

### Use Case: Contract Analysis

**Upload:** Contracts, agreements, legal documents

**Sample Questions:**

1. **Specific Clauses:**
   ```
   Q: "What are the termination conditions?"
   A: [Identifies and quotes termination clauses with section numbers]
   ```

2. **Obligations:**
   ```
   Q: "What are the vendor's obligations under this contract?"
   A: [Lists obligations with citations to specific sections]
   ```

3. **Liability:**
   ```
   Q: "What are the liability limitations?"
   A: [Explains liability caps and exclusions with references]
   ```

4. **Comparison:**
   ```
   Q: "Compare the payment terms in Contract A vs Contract B"
   A: [Provides side-by-side comparison with citations]
   ```

---

## Technical Documentation

### Use Case: API Documentation

**Upload:** API docs, technical specifications, user manuals

**Sample Questions:**

1. **How-To Questions:**
   ```
   Q: "How do I authenticate with the API?"
   A: [Provides authentication steps with code examples from docs]
   ```

2. **Configuration:**
   ```
   Q: "What configuration options are available?"
   A: [Lists configuration parameters with descriptions and defaults]
   ```

3. **Troubleshooting:**
   ```
   Q: "How do I fix error code 401?"
   A: [Explains error and provides solutions from documentation]
   ```

4. **Best Practices:**
   ```
   Q: "What are the recommended best practices for rate limiting?"
   A: [Summarizes best practices section with citations]
   ```

---

## Comparative Analysis

### Example: Comparing Research Studies

**Setup:**
```python
# Upload multiple research papers
papers = [
    "study_a_diabetes.pdf",
    "study_b_diabetes.pdf",
    "study_c_diabetes.pdf"
]

for paper in papers:
    docs = processor.process_pdf(paper)
    vector_store.add_documents(docs)
```

**Comparison Questions:**

1. **Methodology Comparison:**
   ```
   Q: "Compare the methodologies used across all three studies"
   
   Expected Answer Structure:
   Study A: Randomized controlled trial with 500 participants...
   Study B: Observational cohort study with 1200 participants...
   Study C: Meta-analysis of 15 previous studies...
   
   Key Similarities: All focused on Type 2 diabetes...
   Key Differences: Sample sizes varied significantly...
   ```

2. **Results Comparison:**
   ```
   Q: "What were the different efficacy rates reported?"
   
   Expected Answer:
   - Study A reported 65% efficacy [Source: study_a.pdf, Page: 12]
   - Study B reported 58% efficacy [Source: study_b.pdf, Page: 8]
   - Study C reported pooled efficacy of 62% [Source: study_c.pdf, Page: 15]
   ```

3. **Contradictions:**
   ```
   Q: "Are there any contradictory findings between the studies?"
   A: [Identifies and explains contradictions with citations]
   ```

---

## Advanced Queries

### Follow-Up Questions

The system maintains conversation context:

```
User: "What were the main findings?"
Assistant: [Provides summary of findings]

User: "What were the limitations?"
Assistant: [Understands context refers to the same study]

User: "How do these compare to previous research?"
Assistant: [Provides comparison if available in documents]
```

### Multi-Part Questions

```
Q: "What methodology was used, what were the results, and what do 
    the authors conclude?"

A: [Provides structured answer covering all three aspects with 
   separate citations for each part]
```

### Quantitative Analysis

```
Q: "What percentage improvement was observed and was it 
    statistically significant?"

A: "The study reported a 23% improvement in diagnostic accuracy. 
    Statistical significance was achieved with p<0.001. 
    [Source: paper.pdf, Page: 5, Section: Statistical Analysis]"
```

### Temporal Questions

```
Q: "How did the outcomes change over the 24-month study period?"

A: [Provides timeline of changes with citations to different 
   time points in the document]
```

---

## Tips for Better Results

### 1. Be Specific

❌ Poor: "Tell me about the study"
✅ Good: "What were the inclusion criteria for participants in the study?"

### 2. Use Domain Terms

❌ Poor: "What happened to the sick people?"
✅ Good: "What were the patient outcomes measured?"

### 3. Ask Follow-Ups

```
Q1: "What is the recommended dosage?"
Q2: "Are there any contraindications?"
Q3: "How does this compare to alternative treatments?"
```

### 4. Request Comparisons

```
Q: "Compare the cost-benefit analysis in Section 3 with the 
    projections in Section 5"
```

### 5. Verify Citations

Always check the cited sources to verify the information matches your understanding.

---

## Evaluation Examples

### Running Evaluations

```python
from src.evaluator import RAGEvaluator

evaluator = RAGEvaluator()

# Ask question
response = rag_chain.query("What is the sample size?")

# Evaluate
metrics = evaluator.evaluate_response(
    question="What is the sample size?",
    response=response,
    response_time=1.5
)

print(f"Relevance: {metrics.answer_relevance:.2%}")
print(f"Citation Accuracy: {metrics.citation_accuracy:.2%}")
print(f"Faithfulness: {metrics.faithfulness:.2%}")
```

### Batch Evaluation

```python
test_questions = [
    "What is the study design?",
    "What were the main findings?",
    "What are the limitations?",
    "What are the recommendations?"
]

for question in test_questions:
    response = rag_chain.query(question)
    # Evaluation happens automatically
```

---

## Common Patterns

### Pattern 1: Fact Extraction

```
Question Format: "What is [specific fact]?"
Example: "What is the sample size?"
Use Case: Extracting specific data points
```

### Pattern 2: Summary

```
Question Format: "Summarize [section/topic]"
Example: "Summarize the methodology section"
Use Case: Getting high-level overview
```

### Pattern 3: Comparison

```
Question Format: "Compare [X] and [Y]"
Example: "Compare the results from Study A and Study B"
Use Case: Analyzing differences between documents
```

### Pattern 4: Explanation

```
Question Format: "Why/How [phenomenon]?"
Example: "Why did the authors choose this methodology?"
Use Case: Understanding reasoning and context
```

### Pattern 5: List Generation

```
Question Format: "What are the [items]?"
Example: "What are the key limitations?"
Use Case: Generating structured lists
```

---

## Troubleshooting Query Issues

### Issue: Answer is too vague

**Solution:** Be more specific in your question
```
❌ "Tell me about the results"
✅ "What was the primary outcome measure and its result?"
```

### Issue: Wrong document referenced

**Solution:** Specify the document
```
❌ "What is the revenue?"
✅ "What is the Q3 2024 revenue according to the earnings report?"
```

### Issue: Missing information

**Solution:** Check if information exists in documents
```python
# Search for specific term
results = vector_store.similarity_search("revenue growth")
for doc, score in results:
    print(f"Found in: {doc.metadata['filename']}")
```

### Issue: Inconsistent citations

**Solution:** Use hybrid search mode for better accuracy
```python
response = rag_chain.query(
    question="What is the methodology?",
    search_mode="hybrid"  # Instead of "vector" or "keyword"
)
```

---

## Best Practices Summary

1. ✅ Upload related documents together
2. ✅ Use specific, domain-appropriate terminology
3. ✅ Ask follow-up questions for clarification
4. ✅ Verify citations in original documents
5. ✅ Use comparison mode for multi-document analysis
6. ✅ Enable conversation memory for related questions
7. ✅ Evaluate responses for critical applications
8. ✅ Start with hybrid search mode
9. ✅ Break complex questions into parts
10. ✅ Review retrieved chunks for context

---

**Need Help?** Check the main [README.md](README.md) for more information or refer to the [SETUP.md](SETUP.md) for installation issues.
