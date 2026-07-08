# TODO Dashboard SaaS Wisata Analytics (Streamlit)

## Status: Not started

## Steps
1. Audit `atms_.py` (CSS, header, sidebar, navigation).
2. Ubah styling header menjadi putih + shadow tipis.
3. Pastikan sidebar width ~280-300px, warna premium (#0F172A) dan struktur filter rapi.
4. Rework halaman **Ringkasan** jadi Bento Grid:
   - Row 1: Rating chart + Donut chart
   - Row 2: WordCloud card putih + Sentimen donut
   - Row 3: Top Tempat Berdasarkan Review (horizontal bar full width)
5. Set konfigurasi Plotly agar interaktif sesuai spec:
   - responsive/autosize
   - hover rapi
   - tombol download PNG aktif
6. KPI cards: pastikan rounded 20px, warna sesuai, sparkline ikut rapi.
7. Halaman Dataset: ganti `st.dataframe` -> `st.data_editor` + search/pagination (manual bila perlu).
8. Run test: `streamlit run atms_.py` dan cek tiap tab.

## Done log
- [x] Step 1
- [ ] Step 2
- [ ] Step 3
- [ ] Step 4
- [ ] Step 5
- [ ] Step 6
- [ ] Step 7
- [ ] Step 8


