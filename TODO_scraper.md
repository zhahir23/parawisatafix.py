# TODO - Upgrade Scraper Google Maps (wisata)

## Sudah dilakukan
- [x] Naikkan `TARGET_REVIEWS_PER_PLACE` (10 → 25)
- [x] Ganti scroll: auto-scroll sampai jumlah review berhenti bertambah (lazy loading)
- [x] Tambah retry untuk `page.goto` (3x)
- [x] Tambah batas `MAX_SCROLL_ITER` dan `MAX_EXPAND_MORE_PER_PLACE`

## Masih perlu dilakukan
- [ ] Tambah fitur resume (state JSON) agar kalau terhenti bisa lanjut
- [ ] Anti-duplicate lebih kuat (hash based)
- [ ] Perluas `TEMPAT_WISATA` menjadi 60–80 tempat
- [ ] Validasi selector review/comment/rating agar lebih stabil
- [ ] Uji run skala kecil (mis. 5 tempat, target 50–100)

## Reminder implementasi
- Output CSV harus tetap kolom: `place,rating,comment,clean_comment,label,cluster`

