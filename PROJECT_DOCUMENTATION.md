# TextInsight AI — Local AI Edition

## Project overview
TextInsight AI is a web-based document analysis and extractive summarization application. It accepts typed text or selectable text in a PDF, counts words, characters, sentences and paragraphs, displays frequent words and a chart, and selects important sentences with a pretrained neural model. It can export results as a text report.

## Tools and model
- Python 3.12: application programming language.
- Streamlit: browser interface.
- PyMuPDF: PDF extraction.
- Pandas and NumPy: tabular data and numerical similarity computations.
- Python regular expressions and Counter: descriptive statistics.
- FastEmbed and ONNX Runtime: local CPU model inference.
- BAAI/bge-small-en-v1.5: pretrained English sentence embedding model, distributed through FastEmbed. This is not a generative language model. It encodes each sentence into a numerical vector representing meaning. The model is not trained by the group.
- VS Code: development environment.

## Method
Text input or PDF → extract and normalize text → compute descriptive statistics → split into sentences → generate neural sentence embeddings → normalize vectors and calculate document centroid → rank sentences by cosine similarity to the centroid, penalizing redundancy with already selected sentences → restore source order → display summary.

This is extractive AI summarization, which reproduces selected sentences from the source rather than generating new prose. It reduces the risk of invented facts but may omit context or select unrepresentative sentences. Short, balanced and detailed settings control the maximum number of sentences. Short sources may yield fewer sentences.

## Limitations
English is the target language. PDF scans without a text layer require OCR, which is not included. PDFs are limited to 20 MB; AI input is limited to 40,000 characters. Very long individual sentences may be truncated internally by the embedding tokenizer. Sentence and paragraph counts are estimates. Internet access is required initially to install dependencies and download the pretrained model; cached models can be loaded locally on subsequent runs. There is no Gemini API key or paid API requirement. Users should verify summary accuracy.

## Testing and demonstration
1. Run START_LOCAL_AI.bat inside the existing project folder.
2. Paste a multi-sentence English passage, enable local AI summary and click Analyze document.
3. Check counts, frequency chart, model name and selected sentences.
4. Upload sample.pdf and repeat.
5. Test empty input and scanned PDF handling. Download the analysis report.
6. Capture screenshots of actual results for the final presentation. Live local-model inference must be verified on the target PC; automated ranking tests use synthetic embeddings.

## References
- https://docs.streamlit.io/
- https://pymupdf.readthedocs.io/
- https://qdrant.tech/documentation/fastembed/fastembed-quickstart/
- https://huggingface.co/BAAI/bge-small-en-v1.5
- https://onnxruntime.ai/
