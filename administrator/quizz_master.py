
""" 
Designed to read data from a pdf file and make given number of questions -
and their short answers
"""

import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer, pipeline
import json
import pdfplumber  # Extracts text better than PyPDF2
from sentence_transformers import SentenceTransformer, util

class QuestionAnswerProcessor:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.qg_model_name = "valhalla/t5-base-qg-hl"
        self.qa_model_name = "deepset/roberta-large-squad2"

        self.qg_model = T5ForConditionalGeneration.from_pretrained(self.qg_model_name).to(self.device)
        self.qg_tokenizer = T5Tokenizer.from_pretrained(self.qg_model_name, legacy=False)
        self.qa_pipeline = pipeline("question-answering", model=self.qa_model_name, device=0 if torch.cuda.is_available() else -1)
        self.sbert_model = SentenceTransformer('all-MiniLM-L6-v2')

    def extract_text_from_pdf(self, pdf_path):
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"

        text = text.replace("\n", " ").replace("  ", " ").strip()
        sentences = text.split(". ")
        chunks = []
        chunk = ""

        for sentence in sentences:
            if len(chunk) + len(sentence) < 1024:
                chunk += sentence + ". "
            else:
                chunks.append(chunk.strip())
                chunk = sentence + ". "

        if chunk:
            chunks.append(chunk.strip())

        return chunks, text

    def generate_questions(self, text, num_questions):
        inputs = f"highlight: {text} </s> generate questions:"
        input_ids = self.qg_tokenizer(inputs, return_tensors="pt", truncation=True, max_length=512).input_ids.to(self.device)

        output_ids = self.qg_model.generate(
            input_ids,
            max_length=64,
            num_return_sequences=num_questions,
            num_beams=5,
            do_sample=True,
            top_p=0.92,
            temperature=0.8
        )

        questions = [self.qg_tokenizer.decode(ids, skip_special_tokens=True) for ids in output_ids]
        return self.filter_similar_questions(questions, threshold=0.8)[:num_questions]

    def filter_similar_questions(self, questions, threshold=0.8):
        embeddings = self.sbert_model.encode(questions, convert_to_tensor=True)
        filtered_questions = []
        
        for i, q in enumerate(questions):
            if all(util.pytorch_cos_sim(embeddings[i], self.sbert_model.encode(fq)) < threshold for fq in filtered_questions):
                filtered_questions.append(q)

        return filtered_questions

    def answer_questions(self, full_text, questions):
        qa_dict = {}
        for q in questions:
            result = self.qa_pipeline(question=q, context=full_text)
            answer = result.get("answer", "None")

            if len(answer.strip()) < 2:
                answer = "None"

            qa_dict[q] = answer
        return qa_dict

    def process_pdf(self, pdf_path, total_questions):
        chunks, full_text = self.extract_text_from_pdf(pdf_path)
        num_chunks = len(chunks)

        if num_chunks == 0:
            return {}

        questions_per_chunk = total_questions // num_chunks
        extra_questions = total_questions % num_chunks

        questions = []
        for i, chunk in enumerate(chunks):
            num_qs = questions_per_chunk + (1 if i < extra_questions else 0)
            if num_qs > 0:
                questions.extend(self.generate_questions(chunk, num_qs))

        qa_dict = self.answer_questions(full_text, questions)
        return qa_dict



# # Stand-alon usage ------------------------
# if __name__ == "__main__":
#     processor = QuestionAnswerProcessor()
#     num_questions = 10
#     qa_data = processor.process_pdf("Introduction to Artificial Intelligence.pdf", num_questions)
#     print(json.dumps(qa_data, indent=4, ensure_ascii=False))
