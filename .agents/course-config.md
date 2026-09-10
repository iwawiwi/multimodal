# Course Configuration — Pembelajaran Mesin Multimodal

**This file is the single source of truth for course identity.** The global
`lecture-slide-designer` skill is course-agnostic; it reads this file to
substitute placeholders (`{{COURSE_CODE}}`, `{{COURSE_TITLE}}`, etc.) when
generating decks.

> When reusing the skill for another course, create a NEW `.agents/course-config.md`
> in that project with different values. Never edit the global skill.

---

## Identity

| Key | Value |
| :--- | :--- |
| Course code | `IF25-40304` |
| Course title | `Pembelajaran Mesin Multimodal` |
| SKS | `3 SKS` |
| Program study | `Program Studi Teknik Informatika` |
| Department | `Teknik Informatika ITERA` |
| Institution | `Institut Teknologi Sumatera (ITERA)` |
| Lecturer name | `I Wayan Wiprayoga Wisesa` |
| Lecturer email | `wayan.wisesa@if.itera.ac.id` |
| Campus logo (left) | `assets/img/logo_2.png` |
| Ministry logo (right) | `assets/img/dikti-saintek-berdampak-color.svg` |

## Placeholder mapping

These placeholders in `resources/slide-template.html` are substituted from this file:

| Placeholder | Value |
| :--- | :--- |
| `{{COURSE_CODE}}` | `IF25-40304` |
| `{{COURSE_TITLE}}` | `Pembelajaran Mesin Multimodal` |
| `{{DEPT}}` | `Teknik Informatika ITERA` |
| `{{INSTITUTION}}` | `Institut Teknologi Sumatera (ITERA)` |
| `{{PROGRAM_STUDY}}` | `Program Studi Teknik Informatika` |
| `{{LECTURER_NAME}}` | `I Wayan Wiprayoga Wisesa` |
| `{{LECTURER_EMAIL}}` | `wayan.wisesa@if.itera.ac.id` |
| `{{LOGO_CAMPUS}}` | `assets/img/logo_2.png` |
| `{{LOGO_MINISTRY}}` | `assets/img/dikti-saintek-berdampak-color.svg` |
| `{{WEEK_NUM}}` | meeting number (e.g. `1`, `2`) |
| `{{WEEK_NUM_2DIGIT}}` | zero-padded meeting number (e.g. `01`, `02`) |
| `{{TOPIC_TITLE}}` | meeting topic (e.g. `Representasi Modalitas I: Teks`) |

## Weekly topics (16 meetings)

`kind` column: `lecture` = regular weekly meeting; `milestone` = UTS/UAS exam (rendered as a separate `milestone-card` in `index.html`, NOT in the weeks grid).

| Week | Topic | Kind | Hands-on |
| :--- | :--- | :--- | :--- |
| 01 | Pengantar Pembelajaran Mesin Multimodal | lecture | — |
| 02 | Representasi Modalitas I: Teks | lecture | `Word Embeddings Lab` (`pdf/mgg02-hands-on.pdf`) |
| 03 | Representasi Modalitas II: Gambar | lecture | — |
| 04 | Representasi Modalitas III: Audio & Video | lecture | — |
| 05 | Fusion Strategies I: Early & Late Fusion | lecture | — |
| 06 | Fusion Strategies II: Intermediate & Cross-Attention | lecture | — |
| 07 | Alignment: Temporal & Structural | lecture | — |
| 08 | UTS | milestone | — |
| 09 | Vision-Language Models: CLIP & Contrastive Learning | lecture | — |
| 10 | Visual Question Answering (VQA) | lecture | — |
| 11 | Image Captioning & Text-to-Image Generation | lecture | — |
| 12 | Audio-Visual Learning & Speech-Vision | lecture | — |
| 13 | Multimodal Transformers & Cross-Attention | lecture | — |
| 14 | Bias, Hallucination & Ethical Paradigms | lecture | — |
| 15 | Green AI & Missing Modality Fallback | lecture | — |
| 16 | UAS | milestone | — |
