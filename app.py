"""TextInsight AI — gradient document workspace, compatible with local and cloud deployment."""
import hashlib
import altair as alt
import pandas as pd
import streamlit as st
from analysis_utils import analyze_text, extract_pdf_text, MAX_AI_CHARS
from local_summary import generate_summary, MODEL_NAME

st.set_page_config(page_title='TextInsight AI | Document workspace', page_icon='📄', layout='wide')

st.markdown('''<style>
.block-container {max-width: 1440px; padding-top: 2.8rem; padding-bottom: 2rem;}
[data-testid="stSidebar"] {border-right: 1px solid #E1E5F2;}
.ti-brand {display:flex; align-items:center; gap:11px; margin: 0 0 6px;}
.ti-mark {width:40px; height:40px; border-radius:12px; background:linear-gradient(135deg,#315ACB,#8054D5); color:white; display:grid; place-items:center; flex-shrink:0;}
.ti-brand strong {font-size:19px; letter-spacing:-.04em; color:#20254C;}
.ti-kicker {font-size:11px; letter-spacing:.13em; font-weight:700; color:#626A87; text-transform:uppercase;}
.ti-hero {background:linear-gradient(115deg,#233FA8 0%,#4945C6 50%,#7041C6 100%); box-shadow:0 9px 24px rgba(52,55,130,.15); border-radius:20px; padding:30px 32px; color:white; margin-bottom:8px;}
.ti-hero .ti-kicker {color:#E3E7FF;}
.ti-hero h1 {font-size:clamp(25px,3vw,40px); line-height:1.15; letter-spacing:-.04em; color:#FFFFFF !important; padding:12px 0 8px; margin:0;}
.ti-hero p {color:#F0EFFF; margin:0; font-size:15px; line-height:1.6; max-width:700px;}
.ti-pill {display:inline-flex; align-items:center; gap:7px; border:1px solid #DCDDF8; border-radius:20px; background:#EEEDFF; color:#4338A3; padding:5px 10px; font-size:12px; font-weight:650; margin:10px 0;}
.ti-dot {width:7px; height:7px; background:#6555D7; border-radius:50%;}
.ti-label {font-size:11px; font-weight:750; color:#5C54B8; letter-spacing:.10em; text-transform:uppercase; margin-bottom:3px;}
.ti-section {font-size:20px; line-height:1.3; color:#23294A; letter-spacing:-.025em; font-weight:720; margin:0 0 3px;}
.ti-hint {font-size:13px; line-height:1.5; color:#626A87; margin-bottom:8px;}
.ti-empty {border:1px dashed #D6D9EF; border-radius:14px; padding:27px 16px; text-align:center; background:#F7F7FE; color:#626A87; margin:6px 0;}
.ti-empty strong {display:block; font-size:15px; color:#30386A; margin-bottom:7px;}
.ti-step {display:flex; align-items:center; gap:9px; padding:8px 0; font-size:14px; color:#414967;}
.ti-step span {height:23px; width:23px; display:grid; place-items:center; border-radius:7px; background:#E6E8FC; color:#4F46B8; font-size:12px; font-weight:750;}
[data-testid="stMetric"] {background:#FFFFFF; border:1px solid #E0E3F2; border-radius:14px; padding:16px 15px; min-width:0;}
[data-testid="stMetricLabel"] {color:#626A87;}
[data-testid="stMetricValue"] {color:#343A8C; font-weight:700; font-size:clamp(23px,2.4vw,34px); letter-spacing:-.04em;}
[data-testid="stVerticalBlockBorderWrapper"] > div {border-radius:15px;}
[data-testid="stFileUploaderDropzone"] {border:1px dashed #A5ADE7; border-radius:12px; background:#F2F4FF;}
[data-testid="stButton"] button[kind="primary"] {min-height:44px; font-weight:650; border-radius:10px; background:linear-gradient(110deg,#3556C6,#7041C6); color:#fff; border:0;}
[data-testid="stButton"] button[kind="primary"]:hover {background:linear-gradient(110deg,#2948B5,#6033B6); color:#fff;}
[data-testid="stButton"] button:focus-visible, [data-testid="stDownloadButton"] button:focus-visible {outline:3px solid #7165D9; outline-offset:3px;}
[data-testid="stMetric"] {box-shadow:0 3px 12px rgba(38,45,92,.045);}
.st-key-input_panel textarea {line-height:1.6;}
[data-testid="stText"] {white-space:pre-wrap; overflow-wrap:anywhere;}
[data-testid="stText"] pre {white-space:pre-wrap; overflow-wrap:anywhere; font-family:inherit; line-height:1.65;}
.st-key-summary_panel [data-testid="stText"] {background:#F4F3FF; border:1px solid #E1DDF9; border-radius:12px; padding:14px; color:#282D52;}
@media (max-width: 760px) {
 .block-container {padding:1rem .85rem 2rem;}
 .ti-hero {padding:22px 18px; border-radius:15px;}
 [data-testid="stHorizontalBlock"] {flex-wrap:wrap; gap:.65rem;}
 .st-key-workspace [data-testid="stColumn"], .st-key-frequencies [data-testid="stColumn"] {flex:1 1 100% !important; min-width:0 !important; width:100% !important;}
 .st-key-metrics [data-testid="stColumn"] {flex:1 1 44% !important; min-width:0 !important;}
}
</style>''', unsafe_allow_html=True)


def section(number, title, detail):
    # Only fixed application labels are passed to this HTML helper.
    st.markdown(f'<div class="ti-label">{number}</div><div class="ti-section">{title}</div><div class="ti-hint">{detail}</div>', unsafe_allow_html=True)


def empty_panel(title, detail):
    st.markdown(f'<div class="ti-empty"><strong>{title}</strong>{detail}</div>', unsafe_allow_html=True)


def fill_example():
    st.session_state['document_input'] = (
        'Trees are important to the environment. They provide oxygen, clean the air, '
        'and give animals shelter. Trees also help prevent floods. People should plant '
        'more trees to protect nature.'
    )


with st.sidebar:
    st.markdown('''<div class="ti-brand"><div class="ti-mark">TI</div><strong>TextInsight AI</strong></div>
    <div class="ti-kicker">Document workspace</div>
    <div class="ti-pill"><span class="ti-dot"></span> AI model · CPU</div>''', unsafe_allow_html=True)
    st.divider()
    st.markdown('**WORKFLOW**')
    st.markdown('''<div class="ti-step"><span>1</span> Add a document</div>
    <div class="ti-step"><span>2</span> Review text statistics</div>
    <div class="ti-step"><span>3</span> Read &amp; export summary</div>''', unsafe_allow_html=True)
    st.divider()
    st.subheader('Analysis settings')
    length = st.selectbox('Summary length', ['Short', 'Balanced', 'Detailed'], index=1)
    exclude = st.checkbox('Exclude common English words', value=True)
    st.divider()
    st.markdown('**AI model**')
    st.caption(MODEL_NAME)
    st.caption('Extractive summarization · English · CPU')
    st.markdown('**Privacy**')
    st.caption('Documents are processed on the application server (your computer when run locally, or the hosting server online). No external AI API key is required. Avoid uploading sensitive documents to the public app.')
    with st.expander('Supported documents'):
        st.caption('Selectable-text PDF (20 MB maximum) or pasted text. AI input: up to 40,000 characters. Scanned pages need OCR, which is not included.')

st.markdown('''<div class="ti-hero"><div class="ti-kicker">TextInsight AI / Document intelligence</div>
<h1>Understand more. Read less.</h1><p>Turn documents into clear insights with text statistics, meaningful word frequencies and AI-powered summaries — without an AI API key.</p></div>''', unsafe_allow_html=True)

with st.container(key='workspace'):
    input_col, summary_col = st.columns([1.25, 1], gap='medium')
    with input_col:
        with st.container(border=True, key='input_panel'):
            section('01 / Input', 'Add your document', 'Paste text or upload a PDF to begin. You can also try an example.')
            method = st.radio('Input method', ['Enter Text', 'Upload PDF'], horizontal=True)
            document_text, source = '', 'Typed text'
            if method == 'Enter Text':
                st.button('Try sample text', on_click=fill_example, key='sample_button')
                document_text = st.text_area('Your text', height=210, placeholder='Type or paste your document here…', key='document_input')
            else:
                upload = st.file_uploader('Drop a PDF here or browse (up to 20 MB)', type=['pdf'])
                if upload is not None:
                    source = upload.name
                    try:
                        document_text, pages, empty_pages = extract_pdf_text(upload.getvalue())
                        st.success(f'Text extracted from {pages - empty_pages} of {pages} page(s).')
                        if empty_pages:
                            st.warning(f'{empty_pages} page(s) contain no selectable text and may need OCR.')
                        with st.expander('Preview extracted text'):
                            st.text(document_text[:5000])
                    except Exception as exc:
                        st.error(f'PDF could not be read: {exc}')
            st.caption(f'{len(document_text):,} characters in current input')
            use_ai = st.checkbox('Generate AI summary', value=True)
            if use_ai and len(document_text) > MAX_AI_CHARS:
                st.warning('AI summaries support up to 40,000 characters. Shorten the input to summarize it, or turn off AI for full-document statistics.')
            clicked = st.button('Analyze document', type='primary', width='stretch')

    fingerprint = hashlib.sha256((source + '\0' + document_text + '\0' + str(exclude) + '\0' + str(use_ai) + '\0' + (length if use_ai else '')).encode('utf-8')).hexdigest()
    if clicked:
        st.session_state.pop('analysis', None)
        if not document_text.strip():
            input_col.warning('Enter text or upload a readable PDF first.')
        else:
            record = {'id': fingerprint, 'source': source, 'stats': analyze_text(document_text, exclude), 'summary': None, 'error': None, 'model': MODEL_NAME, 'ai_requested': use_ai}
            if use_ai:
                with summary_col:
                    with st.spinner('Generating AI summary… First use downloads the model.'):
                        try:
                            record['summary'] = generate_summary(document_text, length)
                        except Exception as exc:
                            record['error'] = f'AI could not summarize: {exc}'
            st.session_state['analysis'] = record

    record = st.session_state.get('analysis')
    stale = bool(record and record['id'] != fingerprint)
    if stale:
        record = None
        input_col.info('Input or settings changed. Analyze again to refresh results.')

    labels = [('Words', 'words'), ('Characters', 'characters'), ('Sentences ≈', 'sentences'), ('Paragraphs ≈', 'paragraphs'), ('Non-space characters', 'characters_no_spaces')]
    with summary_col:
        with st.container(border=True, key='summary_panel'):
            section('AI / Summary', 'Key insights', 'Important sentences from the original document.')
            st.caption(f'Model: {MODEL_NAME}')
            if not record:
                empty_panel('Your summary will appear here', 'Add a document and select Analyze document to get started.')
            elif record['summary']:
                st.text(record['summary'])
                st.caption('Extractive summary: original sentences, not newly generated prose. Verify important details against the source.')
                with st.expander('Copy summary'):
                    st.code(record['summary'], language=None, wrap_lines=True)
                st.download_button('Download summary (.txt)', record['summary'], file_name='textinsight-summary.txt', mime='text/plain', width='stretch')
            elif record['error']:
                st.error(record['error'])
            else:
                st.info('Enable AI summary and analyze again to generate a summary.')
            if record:
                stats = record['stats']
                report = ['TextInsight AI — Document Report', f"Source: {record['source']}", '']
                report += [f'{label}: {stats[key]}' for label, key in labels]
                report += ['', 'Most frequent words:']
                report += [f'{word}: {count}' for word, count in stats['frequent_words']]
                report += ['', 'AI summary:', f"Model: {record['model']}" if record['summary'] else '', record['summary'] or 'Not generated.']
                st.download_button('Download analysis report (.txt)', '\n'.join(report), file_name='textinsight-report.txt', mime='text/plain', width='stretch')

with st.container(key='metrics'):
    section('02 / Statistics', 'Document overview', 'Source and essential document measurements.')
    if record:
        st.caption(f"Source: {record['source']}")
    else:
        st.caption('No analyzed document yet.')
    for col, (label, key) in zip(st.columns([1, 1, 1, 1, 1.35]), labels):
        col.metric(label, f"{record['stats'][key]:,}" if record else '—')
    st.caption('Sentence and paragraph counts are estimates based on punctuation and blank lines.')

with st.container(border=True, key='frequencies'):
    section('03 / Vocabulary', 'Most frequent words', 'Top 10 words ranked by occurrence. Common English words ' + ('excluded.' if exclude else 'included.'))
    if not record:
        empty_panel('No word frequencies yet', 'Analyze a document to reveal its most common words.')
    else:
        df = pd.DataFrame(record['stats']['frequent_words'], columns=['Word', 'Frequency'])
        if not df.empty:
            left, right = st.columns([1.7, 1], gap='medium')
            chart = alt.Chart(df).mark_bar(color='#6156CF', cornerRadiusEnd=5, size=19).encode(
                y=alt.Y('Word:N', sort=df['Word'].tolist(), title=None, axis=alt.Axis(labelLimit=160)),
                x=alt.X('Frequency:Q', title='Occurrences', axis=alt.Axis(tickMinStep=1), scale=alt.Scale(zero=True)),
                tooltip=[alt.Tooltip('Word:N'), alt.Tooltip('Frequency:Q', format=',d')],
            ).properties(height=max(160, len(df) * 28)).configure_view(stroke=None)
            left.altair_chart(chart, width='stretch')
            right.dataframe(df, hide_index=True, width='stretch', height=min(390, 38 + len(df)*35))
        else:
            st.info('No words matched the current filter.')

st.divider()
st.caption('TextInsight AI  /  Python · Streamlit · PyMuPDF · BGE AI  /  Document intelligence')
