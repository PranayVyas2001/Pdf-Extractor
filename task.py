import pdfplumber
from PyPDF2 import PdfWriter, PdfReader

def extract_text_blocks(pdf_file):
    """
    Extracts text and bounding boxes from the PDF to detect whitespace between text blocks.
    """
    text_blocks = []
    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text_blocks.append({
                "page": page_num,
                "chars": page.chars  # Extract characters and their positions
            })
    return text_blocks


def detect_large_whitespaces(text_blocks, threshold=50):
    """
    Detect large whitespaces between blocks of text by comparing the vertical (Y-axis) distance
    between consecutive characters.
    """
    whitespace_locations = {}
    for block in text_blocks:
        page = block['page']
        chars = block['chars']
        prev_bottom = 0
        large_spaces = []
        for char in chars:
            if prev_bottom:
                whitespace = char["top"] - prev_bottom
                if whitespace > threshold:
                    large_spaces.append((prev_bottom, char["top"]))
            prev_bottom = char["bottom"]

        if large_spaces:
            whitespace_locations[page] = large_spaces
    return whitespace_locations


def make_cuts_based_on_whitespace(whitespace_locations, num_cuts):
    """
    From detected whitespaces, choose the largest X cuts where X is specified by num_cuts.
    """
    cut_positions = []
    all_whitespace = []
    
    # Flatten the whitespace data from all pages
    for page, spaces in whitespace_locations.items():
        for space in spaces:
            all_whitespace.append((page, space))
    
    # Sort the whitespace by size (descending)
    sorted_whitespace = sorted(all_whitespace, key=lambda x: x[1][1] - x[1][0], reverse=True)
    
    # Select the largest whitespaces
    cut_positions = sorted_whitespace[:num_cuts]
    
    return cut_positions


def split_pdf_by_cuts(input_pdf, cut_positions):
    """
    Split the PDF into multiple segments based on the largest whitespace cuts.
    Save each segment as a new PDF file.
    """
    reader = PdfReader(input_pdf)
    
    for i, (page_num, (top, bottom)) in enumerate(cut_positions):
        writer = PdfWriter()
        writer.add_page(reader.pages[page_num])
        output_filename = f"segment_{i + 1}.pdf"
        
        with open(output_filename, "wb") as output_pdf:
            writer.write(output_pdf)
        print(f"Saved: {output_filename}")


def segment_pdf(input_pdf, num_cuts):
    """
    Main function to segment the PDF based on whitespace and create multiple output PDFs.
    """
    text_blocks = extract_text_blocks(input_pdf)
    whitespace_locations = detect_large_whitespaces(text_blocks)
    cut_positions = make_cuts_based_on_whitespace(whitespace_locations, num_cuts)
    split_pdf_by_cuts(input_pdf, cut_positions)


if _name_ == "_main_":
    # Example usage:
    input_pdf_path = "input.pdf"
    number_of_cuts = 3  # Define how many segments you want
    segment_pdf(input_pdf_path, number_of_cuts)