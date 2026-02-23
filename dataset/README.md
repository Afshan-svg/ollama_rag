# 📘 NCERT Educational Question-Answering Dataset

This dataset is a curated collection of question-answer pairs derived from **NCERT** (National Council of Educational Research and Training) textbooks used in Indian schools. It includes English and Science content for Classes **6, 7, and 8**, structured to support NLP research in **education**, **question answering**, **reading comprehension**, and **automated tutoring systems**.

## � Research & Code
- **📜 Paper**: [Pustak AI: Curriculum-Aligned and Interactive Textbooks Using Large Language Models](https://arxiv.org/html/2511.10002v2)
- **💻 Benchmarking Code**: [EvalLab Repository](https://github.com/theshivam7/EvalLab)
- **🤗 Hugging Face Dataset**: [ncert-dataset](https://huggingface.co/datasets/theshivam7/ncert-dataset)

## �👥 Authors

- [Shivam Sharma](https://www.linkedin.com/in/theshivam7/) (IIT Madras)
- [Riya Naik](https://www.linkedin.com/in/riya-naik-279660108/) (BITS Pilani)
- [Tejas Gawas](https://www.linkedin.com/in/tejash-gawas/)
- [Heramb Patil](https://www.linkedin.com/in/herambvpatil/)
- [Prof. Kunal Kargaonkar](https://www.linkedin.com/in/kunal-korgaonkar-70171418/) (BITS Pilani)  

## 🧾 Dataset Summary

| Dataset                         | Subject        | Class | Questions | Chapters | Avg Questions/Chapter |
| ------------------------------- | -------------- | ----- | --------- | -------- | --------------------- |
| ncert-class6-english            | English        | 6     | \~144     | 8        | \~18                  |
| ncert-class7-english            | English        | 7     | \~181     | 8        | \~23                  |
| ncert-class8-english            | English        | 8     | \~126     | 8        | \~16                  |
| ncert-class6-8-english-combined | English        | 6–8   | \~451     | 24       | \~19                  |
| ncert-class6-science            | Science        | 6     | \~77      | 13       | \~6                   |
| ncert-class7-science            | Science        | 7     | \~108     | 13       | \~8                   |
| ncert-class8-science            | Science        | 8     | \~102     | 13       | \~7                   |
| ncert-class6-8-science-combined | Science        | 6–8   | \~288     | 39       | \~7                   |

## 🧬 Dataset Structure

Each record includes:

```json
{
  "context": "The Harappan civilization was one of the earliest urban societies in the world...",
  "question": "What is the Harappan civilization known for?",
  "answer": "It is known for being one of the earliest urban civilizations."
}
```

## 📊 Data Splits (Optional)
If your CSVs are split manually or programmatically, the following format applies:
| Split        | Description                    |
| ------------ | ------------------------------ |
| `train`      | Majority of the data (\~80%)   |
| `validation` | Evaluation tuning (\~10%)      |
| `test`       | Final model evaluation (\~10%) |

If you only provide full datasets, this section can be skipped in real hosting.

## 🛠️ Data Curation Process

1. Text Extraction from NCERT PDF textbooks using custom scripts.
2. Manual QA Curation to ensure pedagogical quality.
3. Contextual Mapping to maintain alignment between questions and source text.
4. Formatting in CSV files with standard columns: context, question, answer.
5. Validation & Deduplication for quality and uniqueness.

---

## 🔧 Usage Example

You can load the dataset using the Hugging Face Datasets library:

Install 🤗 Datasets:

```
pip install datasets
```

Load via:
from datasets import load_dataset

# Load a specific dataset
```
# Load English
ds = load_dataset("theshivam7/ncert-dataset", name="english")

# Load Science
ds = load_dataset("theshivam7/ncert-dataset", name="science")

# Load dummy test (for dev or testing)
ds = load_dataset("theshivam7/ncert-dataset", name="test")
```

## Potential Use Cases

1. 📖 Reading Comprehension Modeling
2. 🧠 Curriculum-Aware Tutoring Systems
3. ✍️ Automated Question Generation
4. 📊 Curriculum & Assessment Analytics
5. 📚 Content Summarization
6. 🌐 Language Learning Tools for Indian Classrooms

## License
This dataset is released under the Creative Commons Attribution 4.0 (CC BY 4.0) license. See the [LICENSE](https://huggingface.co/datasets/theshivam7/ncert-dataset/blob/main/LICENSE) file for more information.


## 📜 Citation
If you use the PustakAI dataset or results in your research, please cite our paper:

```bibtex
@article{pustakai2025,
  title={Pustak AI: Curriculum-Aligned and Interactive Textbooks Using Large Language Models},
  author={Shivam Sharma and Riya Naik and Tejas Gawas and Heramb Patil and Kunal Kargaonkar},
  journal={arXiv preprint arXiv:2511.10002v2},
  year={2025}
}
```
---
