# TODO - Dashboard SaaS Wisata Analytics (Streamlit)

## Rencana Implementasi
- [x] Audit ulang requirement & mapping kolom dataset (`place`, `rating`, `comment`) + buat `clean_comment` dan `sentiment`.
- [ ] Replace UI: Sidebar premium (bg #0F172A, width 280-300px), header putih + shadow.
- [ ] Implement filter premium:


  - [ ] Tempat Wisata: searchable selectbox (streamlit-antd-components) (tanpa multiselect default)
  - [ ] Rating: checkbox horizontal ☑ 5..1 (no default merah)
  - [ ] Sentimen: segmented button (Semua/Positif/Negatif)
  - [ ] Search komentar dengan icon.
- [ ] KPI Cards: 5 card (warna sesuai spec) + mini sparkline di bagian bawah tiap card.
- [ ] Navigation: streamlit-option-menu dengan styling active/hover sesuai.
- [ ] Halaman Ringkasan: Bento grid + Plotly (zoom/hover/download PNG/autosize/responsive).
- [ ] Halaman Rating: Plotly bar chart interaktif, sorting, hover, download.
- [ ] Halaman WordCloud: card putih rounded + WordCloud + Top 20 kata.
- [ ] Halaman Sentimen: donut + bar + metric cards (Accuracy/Precision/Recall/F1 bila ada y_true/y_pred).
- [ ] Halaman SNA: network graph interaktif + tabel Top 10 node berpengaruh.
- [ ] Halaman Dataset: ganti `st.dataframe` -> `st.data_editor` + search + pagination + download CSV/Excel.
- [ ] Perapihan CSS: font Inter/Poppins, card hover transition, border warna spec.
- [ ] Run & test: `streamlit run atms_.py`.

## Catatan
- Semua perubahan dilakukan di `atms_.py`.

