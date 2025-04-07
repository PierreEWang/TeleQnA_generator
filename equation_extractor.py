import os
import sys
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)),
            '../../')))

from deepdoc.vision import Recognizer, LayoutRecognizer, init_in_out, OCR
from api.utils.file_utils import get_project_base_directory
import numpy as np
import argparse
from pix2tex.cli import LatexOCR

import re


def is_valid_latex(latex_string):
    basic_latex_pattern = r'\\[a-zA-Z]+\{.*?\}|\\[a-zA-Z]+'
    return bool(re.search(basic_latex_pattern, latex_string))

def detect_equation_pages(pdf_path, threshold=0.5):
    args = argparse.Namespace()
    args.inputs = pdf_path
    args.output_dir = "./temp"
    images, _ = init_in_out(args)

    labels = LayoutRecognizer.labels
    detr = Recognizer(
        labels,
        "layout",
        os.path.join(
            get_project_base_directory(),
            "rag/res/deepdoc/"))

    equation_pages = []
    equation_bboxes = []
    for i, image in enumerate(images):
        layouts = detr([np.array(image)], threshold)[0]
        page_equations = []
        for layout in layouts:
            if layout["type"].lower() == "equation":
                equation_pages.append(i)
                page_equations.append(layout["bbox"])
        if page_equations:
            equation_bboxes.append((i, page_equations))

    return equation_pages, equation_bboxes

def ocr_equation_pages(pdf_path, equation_pages):
    args = argparse.Namespace()
    args.inputs = pdf_path
    args.output_dir = "./temp"
    images, _ = init_in_out(args)
    ocr = OCR()

    ocr_results = []
    for page_num in equation_pages:
        page_text = ocr(np.array(images[page_num]))
        ocr_results.append((page_num, "\n".join([result[1][0] for result in page_text])))

    return ocr_results

def ocr_equation_pages(pdf_path, equation_pages):
    args = argparse.Namespace()
    args.inputs = pdf_path
    args.output_dir = "./temp"
    images, _ = init_in_out(args)
    ocr = OCR()

    ocr_results = []
    for page_num in equation_pages:
        page_text = ocr(np.array(images[page_num]))
        ocr_results.append((page_num, "\n".join([result[1][0] for result in page_text])))

    return ocr_results

def process_pdf_equations(pdf_path):
    print(f"Processing PDF: {pdf_path}")

    equation_pages, equation_bboxes = detect_equation_pages(pdf_path)
    print(f"Pages with equations: {[page + 1 for page in equation_pages]}")

    ocr_results = ocr_equation_pages(pdf_path, equation_pages)
    latex_ocr = LatexOCR()

    equations_with_context = []
    for (page_num, page_text), (_, bboxes) in zip(ocr_results, equation_bboxes):
        args = argparse.Namespace()
        args.inputs = pdf_path
        args.output_dir = "./temp"
        images, _ = init_in_out(args)
        image = images[page_num]

        for bbox in bboxes:
            x0, y0, x1, y1 = bbox
            equation_image = image.crop((x0, y0, x1, y1))
            latex_code = latex_ocr(equation_image)

            # Add this check
            if not is_valid_latex(latex_code):
                print(f"Invalid LaTeX detected on page {page_num + 1}. Skipping this equation.")
                continue

            equations_with_context.append({
                'page_number': page_num + 1,
                'equation': latex_code,
                'context': page_text
            })

    print("\nEquations with LaTeX:")
    for item in equations_with_context:
        print(f"\nPage {item['page_number']}:")
        print(f"Equation (LaTeX): {item['equation']}")

    return equations_with_context

if __name__ == "__main__":
    pdf_path = "C:/Users/p50038325/Downloads/2401.00443v2.pdf"
    equations_with_context = process_pdf_equations(pdf_path)