import os
import fitz  # PyMuPDF
import re
import json
import tempfile
import numpy as np
from collections import Counter
from typing import List, Dict, Any
from pydantic import BaseModel

# Data models
class HeadingData(BaseModel):
    level: str  # H1, H2, H3, H4
    text: str
    page: int

class TextSpan(BaseModel):
    text: str
    font_size: float
    font_weight: str
    x_position: float
    y_position: float
    width: float
    height: float
    page: int
    bbox: List[float]

class PDFOutlineExtractor:
    def __init__(self):
        self.numbering_patterns = {
            'arabic': r'^\d+(\.\d+)*\s+',
            'roman_upper': r'^[IVXLCDM]+\.\s+',
            'roman_lower': r'^[ivxlcdm]+\.\s+',
            'alpha_upper': r'^[A-Z]\.\s+',
            'alpha_lower': r'^[a-z]\.\s+',
            'chinese': r'^第.*章\s+',
            'arabic_sectioned': r'^\d+\.\d+(\.\d+)*\s+',
            'bracketed': r'^\(\d+\)\s+',
        }
        self.toc_keywords = [
            'table of contents', 'contents', 'index', '目录', 'table des matières',
            'inhaltsverzeichnis', 'índice', 'sommario', '目次'
        ]

    def extract_outline(self, pdf_bytes: bytes) -> Dict[str, Any]:
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(pdf_bytes)
                tmp_file.flush()
                tmp_path = tmp_file.name  # Save path
    
            doc = fitz.open(tmp_path)
            title = self.extract_embedded_title(doc)
            embedded_outline = self.extract_embedded_outline(doc)
            if not title:
                title = self.extract_first_page_title(doc)
            text_spans = self.extract_text_spans(doc)
            style_clusters = self.cluster_font_styles(text_spans)
            numbered_headings = self.detect_numbered_headings(text_spans)
            toc_headings = self.extract_toc_headings(doc, text_spans)
            ml_headings = self.classify_headings_rule_based(text_spans, style_clusters)
            final_outline = self.assemble_hierarchy(
                embedded_outline, numbered_headings, toc_headings, ml_headings, text_spans
            )
            return {
                "title": title or "Untitled Document",
                "outline": final_outline
            }
        finally:
            if 'doc' in locals():
                doc.close()
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)


    def extract_embedded_title(self, doc: fitz.Document) -> str:
        metadata = doc.metadata
        return metadata.get('title', '').strip() if metadata else ''

    def extract_embedded_outline(self, doc: fitz.Document) -> List[Dict]:
        outline = []
        try:
            toc = doc.get_toc(simple=False)
            for level, title, page, dest in toc:
                outline.append({
                    'level': f'H{min(level, 4)}',
                    'text': title.strip(),
                    'page': page
                })
        except:
            pass
        return outline

    def extract_first_page_title(self, doc: fitz.Document) -> str:
        if len(doc) == 0:
            return ''
        page = doc[0]
        blocks = page.get_text("dict")["blocks"]
        largest_text = ""
        max_font_size = 0
        highest_y = float('inf')
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        font_size = span["size"]
                        y_pos = span["bbox"][1]
                        if font_size > max_font_size or (font_size == max_font_size and y_pos < highest_y):
                            if len(text) > 3 and not text.isdigit():
                                largest_text = text
                                max_font_size = font_size
                                highest_y = y_pos
        return largest_text

    def extract_text_spans(self, doc: fitz.Document) -> List[TextSpan]:
        spans = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        line_spans = []
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text:
                                line_text += text + " "
                                line_spans.append(span)
                        line_text = line_text.strip()
                        if len(line_text) >= 3 and not self.is_likely_body_text(line_text):
                            if line_spans:
                                first_span = line_spans[0]
                                spans.append(TextSpan(
                                    text=line_text,
                                    font_size=first_span["size"],
                                    font_weight="bold" if any("bold" in s["font"].lower() for s in line_spans) else "normal",
                                    x_position=first_span["bbox"][0],
                                    y_position=first_span["bbox"][1],
                                    width=line_spans[-1]["bbox"][2] - first_span["bbox"][0],
                                    height=first_span["bbox"][3] - first_span["bbox"][1],
                                    page=page_num + 1,
                                    bbox=list(first_span["bbox"])
                                ))
        return spans

    def is_likely_body_text(self, text: str) -> bool:
        if len(text) > 120:
            return True
        if text.endswith(('.', ':', ',', ';', '!', '?')):
            return True
        if 'http' in text.lower() or '@' in text or 'www.' in text.lower():
            return True
        if len(re.findall(r'\d', text)) > len(text) * 0.3:
            return True
        if any(word in text.lower() for word in ['copyright', '©', 'all rights reserved', 'page', 'draft']):
            return True
        if re.match(r'^\d+\.\s+[a-z]', text):
            return True
        if text.lower().startswith(('who have', 'who are', 'this is', 'the ', 'a ', 'an ', 'in ', 'at ', 'on ', 'with ')):
            return True
        return False

    def cluster_font_styles(self, text_spans: List[TextSpan]) -> Dict[str, str]:
        if not text_spans:
            return {}
        font_sizes = [span.font_size for span in text_spans]
        size_counter = Counter(font_sizes)
        top_sizes = [size for size, _ in size_counter.most_common(4)]
        top_sizes.sort(reverse=True)
        style_map = {}
        for i, size in enumerate(top_sizes):
            if i == 0:
                style_map[str(size)] = "H1"
            elif i == 1:
                style_map[str(size)] = "H2"
            elif i == 2:
                style_map[str(size)] = "H3"
            elif i == 3:
                style_map[str(size)] = "H4"
        return style_map

    def detect_numbered_headings(self, text_spans: List[TextSpan]) -> List[Dict]:
        headings = []
        for span in text_spans:
            text = span.text.strip()
            level = None
            if self.is_likely_body_text(text):
                continue
            if re.match(r'^\d+\.\d+\.\d+\s+[A-Z]', text):
                level = "H3"
            elif re.match(r'^\d+\.\d+\s+[A-Z]', text):
                level = "H2"
            elif re.match(r'^\d+\.\s+[A-Z]', text):
                level = "H1"
            elif re.match(r'^[IVXLCDM]+\.\s+[A-Z]', text, re.IGNORECASE):
                level = "H1"
            elif re.match(r'^[A-Za-z]\.\s+[A-Z]', text):
                level = "H2"
            elif re.match(r'^\(\d+\)\s+[A-Z]', text):
                level = "H2"
            elif re.match(r'^(chapter|section|part|appendix)\s+\d+', text, re.IGNORECASE):
                level = "H1"
            if level:
                headings.append({
                    'level': level,
                    'text': text,
                    'page': span.page,
                    'font_size': span.font_size,
                    'y_position': span.y_position,
                    'source': 'numbered'
                })
        return headings

    def extract_toc_headings(self, doc: fitz.Document, text_spans: List[TextSpan]) -> List[Dict]:
        toc_headings = []
        for page_num in range(min(5, len(doc))):
            page = doc[page_num]
            text = page.get_text().lower()
            if any(keyword in text for keyword in self.toc_keywords):
                lines = page.get_text().split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if any(keyword in line.lower() for keyword in self.toc_keywords):
                        continue
                    toc_match = re.search(r'^(\d+(?:\.\d+)*)\s*\.?\s*([^.]+?)\.{2,}\s*(\d+)$', line)
                    if toc_match:
                        number = toc_match.group(1)
                        heading_text = toc_match.group(2).strip()
                        page_ref = int(toc_match.group(3))
                        dots = number.count('.')
                        level = f"H{min(dots + 1, 4)}"
                        toc_headings.append({
                            'level': level,
                            'text': f"{number} {heading_text}",
                            'page': page_ref
                        })
                    elif re.search(r'^([^.]+?)\.{3,}\s*(\d+)$', line):
                        simple_match = re.search(r'^([^.]+?)\.{3,}\s*(\d+)$', line)
                        heading_text = simple_match.group(1).strip()
                        page_ref = int(simple_match.group(2))
                        level = "H1"
                        if any(word in heading_text.lower() for word in ['chapter', 'section', 'part']):
                            level = "H1"
                        elif heading_text.startswith('  ') or heading_text.startswith('\t'):
                            level = "H2"
                        toc_headings.append({
                            'level': level,
                            'text': heading_text,
                            'page': page_ref
                        })
        return toc_headings

    def classify_headings_rule_based(self, text_spans: List[TextSpan], style_clusters: Dict[str, str]) -> List[Dict]:
        headings = []
        font_sizes = [span.font_size for span in text_spans]
        if not font_sizes:
            return headings
        avg_font_size = np.mean(font_sizes)
        max_font_size = max(font_sizes)
        for span in text_spans:
            text = span.text.strip()
            if (len(text) > 100 or 
                text.lower().startswith(('figure', 'table', 'image', 'page')) or
                self.is_likely_body_text(text)):
                continue
            if span.font_size <= avg_font_size:
                continue
            font_key = str(span.font_size)
            if font_key in style_clusters:
                level = style_clusters[font_key]
            else:
                size_ratio = span.font_size / max_font_size
                if size_ratio >= 0.8:
                    level = "H1"
                elif size_ratio >= 0.6:
                    level = "H2"
                elif size_ratio >= 0.4:
                    level = "H3"
                else:
                    level = "H4"
            is_heading = False
            if (span.font_weight == "bold" and span.font_size > avg_font_size * 1.2):
                is_heading = True
            elif span.font_size > avg_font_size * 1.5:
                is_heading = True
            elif any(pattern in text for pattern in ['chapter', 'section', 'appendix']) and span.font_size > avg_font_size:
                is_heading = True
            elif text.isupper() and len(text) < 50 and span.font_size > avg_font_size:
                is_heading = True
            elif text.istitle() and len(text) < 80 and span.font_size > avg_font_size * 1.1:
                is_heading = True
            if is_heading:
                headings.append({
                    'level': level,
                    'text': text,
                    'page': span.page,
                    'font_size': span.font_size,
                    'y_position': span.y_position
                })
        return headings

    def assemble_hierarchy(self, embedded_outline: List[Dict], numbered_headings: List[Dict], toc_headings: List[Dict], ml_headings: List[Dict], text_spans: List[TextSpan]) -> List[Dict]:
        all_headings = []
        if embedded_outline:
            all_headings.extend(embedded_outline)
        elif toc_headings:
            all_headings.extend(toc_headings)
        else:
            numbered_texts = {h['text'].strip() for h in numbered_headings}
            all_headings.extend(numbered_headings)
            for ml_heading in ml_headings:
                ml_text = ml_heading['text'].strip()
                if not any(ml_text in num_text or num_text in ml_text for num_text in numbered_texts):
                    all_headings.append(ml_heading)
        seen_texts = set()
        cleaned_headings = []
        all_headings.sort(key=lambda x: (x.get('page', 0), x.get('y_position', 0)))
        for heading in all_headings:
            text = heading['text'].strip()
            if not text or len(text) < 3 or text.isdigit():
                continue
            normalized_text = re.sub(r'\s+', ' ', text).strip()
            is_duplicate = False
            for seen_text in seen_texts:
                if (normalized_text.lower() == seen_text.lower() or
                    (len(normalized_text) > 20 and normalized_text.lower() in seen_text.lower()) or
                    (len(seen_text) > 20 and seen_text.lower() in normalized_text.lower())):
                    is_duplicate = True
                    break
            if not is_duplicate:
                seen_texts.add(normalized_text)
                cleaned_headings.append({
                    'level': heading['level'],
                    'text': normalized_text,
                    'page': heading['page']
                })
        return cleaned_headings[:30]


def main():
    input_dir = os.path.join(os.getcwd(), 'input')
    output_dir = os.path.join(os.getcwd(), 'output')
    os.makedirs(output_dir, exist_ok=True)
    extractor = PDFOutlineExtractor()
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_dir, filename)
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()
            result = extractor.extract_outline(pdf_bytes)
            output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.json')
            with open(output_path, 'w', encoding='utf-8') as out_f:
                json.dump(result, out_f, ensure_ascii=False, indent=2)
            print(f"Processed {filename} -> {output_path}")

if __name__ == "__main__":
    main()
