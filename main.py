from mistralai import Mistral
from dotenv import load_dotenv
import datauri
import os

# Load API key from .env
load_dotenv()
api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)

def save_image(image, output_dir):
    parsed = datauri.parse(image.image_base64)
    image_path = os.path.join(output_dir, image.id)
    with open(image_path, "wb") as file:
        file.write(parsed.data)

def create_markdown_file(ocr_response, output_filename="output.md", images_dir="images"):
    os.makedirs(images_dir, exist_ok=True)
    with open(output_filename, "wt", encoding="utf-8") as f:
        for page in ocr_response.pages:
            f.write(page.markdown)
            for image in page.images:
                save_image(image, images_dir)

def upload_pdf(filename):
    with open(filename, "rb") as file_obj:
        uploaded_pdf = client.files.upload(
            file={
                "file_name": os.path.basename(filename),
                "content": file_obj,
            },
            purpose="ocr"
        )
    signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)
    return signed_url.url

def process_books_folder(books_folder):
    for filename in os.listdir(books_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(books_folder, filename)
            print(f"Processing: {pdf_path}")
            signed_url = upload_pdf(pdf_path)
            ocr_response = client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": signed_url,
                },
                include_image_base64=True,
            )
            base_name = os.path.splitext(filename)[0]
            output_md = f"{base_name}.md"
            images_dir = f"{base_name}_images"
            create_markdown_file(ocr_response, output_filename=output_md, images_dir=images_dir)
            print(f"OCR complete for {filename}. Markdown and images saved.")

def main():
    books_folder = r"C:\Users\imaad\Downloads\Book_text_Extraction\books"
    process_books_folder(books_folder)

if __name__ == "__main__":
    main()