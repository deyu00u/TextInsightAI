"""TextInsight AI — Streamlit interface."""
import hashlib
import pandas as pd
import streamlit as st
from analysis_utils import analyze_text, extract_pdf_text, MAX_AI_CHARS
from local_summary import generate_summary, MODEL_NAME

st.set_page_config(page_title='TextInsight AI', page_icon='📄', layout='wide')


with st.sidebar:
    st.title('TextInsight AI')
    st.caption('DOCUMENT INTELLIGENCE')
    st.divider()
    st.subheader('AI settings')
    model = MODEL_NAME
    st.caption('Local AI model: ' + model)
    st.caption('Extractive summarization · English · CPU')
    length = st.selectbox('Summary length', ['Short', 'Balanced', 'Detailed'], index=1)
    exclude = st.checkbox('Exclude common English words', value=True)
    st.divider()
    st.caption('All document processing runs locally. The model is downloaded on first use; no API key is required.')

st.title('TextInsight AI')
st.markdown('Analyze documents. Discover key words. Understand the essentials.')
st.caption('AI-POWERED TEXT ANALYSIS & SUMMARIZATION')

with st.container(border=True):
    st.subheader('1 · Input document')
    method = st.radio('Input method', ['Enter Text', 'Upload PDF'], horizontal=True)
    document_text = ''
    source = 'Typed text'
    if method == 'Enter Text':
        document_text = st.text_area('Your text', height=200, placeholder='Type or paste your document here…')
    else:
        upload = st.file_uploader('Select a PDF (up to 20 MB)', type=['pdf'])
        if upload is not None:
            source = upload.name
            try:
                document_text, pages, empty_pages = extract_pdf_text(upload.getvalue())
                st.success(f'Extracted text from {pages - empty_pages} of {pages} page(s).')
                if empty_pages:
                    st.warning(f'{empty_pages} page(s) contain no selectable text and may need OCR.')
                with st.expander('Preview extracted text'):
                    st.text(document_text[:5000])
            except Exception as exc:
                st.error(f'PDF could not be read: {exc}')
        st.caption(f'{len(document_text):,} characters in current input')
    use_ai = st.checkbox('Generate local AI summary', value=True)
    if use_ai and len(document_text) > MAX_AI_CHARS:
        st.warning('AI summaries support up to 40,000 characters. Local statistics still cover the whole document.')
    clicked = st.button('Analyze document', type='primary', width='stretch')

fingerprint = hashlib.sha256((source + '\0' + document_text + '\0' + str(exclude)).encode('utf-8')).hexdigest()
if clicked:
    st.session_state.pop('analysis', None)
    if not document_text.strip():
        st.warning('Enter text or upload a readable PDF first.')
    else:
        record = {'id': fingerprint, 'source': source, 'stats': analyze_text(document_text, exclude), 'summary': None, 'error': None, 'model': model, 'ai_requested': use_ai}
        if use_ai:
            with st.spinner('Generating local AI summary… First use downloads the model.'):
                try:
                    record['summary'] = generate_summary(document_text, length)
                except Exception as exc:
                    record['error'] = f'Local AI could not summarize: {exc}'
        st.session_state['analysis'] = record

record = st.session_state.get('analysis')
if record and record['id'] != fingerprint:
    st.info('Input or word-filter settings changed. Analyze again for updated results.')
    record = None

if record:
    stats = record['stats']
    st.subheader('2 · Document analysis')
    st.caption(f"Source: {record['source']}")
    labels = [('Words', 'words'), ('Characters', 'characters'), ('Sentences ≈', 'sentences'), ('Paragraphs ≈', 'paragraphs')]
    for col, (label, key) in zip(st.columns(4), labels):
        col.metric(label, f'{stats[key]:,}')
    st.metric('Characters without whitespace', f"{stats['characters_no_spaces']:,}")
    st.caption('Sentence and paragraph counts are estimates based on punctuation and blank lines.')
    st.subheader('3 · Most frequent words')
    st.caption('Top 10 words; common English words ' + ('excluded.' if exclude else 'included.'))
    df = pd.DataFrame(stats['frequent_words'], columns=['Word', 'Frequency'])
    if not df.empty:
        left, right = st.columns([1, 2])
        left.dataframe(df, hide_index=True, width='stretch')
        right.bar_chart(df, x='Word', y='Frequency', horizontal=True)
    else:
        st.info('No words matched the current filter.')
    st.subheader('4 · AI-generated summary')
    if record['summary']:
        st.caption(f"Model: {record['model']}")
        st.write(record['summary'])
        st.caption('Extractive summary: important sentences selected from the original document.')
    elif record['error']:
        st.error(record['error'])
    else:
        st.info('Enable local AI summary and analyze again to generate a summary.')
    report = ['TextInsight AI — Document Report', f"Source: {record['source']}", '']
    report += [f'{label}: {stats[key]}' for label, key in labels]
    report += [f"Characters without whitespace: {stats['characters_no_spaces']}", '', 'Most frequent words:']
    report += [f'{word}: {count}' for word, count in stats['frequent_words']]
    report += ['', 'AI summary:', f"Model: {record['model']}" if record['summary'] else '', record['summary'] or 'Not generated.']
    st.download_button('Download analysis report (.txt)', '\n'.join(report), file_name='textinsight-report.txt', mime='text/plain')
else:
    st.info('Your analysis results will appear here after you submit a document.')
st.divider()
st.caption('TextInsight AI · Python + Streamlit + PyMuPDF + Local BGE AI')
