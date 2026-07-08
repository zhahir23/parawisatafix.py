# -*- coding: utf-8 -*-
"""Dashboard Analisis Tempat Wisata - Google Maps Review Analytics"""

import io
import re
from collections import Counter
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from wordcloud import WordCloud

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Analisis Tempat Wisata",
    layout="wide",
    page_icon="🌄",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# EMBEDDED DATASET  (300 rows, no external file needed)
# ─────────────────────────────────────────────
_COLUMNS = ["place", "rating", "comment", "sentiment", "clean_comment"]
_DATA = [
    ("Nusa Penida",5,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Gili Trawangan",5,"Bersih dan terawat dengan baik, petugas sangat ramah dan helpful.","Positif","bersih dan terawat dengan baik petugas sangat ramah dan helpful"),
    ("Pantai Parangtritis",5,"Air laut jernih dan biru, pasir putih bersih, sangat indah.","Positif","air laut jernih dan biru pasir putih bersih sangat indah"),
    ("Pantai Kuta Bali",5,"Pengalaman seru dan menakjubkan, pemandangan alam yang cantik.","Positif","pengalaman seru dan menakjubkan pemandangan alam yang cantik"),
    ("Pantai Derawan",4,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Taman Laut Bunaken",5,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Gunung Rinjani",3,"Lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya.","Netral","lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya"),
    ("Taman Mini Indonesia Indah",5,"Suasana alam sangat asri dan sejuk, keluarga sangat menikmati.","Positif","suasana alam sangat asri dan sejuk keluarga sangat menikmati"),
    ("Pantai Kuta Bali",5,"Suasana alam sangat asri dan sejuk, keluarga sangat menikmati.","Positif","suasana alam sangat asri dan sejuk keluarga sangat menikmati"),
    ("Kepulauan Seribu",5,"Destinasi wisata yang wajib dikunjungi, pemandangan memukau.","Positif","destinasi wisata yang wajib dikunjungi pemandangan memukau"),
    ("Pantai Derawan",3,"Cukup menarik, meski ada beberapa kekurangan di fasilitas.","Netral","cukup menarik meski ada beberapa kekurangan di fasilitas"),
    ("Kawah Ijen",4,"Wisata terbaik yang pernah saya kunjungi, sangat direkomendasikan.","Positif","wisata terbaik yang pernah saya kunjungi sangat direkomendasikan"),
    ("Pantai Pink Lombok",4,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Prambanan Temple",4,"Bersih dan terawat dengan baik, petugas sangat ramah dan helpful.","Positif","bersih dan terawat dengan baik petugas sangat ramah dan helpful"),
    ("Pantai Senggigi",5,"Tempat yang sangat indah dan memukau! Pemandangannya luar biasa.","Positif","tempat yang sangat indah dan memukau pemandangannya luar biasa"),
    ("Taman Laut Bunaken",5,"Suasana alam sangat asri dan sejuk, keluarga sangat menikmati.","Positif","suasana alam sangat asri dan sejuk keluarga sangat menikmati"),
    ("Air Terjun Gitgit",4,"Fasilitas lengkap dan nyaman, sangat cocok untuk keluarga.","Positif","fasilitas lengkap dan nyaman sangat cocok untuk keluarga"),
    ("Pantai Pink Lombok",3,"Pemandangan bagus tapi terlalu ramai di akhir pekan.","Netral","pemandangan bagus tapi terlalu ramai di akhir pekan"),
    ("Istana Maimun",3,"Tempat cukup oke, ada beberapa fasilitas yang perlu diperbaiki.","Netral","tempat cukup oke ada beberapa fasilitas yang perlu diperbaiki"),
    ("Goa Pindul",4,"Wisata alam terbaik, cocok untuk liburan keluarga dan anak-anak.","Positif","wisata alam terbaik cocok untuk liburan keluarga dan anak-anak"),
    ("Raja Ampat",3,"Lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya.","Netral","lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya"),
    ("Ancol Dreamland",3,"Tempat cukup oke, ada beberapa fasilitas yang perlu diperbaiki.","Netral","tempat cukup oke ada beberapa fasilitas yang perlu diperbaiki"),
    ("Kebun Raya Bogor",5,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Pura Besakih",5,"Bersih dan terawat dengan baik, petugas sangat ramah dan helpful.","Positif","bersih dan terawat dengan baik petugas sangat ramah dan helpful"),
    ("Taman Mini Indonesia Indah",5,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Prambanan Temple",3,"Standar wisata pada umumnya, tidak ada yang spesial.","Netral","standar wisata pada umumnya tidak ada yang spesial"),
    ("Air Terjun Gitgit",4,"Tempat yang sangat indah dan memukau! Pemandangannya luar biasa.","Positif","tempat yang sangat indah dan memukau pemandangannya luar biasa"),
    ("Pantai Jimbaran",5,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Pantai Parangtritis",5,"Bersih dan terawat dengan baik, petugas sangat ramah dan helpful.","Positif","bersih dan terawat dengan baik petugas sangat ramah dan helpful"),
    ("Pantai Derawan",4,"Pengalaman seru dan menakjubkan, pemandangan alam yang cantik.","Positif","pengalaman seru dan menakjubkan pemandangan alam yang cantik"),
    ("Tanah Lot Bali",5,"Bersih dan terawat dengan baik, petugas sangat ramah dan helpful.","Positif","bersih dan terawat dengan baik petugas sangat ramah dan helpful"),
    ("Goa Pindul",4,"Wisata terbaik yang pernah saya kunjungi, sangat direkomendasikan.","Positif","wisata terbaik yang pernah saya kunjungi sangat direkomendasikan"),
    ("Borobudur Temple",4,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Ubud Monkey Forest",5,"Suasana alam sangat asri dan sejuk, keluarga sangat menikmati.","Positif","suasana alam sangat asri dan sejuk keluarga sangat menikmati"),
    ("Pantai Pink Lombok",4,"Tempat yang sangat indah dan memukau! Pemandangannya luar biasa.","Positif","tempat yang sangat indah dan memukau pemandangannya luar biasa"),
    ("Ancol Dreamland",5,"Destinasi wisata yang wajib dikunjungi, pemandangan memukau.","Positif","destinasi wisata yang wajib dikunjungi pemandangan memukau"),
    ("Pantai Kuta Bali",4,"Destinasi wisata yang wajib dikunjungi, pemandangan memukau.","Positif","destinasi wisata yang wajib dikunjungi pemandangan memukau"),
    ("Labuan Bajo",5,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Prambanan Temple",5,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Raja Ampat",5,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Labuan Bajo",5,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Raja Ampat",5,"Destinasi wisata yang wajib dikunjungi, pemandangan memukau.","Positif","destinasi wisata yang wajib dikunjungi pemandangan memukau"),
    ("Air Terjun Gitgit",3,"Cukup menarik, meski ada beberapa kekurangan di fasilitas.","Netral","cukup menarik meski ada beberapa kekurangan di fasilitas"),
    ("Bromo Tengger Semeru",3,"Tempat cukup oke, ada beberapa fasilitas yang perlu diperbaiki.","Netral","tempat cukup oke ada beberapa fasilitas yang perlu diperbaiki"),
    ("Raja Ampat",1,"Fasilitas toilet kurang bersih dan tidak terawat dengan baik.","Negatif","fasilitas toilet kurang bersih dan tidak terawat dengan baik"),
    ("Bromo Tengger Semeru",5,"Destinasi wisata yang wajib dikunjungi, pemandangan memukau.","Positif","destinasi wisata yang wajib dikunjungi pemandangan memukau"),
    ("Pantai Derawan",3,"Lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya.","Netral","lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya"),
    ("Taman Laut Bunaken",4,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Ancol Dreamland",5,"Pengalaman seru dan menakjubkan, pemandangan alam yang cantik.","Positif","pengalaman seru dan menakjubkan pemandangan alam yang cantik"),
    ("Pantai Derawan",4,"Destinasi wisata yang wajib dikunjungi, pemandangan memukau.","Positif","destinasi wisata yang wajib dikunjungi pemandangan memukau"),
    ("Pantai Senggigi",5,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Istana Maimun",5,"Wisata alam terbaik, cocok untuk liburan keluarga dan anak-anak.","Positif","wisata alam terbaik cocok untuk liburan keluarga dan anak-anak"),
    ("Pantai Derawan",5,"Air laut jernih dan biru, pasir putih bersih, sangat indah.","Positif","air laut jernih dan biru pasir putih bersih sangat indah"),
    ("Raja Ampat",4,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Pantai Jimbaran",5,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Lembah Harau",4,"Wisata terbaik yang pernah saya kunjungi, sangat direkomendasikan.","Positif","wisata terbaik yang pernah saya kunjungi sangat direkomendasikan"),
    ("Labuan Bajo",3,"Lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya.","Netral","lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya"),
    ("Labuan Bajo",4,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Gunung Rinjani",5,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Ubud Monkey Forest",4,"Bersih dan terawat dengan baik, petugas sangat ramah dan helpful.","Positif","bersih dan terawat dengan baik petugas sangat ramah dan helpful"),
    ("Pantai Derawan",5,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Kawah Ijen",1,"Fasilitas toilet kurang bersih dan tidak terawat dengan baik.","Negatif","fasilitas toilet kurang bersih dan tidak terawat dengan baik"),
    ("Pantai Kuta Bali",4,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Pantai Senggigi",5,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Kepulauan Seribu",5,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Borobudur Temple",5,"Wisata terbaik yang pernah saya kunjungi, sangat direkomendasikan.","Positif","wisata terbaik yang pernah saya kunjungi sangat direkomendasikan"),
    ("Ubud Monkey Forest",4,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Pura Besakih",3,"Lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya.","Netral","lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya"),
    ("Kawah Ijen",5,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Pantai Senggigi",5,"Tempat yang sangat indah dan memukau! Pemandangannya luar biasa.","Positif","tempat yang sangat indah dan memukau pemandangannya luar biasa"),
    ("Taman Mini Indonesia Indah",4,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Taman Nasional Ujung Kulon",4,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Pantai Derawan",5,"Pengalaman tak terlupakan, pasti akan kembali lagi ke sini.","Positif","pengalaman tak terlupakan pasti akan kembali lagi ke sini"),
    ("Gunung Rinjani",4,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Taman Nasional Ujung Kulon",3,"Cukup menarik, meski ada beberapa kekurangan di fasilitas.","Netral","cukup menarik meski ada beberapa kekurangan di fasilitas"),
    ("Air Terjun Gitgit",5,"Tempat yang sangat indah dan memukau! Pemandangannya luar biasa.","Positif","tempat yang sangat indah dan memukau pemandangannya luar biasa"),
    ("Komodo National Park",1,"Fasilitas toilet kurang bersih dan tidak terawat dengan baik.","Negatif","fasilitas toilet kurang bersih dan tidak terawat dengan baik"),
    ("Komodo National Park",4,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Bromo Tengger Semeru",4,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Air Terjun Gitgit",4,"Destinasi wisata yang wajib dikunjungi, pemandangan memukau.","Positif","destinasi wisata yang wajib dikunjungi pemandangan memukau"),
    ("Goa Pindul",4,"Lokasi mudah dijangkau, parkir luas, tempat sangat terawat.","Positif","lokasi mudah dijangkau parkir luas tempat sangat terawat"),
    ("Pantai Parangtritis",4,"Pengalaman seru dan menakjubkan, pemandangan alam yang cantik.","Positif","pengalaman seru dan menakjubkan pemandangan alam yang cantik"),
    ("Tanah Lot Bali",1,"Harga tiket terlalu mahal tidak sebanding dengan fasilitasnya.","Negatif","harga tiket terlalu mahal tidak sebanding dengan fasilitasnya"),
    ("Taman Nasional Ujung Kulon",4,"Bersih dan terawat dengan baik, petugas sangat ramah dan helpful.","Positif","bersih dan terawat dengan baik petugas sangat ramah dan helpful"),
    ("Raja Ampat",5,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Ancol Dreamland",4,"Suasana alam sangat asri dan sejuk, keluarga sangat menikmati.","Positif","suasana alam sangat asri dan sejuk keluarga sangat menikmati"),
    ("Ancol Dreamland",3,"Cukup menarik, meski ada beberapa kekurangan di fasilitas.","Netral","cukup menarik meski ada beberapa kekurangan di fasilitas"),
    ("Raja Ampat",4,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Tanah Lot Bali",4,"Wisata alam terbaik, cocok untuk liburan keluarga dan anak-anak.","Positif","wisata alam terbaik cocok untuk liburan keluarga dan anak-anak"),
    ("Tanah Lot Bali",3,"Standar wisata pada umumnya, tidak ada yang spesial.","Netral","standar wisata pada umumnya tidak ada yang spesial"),
    ("Gunung Rinjani",4,"Destinasi wisata yang wajib dikunjungi, pemandangan memukau.","Positif","destinasi wisata yang wajib dikunjungi pemandangan memukau"),
    ("Taman Mini Indonesia Indah",3,"Pemandangan bagus tapi terlalu ramai di akhir pekan.","Netral","pemandangan bagus tapi terlalu ramai di akhir pekan"),
    ("Bromo Tengger Semeru",3,"Lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya.","Netral","lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya"),
    ("Taman Laut Bunaken",3,"Standar wisata pada umumnya, tidak ada yang spesial.","Netral","standar wisata pada umumnya tidak ada yang spesial"),
    ("Borobudur Temple",5,"Suasana alam sangat asri dan sejuk, keluarga sangat menikmati.","Positif","suasana alam sangat asri dan sejuk keluarga sangat menikmati"),
    ("Tanah Lot Bali",5,"Pengalaman seru dan menakjubkan, pemandangan alam yang cantik.","Positif","pengalaman seru dan menakjubkan pemandangan alam yang cantik"),
    ("Kepulauan Seribu",4,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Istana Maimun",5,"Suasana alam sangat asri dan sejuk, keluarga sangat menikmati.","Positif","suasana alam sangat asri dan sejuk keluarga sangat menikmati"),
    ("Lembah Harau",4,"Pengalaman tak terlupakan, pasti akan kembali lagi ke sini.","Positif","pengalaman tak terlupakan pasti akan kembali lagi ke sini"),
    ("Bromo Tengger Semeru",4,"Destinasi wisata yang wajib dikunjungi, pemandangan memukau.","Positif","destinasi wisata yang wajib dikunjungi pemandangan memukau"),
    ("Taman Laut Bunaken",4,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Bromo Tengger Semeru",4,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Borobudur Temple",4,"Destinasi wisata yang wajib dikunjungi, pemandangan memukau.","Positif","destinasi wisata yang wajib dikunjungi pemandangan memukau"),
    ("Pantai Senggigi",4,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Gili Trawangan",4,"Air laut jernih dan biru, pasir putih bersih, sangat indah.","Positif","air laut jernih dan biru pasir putih bersih sangat indah"),
    ("Taman Laut Bunaken",5,"Fasilitas lengkap dan nyaman, sangat cocok untuk keluarga.","Positif","fasilitas lengkap dan nyaman sangat cocok untuk keluarga"),
    ("Istana Maimun",5,"Suasana alam sangat asri dan sejuk, keluarga sangat menikmati.","Positif","suasana alam sangat asri dan sejuk keluarga sangat menikmati"),
    ("Tanah Lot Bali",4,"Fasilitas lengkap dan nyaman, sangat cocok untuk keluarga.","Positif","fasilitas lengkap dan nyaman sangat cocok untuk keluarga"),
    ("Pantai Senggigi",3,"Cukup menarik, meski ada beberapa kekurangan di fasilitas.","Netral","cukup menarik meski ada beberapa kekurangan di fasilitas"),
    ("Labuan Bajo",5,"Destinasi wisata yang wajib dikunjungi, pemandangan memukau.","Positif","destinasi wisata yang wajib dikunjungi pemandangan memukau"),
    ("Danau Toba",5,"Suasana alam sangat asri dan sejuk, keluarga sangat menikmati.","Positif","suasana alam sangat asri dan sejuk keluarga sangat menikmati"),
    ("Gili Trawangan",5,"Pengalaman tak terlupakan, pasti akan kembali lagi ke sini.","Positif","pengalaman tak terlupakan pasti akan kembali lagi ke sini"),
    ("Komodo National Park",4,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Kebun Raya Bogor",5,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Kebun Raya Bogor",4,"Lokasi mudah dijangkau, parkir luas, tempat sangat terawat.","Positif","lokasi mudah dijangkau parkir luas tempat sangat terawat"),
    ("Ancol Dreamland",3,"Tempat cukup oke, ada beberapa fasilitas yang perlu diperbaiki.","Netral","tempat cukup oke ada beberapa fasilitas yang perlu diperbaiki"),
    ("Istana Maimun",4,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Pantai Jimbaran",4,"Suasana alam sangat asri dan sejuk, keluarga sangat menikmati.","Positif","suasana alam sangat asri dan sejuk keluarga sangat menikmati"),
    ("Gunung Rinjani",3,"Cukup menarik, meski ada beberapa kekurangan di fasilitas.","Netral","cukup menarik meski ada beberapa kekurangan di fasilitas"),
    ("Nusa Penida",4,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Kawah Ijen",5,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Kepulauan Seribu",5,"Air laut jernih dan biru, pasir putih bersih, sangat indah.","Positif","air laut jernih dan biru pasir putih bersih sangat indah"),
    ("Pantai Senggigi",4,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Goa Pindul",4,"Wisata alam terbaik, cocok untuk liburan keluarga dan anak-anak.","Positif","wisata alam terbaik cocok untuk liburan keluarga dan anak-anak"),
    ("Danau Toba",3,"Pemandangan bagus tapi terlalu ramai di akhir pekan.","Netral","pemandangan bagus tapi terlalu ramai di akhir pekan"),
    ("Pura Besakih",4,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Borobudur Temple",4,"Wisata terbaik yang pernah saya kunjungi, sangat direkomendasikan.","Positif","wisata terbaik yang pernah saya kunjungi sangat direkomendasikan"),
    ("Taman Nasional Ujung Kulon",3,"Lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya.","Netral","lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya"),
    ("Gunung Rinjani",4,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Air Terjun Gitgit",4,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Danau Toba",4,"Air laut jernih dan biru, pasir putih bersih, sangat indah.","Positif","air laut jernih dan biru pasir putih bersih sangat indah"),
    ("Ancol Dreamland",5,"Air laut jernih dan biru, pasir putih bersih, sangat indah.","Positif","air laut jernih dan biru pasir putih bersih sangat indah"),
    ("Goa Pindul",4,"Tempat yang sangat indah dan memukau! Pemandangannya luar biasa.","Positif","tempat yang sangat indah dan memukau pemandangannya luar biasa"),
    ("Ancol Dreamland",4,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Lembah Harau",4,"Destinasi wisata yang wajib dikunjungi, pemandangan memukau.","Positif","destinasi wisata yang wajib dikunjungi pemandangan memukau"),
    ("Lembah Harau",4,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Pantai Parangtritis",3,"Pemandangan bagus tapi terlalu ramai di akhir pekan.","Netral","pemandangan bagus tapi terlalu ramai di akhir pekan"),
    ("Kepulauan Seribu",5,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Kepulauan Seribu",4,"Bersih dan terawat dengan baik, petugas sangat ramah dan helpful.","Positif","bersih dan terawat dengan baik petugas sangat ramah dan helpful"),
    ("Pantai Kuta Bali",4,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Ancol Dreamland",3,"Lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya.","Netral","lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya"),
    ("Istana Maimun",3,"Tempat cukup oke, ada beberapa fasilitas yang perlu diperbaiki.","Netral","tempat cukup oke ada beberapa fasilitas yang perlu diperbaiki"),
    ("Kepulauan Seribu",4,"Pengalaman seru dan menakjubkan, pemandangan alam yang cantik.","Positif","pengalaman seru dan menakjubkan pemandangan alam yang cantik"),
    ("Taman Nasional Ujung Kulon",5,"Pengalaman seru dan menakjubkan, pemandangan alam yang cantik.","Positif","pengalaman seru dan menakjubkan pemandangan alam yang cantik"),
    ("Pantai Pink Lombok",5,"Lokasi mudah dijangkau, parkir luas, tempat sangat terawat.","Positif","lokasi mudah dijangkau parkir luas tempat sangat terawat"),
    ("Gili Trawangan",5,"Wisata alam terbaik, cocok untuk liburan keluarga dan anak-anak.","Positif","wisata alam terbaik cocok untuk liburan keluarga dan anak-anak"),
    ("Taman Nasional Ujung Kulon",4,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Raja Ampat",5,"Lokasi mudah dijangkau, parkir luas, tempat sangat terawat.","Positif","lokasi mudah dijangkau parkir luas tempat sangat terawat"),
    ("Ubud Monkey Forest",4,"Tempat yang sangat indah dan memukau! Pemandangannya luar biasa.","Positif","tempat yang sangat indah dan memukau pemandangannya luar biasa"),
    ("Komodo National Park",2,"Terlalu ramai dan padat, tidak bisa menikmati suasana dengan tenang.","Negatif","terlalu ramai dan padat tidak bisa menikmati suasana dengan tenang"),
    ("Gili Trawangan",4,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Taman Mini Indonesia Indah",5,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Taman Laut Bunaken",4,"Suasana alam sangat asri dan sejuk, keluarga sangat menikmati.","Positif","suasana alam sangat asri dan sejuk keluarga sangat menikmati"),
    ("Pantai Parangtritis",5,"Tempat yang sangat indah dan memukau! Pemandangannya luar biasa.","Positif","tempat yang sangat indah dan memukau pemandangannya luar biasa"),
    ("Air Terjun Gitgit",5,"Pengalaman tak terlupakan, pasti akan kembali lagi ke sini.","Positif","pengalaman tak terlupakan pasti akan kembali lagi ke sini"),
    ("Kebun Raya Bogor",5,"Fasilitas lengkap dan nyaman, sangat cocok untuk keluarga.","Positif","fasilitas lengkap dan nyaman sangat cocok untuk keluarga"),
    ("Taman Laut Bunaken",4,"Lokasi mudah dijangkau, parkir luas, tempat sangat terawat.","Positif","lokasi mudah dijangkau parkir luas tempat sangat terawat"),
    ("Bromo Tengger Semeru",4,"Suasana alam sangat asri dan sejuk, keluarga sangat menikmati.","Positif","suasana alam sangat asri dan sejuk keluarga sangat menikmati"),
    ("Gunung Rinjani",4,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Komodo National Park",3,"Cukup menarik, meski ada beberapa kekurangan di fasilitas.","Netral","cukup menarik meski ada beberapa kekurangan di fasilitas"),
    ("Pantai Pink Lombok",5,"Tempat yang sangat indah dan memukau! Pemandangannya luar biasa.","Positif","tempat yang sangat indah dan memukau pemandangannya luar biasa"),
    ("Pantai Parangtritis",5,"Lokasi mudah dijangkau, parkir luas, tempat sangat terawat.","Positif","lokasi mudah dijangkau parkir luas tempat sangat terawat"),
    ("Tanah Lot Bali",3,"Cukup menarik, meski ada beberapa kekurangan di fasilitas.","Netral","cukup menarik meski ada beberapa kekurangan di fasilitas"),
    ("Borobudur Temple",4,"Suasana alam sangat asri dan sejuk, keluarga sangat menikmati.","Positif","suasana alam sangat asri dan sejuk keluarga sangat menikmati"),
    ("Ubud Monkey Forest",1,"Parkir sempit dan jauh dari lokasi wisata, tidak nyaman.","Negatif","parkir sempit dan jauh dari lokasi wisata tidak nyaman"),
    ("Istana Maimun",1,"Kurang informasi dan petunjuk arah di lokasi wisata ini.","Negatif","kurang informasi dan petunjuk arah di lokasi wisata ini"),
    ("Air Terjun Gitgit",4,"Air laut jernih dan biru, pasir putih bersih, sangat indah.","Positif","air laut jernih dan biru pasir putih bersih sangat indah"),
    ("Pura Besakih",5,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Kepulauan Seribu",3,"Tempat cukup oke, ada beberapa fasilitas yang perlu diperbaiki.","Netral","tempat cukup oke ada beberapa fasilitas yang perlu diperbaiki"),
    ("Kawah Ijen",4,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Labuan Bajo",3,"Cukup menarik, meski ada beberapa kekurangan di fasilitas.","Netral","cukup menarik meski ada beberapa kekurangan di fasilitas"),
    ("Nusa Penida",3,"Pemandangan bagus tapi terlalu ramai di akhir pekan.","Netral","pemandangan bagus tapi terlalu ramai di akhir pekan"),
    ("Kebun Raya Bogor",4,"Fasilitas lengkap dan nyaman, sangat cocok untuk keluarga.","Positif","fasilitas lengkap dan nyaman sangat cocok untuk keluarga"),
    ("Prambanan Temple",4,"Lokasi mudah dijangkau, parkir luas, tempat sangat terawat.","Positif","lokasi mudah dijangkau parkir luas tempat sangat terawat"),
    ("Komodo National Park",4,"Tempat yang sangat indah dan memukau! Pemandangannya luar biasa.","Positif","tempat yang sangat indah dan memukau pemandangannya luar biasa"),
    ("Kebun Raya Bogor",5,"Pengalaman tak terlupakan, pasti akan kembali lagi ke sini.","Positif","pengalaman tak terlupakan pasti akan kembali lagi ke sini"),
    ("Danau Toba",5,"Destinasi wisata yang wajib dikunjungi, pemandangan memukau.","Positif","destinasi wisata yang wajib dikunjungi pemandangan memukau"),
    ("Ubud Monkey Forest",5,"Bersih dan terawat dengan baik, petugas sangat ramah dan helpful.","Positif","bersih dan terawat dengan baik petugas sangat ramah dan helpful"),
    ("Pantai Jimbaran",3,"Lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya.","Netral","lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya"),
    ("Istana Maimun",4,"Pengalaman tak terlupakan, pasti akan kembali lagi ke sini.","Positif","pengalaman tak terlupakan pasti akan kembali lagi ke sini"),
    ("Nusa Penida",4,"Wisata alam terbaik, cocok untuk liburan keluarga dan anak-anak.","Positif","wisata alam terbaik cocok untuk liburan keluarga dan anak-anak"),
    ("Pantai Kuta Bali",5,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Gili Trawangan",5,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Lembah Harau",5,"Tempat yang sangat indah dan memukau! Pemandangannya luar biasa.","Positif","tempat yang sangat indah dan memukau pemandangannya luar biasa"),
    ("Taman Mini Indonesia Indah",3,"Lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya.","Netral","lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya"),
    ("Pura Besakih",3,"Cukup menarik, meski ada beberapa kekurangan di fasilitas.","Netral","cukup menarik meski ada beberapa kekurangan di fasilitas"),
    ("Pura Besakih",3,"Standar wisata pada umumnya, tidak ada yang spesial.","Netral","standar wisata pada umumnya tidak ada yang spesial"),
    ("Kepulauan Seribu",4,"Destinasi wisata yang wajib dikunjungi, pemandangan memukau.","Positif","destinasi wisata yang wajib dikunjungi pemandangan memukau"),
    ("Labuan Bajo",5,"Air laut jernih dan biru, pasir putih bersih, sangat indah.","Positif","air laut jernih dan biru pasir putih bersih sangat indah"),
    ("Borobudur Temple",5,"Fasilitas lengkap dan nyaman, sangat cocok untuk keluarga.","Positif","fasilitas lengkap dan nyaman sangat cocok untuk keluarga"),
    ("Bromo Tengger Semeru",5,"Air laut jernih dan biru, pasir putih bersih, sangat indah.","Positif","air laut jernih dan biru pasir putih bersih sangat indah"),
    ("Pantai Parangtritis",1,"Sampah berserakan di mana-mana, pengelolaan kebersihan kurang baik.","Negatif","sampah berserakan di mana-mana pengelolaan kebersihan kurang baik"),
    ("Pantai Derawan",5,"Fasilitas lengkap dan nyaman, sangat cocok untuk keluarga.","Positif","fasilitas lengkap dan nyaman sangat cocok untuk keluarga"),
    ("Nusa Penida",5,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Kebun Raya Bogor",4,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Tanah Lot Bali",3,"Pemandangan bagus tapi terlalu ramai di akhir pekan.","Netral","pemandangan bagus tapi terlalu ramai di akhir pekan"),
    ("Pantai Jimbaran",4,"Air laut jernih dan biru, pasir putih bersih, sangat indah.","Positif","air laut jernih dan biru pasir putih bersih sangat indah"),
    ("Gili Trawangan",4,"Wisata terbaik yang pernah saya kunjungi, sangat direkomendasikan.","Positif","wisata terbaik yang pernah saya kunjungi sangat direkomendasikan"),
    ("Ubud Monkey Forest",5,"Wisata terbaik yang pernah saya kunjungi, sangat direkomendasikan.","Positif","wisata terbaik yang pernah saya kunjungi sangat direkomendasikan"),
    ("Pantai Pink Lombok",5,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Pantai Kuta Bali",3,"Tempat cukup oke, ada beberapa fasilitas yang perlu diperbaiki.","Netral","tempat cukup oke ada beberapa fasilitas yang perlu diperbaiki"),
    ("Taman Nasional Ujung Kulon",4,"Pengalaman seru dan menakjubkan, pemandangan alam yang cantik.","Positif","pengalaman seru dan menakjubkan pemandangan alam yang cantik"),
    ("Borobudur Temple",4,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Nusa Penida",5,"Wisata terbaik yang pernah saya kunjungi, sangat direkomendasikan.","Positif","wisata terbaik yang pernah saya kunjungi sangat direkomendasikan"),
    ("Goa Pindul",5,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Nusa Penida",5,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Air Terjun Gitgit",4,"Pengalaman seru dan menakjubkan, pemandangan alam yang cantik.","Positif","pengalaman seru dan menakjubkan pemandangan alam yang cantik"),
    ("Danau Toba",5,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Bromo Tengger Semeru",5,"Air laut jernih dan biru, pasir putih bersih, sangat indah.","Positif","air laut jernih dan biru pasir putih bersih sangat indah"),
    ("Danau Toba",5,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Taman Nasional Ujung Kulon",4,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Pantai Jimbaran",2,"Sampah berserakan di mana-mana, pengelolaan kebersihan kurang baik.","Negatif","sampah berserakan di mana-mana pengelolaan kebersihan kurang baik"),
    ("Pantai Kuta Bali",4,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Raja Ampat",5,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Gili Trawangan",4,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Bromo Tengger Semeru",5,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Prambanan Temple",3,"Pemandangan bagus tapi terlalu ramai di akhir pekan.","Netral","pemandangan bagus tapi terlalu ramai di akhir pekan"),
    ("Lembah Harau",2,"Terlalu ramai dan padat, tidak bisa menikmati suasana dengan tenang.","Negatif","terlalu ramai dan padat tidak bisa menikmati suasana dengan tenang"),
    ("Pantai Parangtritis",3,"Tempat cukup oke, ada beberapa fasilitas yang perlu diperbaiki.","Netral","tempat cukup oke ada beberapa fasilitas yang perlu diperbaiki"),
    ("Prambanan Temple",5,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Taman Nasional Ujung Kulon",5,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Lembah Harau",5,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Pantai Pink Lombok",5,"Wisata terbaik yang pernah saya kunjungi, sangat direkomendasikan.","Positif","wisata terbaik yang pernah saya kunjungi sangat direkomendasikan"),
    ("Pantai Parangtritis",3,"Lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya.","Netral","lumayan bagus tapi bisa lebih ditingkatkan lagi pengelolaannya"),
    ("Ubud Monkey Forest",5,"Tempat yang sangat indah dan memukau! Pemandangannya luar biasa.","Positif","tempat yang sangat indah dan memukau pemandangannya luar biasa"),
    ("Gili Trawangan",4,"Bersih dan terawat dengan baik, petugas sangat ramah dan helpful.","Positif","bersih dan terawat dengan baik petugas sangat ramah dan helpful"),
    ("Ancol Dreamland",5,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Komodo National Park",3,"Tempat cukup oke, ada beberapa fasilitas yang perlu diperbaiki.","Netral","tempat cukup oke ada beberapa fasilitas yang perlu diperbaiki"),
    ("Nusa Penida",4,"Destinasi wisata yang wajib dikunjungi, pemandangan memukau.","Positif","destinasi wisata yang wajib dikunjungi pemandangan memukau"),
    ("Pantai Pink Lombok",5,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Borobudur Temple",5,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Kebun Raya Bogor",4,"Bersih dan terawat dengan baik, petugas sangat ramah dan helpful.","Positif","bersih dan terawat dengan baik petugas sangat ramah dan helpful"),
    ("Pantai Jimbaran",4,"Destinasi wisata yang wajib dikunjungi, pemandangan memukau.","Positif","destinasi wisata yang wajib dikunjungi pemandangan memukau"),
    ("Pura Besakih",4,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Gunung Rinjani",5,"Wisata terbaik yang pernah saya kunjungi, sangat direkomendasikan.","Positif","wisata terbaik yang pernah saya kunjungi sangat direkomendasikan"),
    ("Tanah Lot Bali",3,"Tempat cukup oke, ada beberapa fasilitas yang perlu diperbaiki.","Netral","tempat cukup oke ada beberapa fasilitas yang perlu diperbaiki"),
    ("Prambanan Temple",5,"Pengalaman seru dan menakjubkan, pemandangan alam yang cantik.","Positif","pengalaman seru dan menakjubkan pemandangan alam yang cantik"),
    ("Labuan Bajo",5,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Gili Trawangan",5,"Suasana alam sangat asri dan sejuk, keluarga sangat menikmati.","Positif","suasana alam sangat asri dan sejuk keluarga sangat menikmati"),
    ("Taman Laut Bunaken",5,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Lembah Harau",4,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Nusa Penida",1,"Sampah berserakan di mana-mana, pengelolaan kebersihan kurang baik.","Negatif","sampah berserakan di mana-mana pengelolaan kebersihan kurang baik"),
    ("Goa Pindul",5,"Bersih dan terawat dengan baik, petugas sangat ramah dan helpful.","Positif","bersih dan terawat dengan baik petugas sangat ramah dan helpful"),
    ("Prambanan Temple",5,"Wisata alam terbaik, cocok untuk liburan keluarga dan anak-anak.","Positif","wisata alam terbaik cocok untuk liburan keluarga dan anak-anak"),
    ("Pantai Pink Lombok",4,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Istana Maimun",4,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Gunung Rinjani",5,"Pengalaman tak terlupakan, pasti akan kembali lagi ke sini.","Positif","pengalaman tak terlupakan pasti akan kembali lagi ke sini"),
    ("Taman Laut Bunaken",5,"Pengalaman tak terlupakan, pasti akan kembali lagi ke sini.","Positif","pengalaman tak terlupakan pasti akan kembali lagi ke sini"),
    ("Pura Besakih",4,"Pengalaman seru dan menakjubkan, pemandangan alam yang cantik.","Positif","pengalaman seru dan menakjubkan pemandangan alam yang cantik"),
    ("Pantai Kuta Bali",4,"Bersih dan terawat dengan baik, petugas sangat ramah dan helpful.","Positif","bersih dan terawat dengan baik petugas sangat ramah dan helpful"),
    ("Taman Mini Indonesia Indah",4,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Kawah Ijen",4,"Bersih dan terawat dengan baik, petugas sangat ramah dan helpful.","Positif","bersih dan terawat dengan baik petugas sangat ramah dan helpful"),
    ("Danau Toba",5,"Suasana alam sangat asri dan sejuk, keluarga sangat menikmati.","Positif","suasana alam sangat asri dan sejuk keluarga sangat menikmati"),
    ("Pantai Kuta Bali",3,"Cukup menarik, meski ada beberapa kekurangan di fasilitas.","Netral","cukup menarik meski ada beberapa kekurangan di fasilitas"),
    ("Danau Toba",5,"Pengalaman tak terlupakan, pasti akan kembali lagi ke sini.","Positif","pengalaman tak terlupakan pasti akan kembali lagi ke sini"),
    ("Taman Mini Indonesia Indah",5,"Bersih dan terawat dengan baik, petugas sangat ramah dan helpful.","Positif","bersih dan terawat dengan baik petugas sangat ramah dan helpful"),
    ("Prambanan Temple",4,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Komodo National Park",5,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Nusa Penida",5,"Lokasi mudah dijangkau, parkir luas, tempat sangat terawat.","Positif","lokasi mudah dijangkau parkir luas tempat sangat terawat"),
    ("Borobudur Temple",4,"Air laut jernih dan biru, pasir putih bersih, sangat indah.","Positif","air laut jernih dan biru pasir putih bersih sangat indah"),
    ("Labuan Bajo",3,"Standar wisata pada umumnya, tidak ada yang spesial.","Netral","standar wisata pada umumnya tidak ada yang spesial"),
    ("Kawah Ijen",4,"Suasana alam sangat asri dan sejuk, keluarga sangat menikmati.","Positif","suasana alam sangat asri dan sejuk keluarga sangat menikmati"),
    ("Kebun Raya Bogor",4,"Wisata alam terbaik, cocok untuk liburan keluarga dan anak-anak.","Positif","wisata alam terbaik cocok untuk liburan keluarga dan anak-anak"),
    ("Tanah Lot Bali",5,"Wisata alam terbaik, cocok untuk liburan keluarga dan anak-anak.","Positif","wisata alam terbaik cocok untuk liburan keluarga dan anak-anak"),
    ("Komodo National Park",5,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Goa Pindul",4,"Fasilitas lengkap dan nyaman, sangat cocok untuk keluarga.","Positif","fasilitas lengkap dan nyaman sangat cocok untuk keluarga"),
    ("Pantai Jimbaran",3,"Pemandangan bagus tapi terlalu ramai di akhir pekan.","Netral","pemandangan bagus tapi terlalu ramai di akhir pekan"),
    ("Danau Toba",2,"Parkir sempit dan jauh dari lokasi wisata, tidak nyaman.","Negatif","parkir sempit dan jauh dari lokasi wisata tidak nyaman"),
    ("Air Terjun Gitgit",5,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Kebun Raya Bogor",3,"Standar wisata pada umumnya, tidak ada yang spesial.","Netral","standar wisata pada umumnya tidak ada yang spesial"),
    ("Kawah Ijen",4,"Lokasi mudah dijangkau, parkir luas, tempat sangat terawat.","Positif","lokasi mudah dijangkau parkir luas tempat sangat terawat"),
    ("Kawah Ijen",5,"Tempat sangat bersih, staff ramah, dan fasilitas bagus sekali.","Positif","tempat sangat bersih staff ramah dan fasilitas bagus sekali"),
    ("Kepulauan Seribu",4,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Pantai Senggigi",4,"Pengalaman seru dan menakjubkan, pemandangan alam yang cantik.","Positif","pengalaman seru dan menakjubkan pemandangan alam yang cantik"),
    ("Pantai Jimbaran",5,"Harga tiket sangat terjangkau, nilai uang sangat sepadan.","Positif","harga tiket sangat terjangkau nilai uang sangat sepadan"),
    ("Pantai Senggigi",5,"Pengalaman seru dan menakjubkan, pemandangan alam yang cantik.","Positif","pengalaman seru dan menakjubkan pemandangan alam yang cantik"),
    ("Goa Pindul",4,"Wisata terbaik yang pernah saya kunjungi, sangat direkomendasikan.","Positif","wisata terbaik yang pernah saya kunjungi sangat direkomendasikan"),
    ("Kawah Ijen",4,"Suasana alam sangat asri dan sejuk, keluarga sangat menikmati.","Positif","suasana alam sangat asri dan sejuk keluarga sangat menikmati"),
    ("Prambanan Temple",2,"Sampah berserakan di mana-mana, pengelolaan kebersihan kurang baik.","Negatif","sampah berserakan di mana-mana pengelolaan kebersihan kurang baik"),
    ("Pantai Derawan",5,"Air laut jernih dan biru, pasir putih bersih, sangat indah.","Positif","air laut jernih dan biru pasir putih bersih sangat indah"),
    ("Pura Besakih",3,"Standar wisata pada umumnya, tidak ada yang spesial.","Netral","standar wisata pada umumnya tidak ada yang spesial"),
    ("Ubud Monkey Forest",4,"Wisata alam terbaik, cocok untuk liburan keluarga dan anak-anak.","Positif","wisata alam terbaik cocok untuk liburan keluarga dan anak-anak"),
    ("Goa Pindul",5,"Wisata alam terbaik, cocok untuk liburan keluarga dan anak-anak.","Positif","wisata alam terbaik cocok untuk liburan keluarga dan anak-anak"),
    ("Lembah Harau",4,"Lokasi mudah dijangkau, parkir luas, tempat sangat terawat.","Positif","lokasi mudah dijangkau parkir luas tempat sangat terawat"),
    ("Gunung Rinjani",4,"Suasana alam sangat asri dan sejuk, keluarga sangat menikmati.","Positif","suasana alam sangat asri dan sejuk keluarga sangat menikmati"),
    ("Pura Besakih",1,"Fasilitas toilet kurang bersih dan tidak terawat dengan baik.","Negatif","fasilitas toilet kurang bersih dan tidak terawat dengan baik"),
    ("Istana Maimun",5,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Danau Toba",4,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Pantai Parangtritis",3,"Standar wisata pada umumnya, tidak ada yang spesial.","Netral","standar wisata pada umumnya tidak ada yang spesial"),
    ("Labuan Bajo",3,"Cukup menarik, meski ada beberapa kekurangan di fasilitas.","Netral","cukup menarik meski ada beberapa kekurangan di fasilitas"),
    ("Komodo National Park",4,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Pantai Pink Lombok",5,"Wisata terbaik yang pernah saya kunjungi, sangat direkomendasikan.","Positif","wisata terbaik yang pernah saya kunjungi sangat direkomendasikan"),
    ("Taman Nasional Ujung Kulon",5,"Pemandangan sunrise di sini luar biasa indah, sangat recommended.","Positif","pemandangan sunrise di sini luar biasa indah sangat recommended"),
    ("Pantai Jimbaran",5,"Wisata alam terbaik, cocok untuk liburan keluarga dan anak-anak.","Positif","wisata alam terbaik cocok untuk liburan keluarga dan anak-anak"),
    ("Ubud Monkey Forest",4,"Tempat yang sangat indah dan memukau! Pemandangannya luar biasa.","Positif","tempat yang sangat indah dan memukau pemandangannya luar biasa"),
    ("Pantai Senggigi",4,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Raja Ampat",2,"Pedagang asongan terlalu agresif mengganggu kenyamanan wisatawan.","Negatif","pedagang asongan terlalu agresif mengganggu kenyamanan wisatawan"),
    ("Taman Mini Indonesia Indah",4,"Air laut jernih dan biru, pasir putih bersih, sangat indah.","Positif","air laut jernih dan biru pasir putih bersih sangat indah"),
    ("Lembah Harau",5,"Spot foto terbaik, instagramable banget! Tempat sangat cantik.","Positif","spot foto terbaik instagramable banget tempat sangat cantik"),
    ("Taman Mini Indonesia Indah",5,"Suasana alam sangat asri dan sejuk, keluarga sangat menikmati.","Positif","suasana alam sangat asri dan sejuk keluarga sangat menikmati")
]

@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.DataFrame(_DATA, columns=_COLUMNS)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
def inject_css():
    st.markdown("""
<style>
:root { color-scheme: dark; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp, .main, .block-container {
    background-color: #0D1117 !important;
    color: #F0F6FC !important;
    padding-top: 1rem !important;
}
.block-container { max-width: 100% !important; padding-left: 2rem; padding-right: 2rem; }
section[data-testid="stSidebar"] {
    background: #0D1B2E !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
    min-width: 260px !important;
}
section[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
.sidebar-title {
    font-size: 11px; font-weight: 700; letter-spacing: 1.5px;
    color: #64748B !important; text-transform: uppercase; margin-bottom: 12px;
}
.filter-label { font-size: 13px; font-weight: 600; color: #94A3B8 !important; margin-bottom: 6px; }
.stSelectbox > div > div {
    background: #1C2A3A !important; border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important; color: #F0F6FC !important;
}
.stTextInput > div > div > input {
    background: #1C2A3A !important; border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important; color: #F0F6FC !important;
}
.header-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 18px 24px; margin-bottom: 20px;
    background: #161D2B; border: 1px solid rgba(255,255,255,0.07); border-radius: 18px;
}
.header-left { display: flex; align-items: center; gap: 16px; }
.app-badge {
    width: 48px; height: 48px; border-radius: 16px;
    display: grid; place-items: center; font-size: 1.4rem;
    background: linear-gradient(135deg, #6D28D9, #2563EB);
}
.header-title { font-size: 1.75rem; font-weight: 700; color: #F0F6FC; line-height: 1.2; }
.header-subtitle { font-size: 0.88rem; color: #64748B; margin-top: 2px; }
.header-right { display: flex; align-items: center; gap: 12px; }
.header-date { color: #94A3B8; font-size: 0.88rem; }
.status-chip {
    padding: 8px 14px; border-radius: 999px;
    background: rgba(34,197,94,0.12); color: #86EFAC; font-size: 0.85rem; font-weight: 500;
}
.info-banner {
    display: flex; align-items: center; gap: 12px;
    padding: 14px 20px; margin-bottom: 20px;
    background: rgba(37,99,235,0.1); border: 1px solid rgba(37,99,235,0.25);
    border-radius: 12px; font-size: 0.88rem; color: #93C5FD;
}
.metric-card {
    background: #161D2B; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px; padding: 20px; height: 100%;
}
.metric-icon-wrap {
    width: 40px; height: 40px; border-radius: 12px;
    display: grid; place-items: center; font-size: 1.1rem; margin-bottom: 14px;
}
.metric-label { font-size: 0.82rem; color: #64748B; font-weight: 500; margin-bottom: 4px; }
.metric-value { font-size: 1.85rem; font-weight: 800; color: #F0F6FC; line-height: 1; }
.metric-sub { font-size: 0.82rem; margin-top: 6px; font-weight: 500; }
.metric-sub-gray { color: #64748B; }
.metric-sub-green { color: #4ADE80; }
.metric-sub-red { color: #F87171; }
.content-card {
    background: #161D2B; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 20px 22px; margin-bottom: 16px;
}
.card-title { font-size: 1rem; font-weight: 700; color: #F0F6FC; margin-bottom: 4px; }
.section-title { font-size: 1.1rem; font-weight: 700; color: #F0F6FC; margin: 18px 0 10px 0; }
.footer-card {
    text-align: center; font-size: 0.82rem; color: #475569;
    padding: 16px; margin-top: 32px; border-top: 1px solid rgba(255,255,255,0.06);
}
/* ── Sidebar nav buttons ── */
section[data-testid="stSidebar"] .stButton > button {
    background: #1C2A3A !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: #CBD5E1 !important;
    text-align: left !important;
    padding: 9px 14px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    width: 100% !important;
    margin-bottom: 4px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(37,99,235,0.2) !important;
    border-color: rgba(37,99,235,0.4) !important;
    color: #E0E7FF !important;
}
section[data-testid="stSidebar"] .stCaption p {
    font-size: 10px !important;
    color: #334155 !important;
    text-align: center !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def clean_text(text: str) -> str:
    if pd.isna(text): return ""
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def build_similarity_graph(df: pd.DataFrame, threshold: float = 0.2) -> nx.Graph:
    place_text = df.groupby("place")["clean_comment"].apply(lambda x: " ".join(x.dropna().astype(str)))
    if len(place_text) < 2:
        return nx.Graph()
    X = TfidfVectorizer(max_features=300).fit_transform(place_text)
    sim = cosine_similarity(X)
    places = place_text.index.tolist()
    G = nx.Graph()
    G.add_nodes_from(places)
    for i in range(len(places)):
        for j in range(i + 1, len(places)):
            if sim[i, j] > threshold:
                G.add_edge(places[i], places[j], weight=float(sim[i, j]))
    return G


def build_network_plotly(G: nx.Graph) -> go.Figure:
    fig = go.Figure()
    if len(G) == 0:
        fig.add_annotation(text="Tidak ada data cukup untuk graph.", xref="paper", yref="paper",
                           showarrow=False, font=dict(size=15, color="#94A3B8"))
        fig.update_layout(template="plotly_dark", paper_bgcolor="#161D2B", plot_bgcolor="#161D2B",
                          xaxis=dict(visible=False), yaxis=dict(visible=False))
        return fig
    pos = nx.spring_layout(G, seed=42, k=1.2)
    ex, ey = [], []
    for u, v in G.edges():
        x0,y0=pos[u]; x1,y1=pos[v]
        ex+=[x0,x1,None]; ey+=[y0,y1,None]
    fig.add_trace(go.Scatter(x=ex, y=ey, mode="lines",
                             line=dict(width=1, color="rgba(99,102,241,0.3)"), hoverinfo="none"))
    deg = nx.degree_centrality(G)
    btw = nx.betweenness_centrality(G, normalized=True)
    clo = nx.closeness_centrality(G)

    # Warna node berbasis centrality (spec):
    # 🟢 Hijau = centrality tinggi, 🟡 Kuning = sedang, 🔴 Merah = rendah
    deg_values = [deg[n] for n in G.nodes()]
    if deg_values:
        q33 = float(pd.Series(deg_values).quantile(0.33))
        q66 = float(pd.Series(deg_values).quantile(0.66))
    else:
        q33, q66 = 0.0, 0.0

    c_high = "#22C55E"   # Hijau
    c_mid  = "#FACC15"   # Kuning
    c_low  = "#EF4444"   # Merah

    nx_x, nx_y, nt, nc, ns = [], [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        nx_x.append(x)
        nx_y.append(y)

        # kategori berdasarkan degree centrality
        d = deg[node]
        if d >= q66:
            color = c_high
        elif d >= q33:
            color = c_mid
        else:
            color = c_low
        nc.append(color)

        # ukuran node juga tetap mengikuti centrality (semakin besar semakin penting)
        ns.append(10 + d * 40)

        nt.append(
            f"<b>{node}</b><br>Degree:{deg[node]:.3f}"
            f"<br>Betweenness:{btw[node]:.3f}<br>Closeness:{clo[node]:.3f}"
        )

    fig.add_trace(go.Scatter(x=nx_x, y=nx_y, mode="markers+text",
                             text=list(G.nodes()), textposition="top center",
                             textfont=dict(size=7, color="#CBD5E1"),
                             hovertext=nt, hoverinfo="text",
                             marker=dict(size=ns, color=nc, line=dict(width=1,color="#0D1117"))))
    fig.update_layout(template="plotly_dark", paper_bgcolor="#161D2B", plot_bgcolor="#161D2B",
                      margin=dict(l=10,r=10,t=10,b=10), hovermode="closest", showlegend=False)
    fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(showgrid=False, zeroline=False, visible=False)
    return fig


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar(df: pd.DataFrame):
    with st.sidebar:
        st.markdown("<div class='sidebar-title'>FILTER DATA</div>", unsafe_allow_html=True)

        st.markdown("<div class='filter-label'>Tempat Wisata</div>", unsafe_allow_html=True)
        places = ["Semua Tempat"] + sorted(df["place"].dropna().unique().tolist())
        sel_place = st.selectbox("Tempat Wisata", places, label_visibility="collapsed", key="place_sel")

        st.markdown("<div class='filter-label' style='margin-top:12px;'>Rating</div>", unsafe_allow_html=True)
        sel_rating = st.selectbox("Rating", ["Semua Rating","5 ⭐","4 ⭐","3 ⭐","2 ⭐","1 ⭐"],
                                  label_visibility="collapsed", key="rating_sel")

        st.markdown("<div class='filter-label' style='margin-top:12px;'>Sentimen</div>", unsafe_allow_html=True)
        sel_sentiment = st.selectbox("Sentimen", ["Semua Sentimen","Positif","Netral","Negatif"],
                                     label_visibility="collapsed", key="sent_sel")

        st.markdown("<div class='filter-label' style='margin-top:12px;'>Cari Kata</div>", unsafe_allow_html=True)
        search_text = st.text_input("Cari kata", placeholder="Cari kata di komentar...", key="search_inp")

        st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.08);margin:14px 0;'>",
                    unsafe_allow_html=True)
        st.markdown("<div class='sidebar-title'>NAVIGASI</div>", unsafe_allow_html=True)

        if "selected_page" not in st.session_state:
            st.session_state["selected_page"] = "Ringkasan"

        nav_items = [
            ("🏠", "Ringkasan"),
            ("😊", "Visualisasi Sentimen"),
            ("☁️", "WordCloud"),
            ("📊", "TF-IDF"),
            ("🔗", "Social Network Analysis"),
            ("📄", "Dataset"),
            ("ℹ️", "Tentang"),
        ]
        for icon, label in nav_items:
            active = st.session_state["selected_page"] == label
            btn_style = "background-color:#2563EB;color:#fff;border:none;" if active else ""
            if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
                st.session_state["selected_page"] = label
                st.rerun()

        st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:14px 0;'>",
                    unsafe_allow_html=True)
        st.caption("© 2026 Dashboard Analisis Wisata · Google Maps Review Analytics")

    return sel_place, sel_rating, sel_sentiment, search_text


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
def render_header():
    today = datetime.now().strftime("%d %B %Y")
    st.markdown(f"""
    <div class='info-banner'>
        ℹ️ Dashboard ini menganalisis ulasan untuk berbagai tempat wisata dan menampilkan insight sentimen, kata kunci, dan jaringan co-occurrence.
    </div>
    <div class='header-row'>
        <div class='header-left'>
            <div class='app-badge'>📊</div>
            <div>
                <div class='header-title'>Dashboard Analisis Tempat Wisata</div>
                <div class='header-subtitle'>Google Maps Review Analytics</div>
            </div>
        </div>
        <div class='header-right'>
            <div class='header-date'>{today}</div>
            <div class='status-chip'>🟢 Online</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# METRIC CARDS
# ─────────────────────────────────────────────
def render_metrics(filtered: pd.DataFrame):
    total      = len(filtered)
    n_places   = filtered["place"].nunique()
    avg_r      = filtered["rating"].astype(float).mean() if total else 0
    pos        = int((filtered["sentiment"] == "Positif").sum())
    neg        = int((filtered["sentiment"] == "Negatif").sum())
    pos_pct    = pos * 100 / total if total else 0
    neg_pct    = neg * 100 / total if total else 0

    cards = [
        ("💬","Total Review",  f"{total:,}",    "Jumlah ulasan yang dianalisis","#8B5CF6","metric-sub-gray"),
        ("📍","Jumlah Tempat", f"{n_places}",   "Destinasi wisata unik",        "#2563EB","metric-sub-gray"),
        ("⭐","Rating Rata-rata",f"{avg_r:.2f}","Skala 1-5",                    "#F59E0B","metric-sub-gray"),
        ("😊","Review Positif",f"{pos_pct:.0f}%",f"{pos_pct:.1f}% Positif",    "#F97316","metric-sub-green"),
        ("😞","Review Negatif",f"{neg_pct:.0f}%",f"{neg_pct:.1f}% Negatif",    "#EF4444","metric-sub-red"),
    ]
    cols = st.columns(5, gap="small")
    for col,(icon,label,value,sub,color,sub_cls) in zip(cols,cards):
        with col:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-icon-wrap' style='background:{color}22;'>
                    <span style='font-size:1.2rem;'>{icon}</span>
                </div>
                <div class='metric-label'>{label}</div>
                <div class='metric-value'>{value}</div>
                <div class='metric-sub {sub_cls}'>{sub}</div>
            </div>
            """, unsafe_allow_html=True)
    return total, n_places, avg_r, pos, neg, pos_pct, neg_pct


# ─────────────────────────────────────────────
# PAGE: RINGKASAN
# ─────────────────────────────────────────────
def page_ringkasan(filtered, total, pos_pct, neg_pct):
    st.markdown("<div class='section-title'>Distribusi & Analisis</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown("<div class='content-card'><div class='card-title'>Distribusi Rating</div></div>",
                    unsafe_allow_html=True)
        rc = filtered["rating"].astype(int).value_counts().sort_index()
        pcts = (rc / rc.sum() * 100).round(1)
        fig = go.Figure(go.Bar(
            x=rc.index.astype(str), y=rc.values,
            text=[f"{v:,} ({pcts.get(i,0)}%)" for i,v in zip(rc.index,rc.values)],
            textposition="outside",
            marker=dict(color="#7C3AED", line=dict(color="#A78BFA", width=0)),
            hovertemplate="Rating %{x}<br>%{y} ulasan<extra></extra>",
        ))
        fig.update_layout(template="plotly_dark", plot_bgcolor="#161D2B", paper_bgcolor="#161D2B",
                          height=320, margin=dict(l=10,r=10,t=30,b=10),
                          xaxis=dict(title="Rating", tickfont=dict(size=13)),
                          yaxis=dict(title="Jumlah Review", gridcolor="rgba(255,255,255,0.05)"),
                          bargap=0.3)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col2:
        st.markdown("<div class='content-card'><div class='card-title'>Distribusi Sentimen</div></div>",
                    unsafe_allow_html=True)
        sc = filtered["sentiment"].value_counts()
        cmap = {"Positif":"#22C55E","Netral":"#60A5FA","Negatif":"#EF4444"}
        colors = [cmap.get(s,"#94A3B8") for s in sc.index]
        dominant = sc.idxmax() if not sc.empty else "-"
        dom_pct  = int(sc.max()/total*100) if total else 0
        fig2 = go.Figure(go.Pie(
            labels=sc.index, values=sc.values, hole=0.62,
            marker=dict(colors=colors, line=dict(color="#0D1117",width=2)),
            textinfo="label+percent", textfont=dict(size=11,color="#F0F6FC"),
            hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
        ))
        fig2.add_annotation(text=f"<b>{dom_pct}%</b><br><span style='font-size:11px'>{dominant}</span>",
                            x=0.5, y=0.5, showarrow=False,
                            font=dict(size=18, color="#22C55E" if dominant=="Positif" else "#F0F6FC"))
        fig2.update_layout(template="plotly_dark", paper_bgcolor="#161D2B",
                           height=320, margin=dict(l=0,r=0,t=10,b=10),
                           legend=dict(orientation="v",x=1.02,y=0.5,font=dict(color="#CBD5E1",size=11)))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    col3, col4 = st.columns([2, 1], gap="medium")
    with col3:
        st.markdown("<div class='content-card'><div class='card-title'>Rating Rata-rata per Tempat</div></div>",
                    unsafe_allow_html=True)
        avg_r = filtered.groupby("place")["rating"].mean().sort_values(ascending=False)
        fig3 = px.bar(x=avg_r.index, y=avg_r.values, labels={"x":"","y":"Rating"},
                      color=avg_r.values, color_continuous_scale=["#3B82F6","#22C55E","#F59E0B"])
        fig3.update_layout(template="plotly_dark", plot_bgcolor="#161D2B", paper_bgcolor="#161D2B",
                           height=280, margin=dict(l=10,r=10,t=10,b=50),
                           xaxis_tickangle=-40, coloraxis_showscale=False)
        fig3.update_traces(hovertemplate="%{x}<br>Rating: %{y:.2f}<extra></extra>")
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    with col4:
        st.markdown("<div class='content-card'><div class='card-title'>Top 10 Tempat by Review</div></div>",
                    unsafe_allow_html=True)
        top = filtered["place"].value_counts().head(10)
        fig4 = px.bar(x=top.values, y=top.index, orientation="h",
                      color=top.values, color_continuous_scale="purples", labels={"x":"Jumlah","y":""})
        fig4.update_layout(template="plotly_dark", plot_bgcolor="#161D2B", paper_bgcolor="#161D2B",
                           height=280, margin=dict(l=5,r=10,t=10,b=10),
                           yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────
# PAGE: SENTIMEN
# ─────────────────────────────────────────────
def page_sentimen(filtered):
    st.markdown("<div class='section-title'>Analisis Sentimen</div>", unsafe_allow_html=True)
    cmap = {"Positif":"#22C55E","Netral":"#60A5FA","Negatif":"#EF4444"}
    sc = filtered["sentiment"].value_counts()
    c1, c2 = st.columns(2, gap="medium")

    with c1:
        st.markdown("<div class='content-card'><div class='card-title'>Pie Sentimen</div></div>", unsafe_allow_html=True)
        fig = px.pie(names=sc.index, values=sc.values, hole=0.52,
                     color=sc.index, color_discrete_map=cmap)
        fig.update_layout(template="plotly_dark", paper_bgcolor="#161D2B",
                          height=360, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with c2:
        st.markdown("<div class='content-card'><div class='card-title'>Bar Sentimen</div></div>", unsafe_allow_html=True)
        sa = sc.reindex(["Positif","Netral","Negatif"], fill_value=0)
        fig2 = px.bar(x=sa.index, y=sa.values, color=sa.index,
                      color_discrete_map=cmap, labels={"x":"Sentimen","y":"Jumlah"})
        fig2.update_layout(template="plotly_dark", plot_bgcolor="#161D2B", paper_bgcolor="#161D2B",
                           height=360, margin=dict(l=10,r=10,t=10,b=10), showlegend=False)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div class='content-card'><div class='card-title'>Sentimen per Tempat Wisata (Stacked)</div></div>",
                unsafe_allow_html=True)
    sp = filtered.groupby(["place","sentiment"]).size().unstack(fill_value=0)
    for col in ["Positif","Netral","Negatif"]:
        if col not in sp.columns: sp[col] = 0
    fig3 = go.Figure()
    for s,c in cmap.items():
        if s in sp.columns:
            fig3.add_trace(go.Bar(name=s, x=sp.index, y=sp[s], marker_color=c))
    fig3.update_layout(barmode="stack", template="plotly_dark",
                       plot_bgcolor="#161D2B", paper_bgcolor="#161D2B",
                       height=320, margin=dict(l=10,r=10,t=10,b=50), xaxis_tickangle=-40)
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────
# PAGE: WORDCLOUD
# ─────────────────────────────────────────────
def page_wordcloud(filtered):
    st.markdown("<div class='section-title'>WordCloud & Kata Paling Umum</div>", unsafe_allow_html=True)
    text = " ".join(filtered["clean_comment"].astype(str).tolist()).strip()
    if not text:
        st.info("Tidak ada teks untuk ditampilkan."); return

    st.markdown("<div class='content-card'><div class='card-title'>WordCloud Komentar</div></div>",
                unsafe_allow_html=True)
    wc = WordCloud(width=1100, height=380, background_color="#161D2B",
                   colormap="cool", max_words=120).generate(text)
    fig_wc, ax = plt.subplots(figsize=(13, 4), facecolor="#161D2B")
    ax.imshow(wc, interpolation="bilinear"); ax.axis("off")
    st.pyplot(fig_wc); plt.close(fig_wc)

    st.markdown("<div class='content-card'><div class='card-title'>20 Kata Paling Sering Muncul</div></div>",
                unsafe_allow_html=True)
    top_w = pd.DataFrame(Counter(text.split()).most_common(20), columns=["Kata","Frekuensi"])
    fig = px.bar(top_w, x="Frekuensi", y="Kata", orientation="h",
                 color="Frekuensi", color_continuous_scale="purples")
    fig.update_layout(template="plotly_dark", plot_bgcolor="#161D2B", paper_bgcolor="#161D2B",
                      height=480, margin=dict(l=10,r=10,t=10,b=10),
                      yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────
# PAGE: SNA
# ─────────────────────────────────────────────
def page_sna(filtered):
    st.markdown("<div class='section-title'>Social Network Analysis</div>", unsafe_allow_html=True)
    G = build_similarity_graph(filtered)
    c1, c2 = st.columns([2, 1], gap="medium")
    with c1:
        st.markdown("<div class='content-card'><div class='card-title'>Graf Kemiripan Antar Tempat</div></div>",
                    unsafe_allow_html=True)
        st.plotly_chart(build_network_plotly(G), use_container_width=True, config={"displayModeBar": False})
    with c2:
        st.markdown("<div class='content-card'><div class='card-title'>Top 10 Centrality</div></div>",
                    unsafe_allow_html=True)
        if len(G) == 0:
            st.write("Graph kosong.")
        else:
            deg = nx.degree_centrality(G)
            btw = nx.betweenness_centrality(G, normalized=True)
            clo = nx.closeness_centrality(G)
            rows = [{"Tempat":n,"Degree":deg[n],"Betweenness":btw[n],"Closeness":clo[n]} for n in G.nodes()]
            cdf = pd.DataFrame(rows).sort_values("Degree",ascending=False).head(10).reset_index(drop=True)
            st.dataframe(cdf.style.format({"Degree":"{:.3f}","Betweenness":"{:.3f}","Closeness":"{:.3f}"}),
                         use_container_width=True)


# ─────────────────────────────────────────────
# PAGE: TF-IDF
# ─────────────────────────────────────────────
def page_tfidf(filtered: pd.DataFrame):
    st.markdown("<div class='section-title'>📊 Analisis TF-IDF</div>", unsafe_allow_html=True)

    corpus = filtered["clean_comment"].astype(str).tolist()
    places = filtered["place"].astype(str).tolist()

    if len(corpus) < 2:
        st.info("Data terlalu sedikit untuk analisis TF-IDF. Hapus filter untuk melihat semua data.")
        return

    # ── Fit TF-IDF ──
    vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2), min_df=1)
    tfidf_matrix = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)
    tfidf_df["place"] = places

    # Global mean scores
    global_scores = pd.Series(
        tfidf_matrix.toarray().mean(axis=0), index=feature_names
    ).sort_values(ascending=False)

    # ── STATISTIK KPI ──
    st.markdown("<div class='section-title' style='font-size:0.95rem;color:#94A3B8;margin-top:4px;'>Statistik TF-IDF</div>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4, gap="small")
    stats = [
        ("📄", "Jumlah Dokumen",  f"{len(corpus):,}",        "Total ulasan diproses",       "#6D28D9"),
        ("🔤", "Kata Unik",       f"{len(feature_names):,}", "Setelah stopword removal",     "#2563EB"),
        ("⚙️", "Max Features",   "500",                     "Batas fitur TF-IDF",           "#0891B2"),
        ("🔢", "N-gram Range",    "1 – 2",                   "Unigram & Bigram",             "#059669"),
    ]
    for col, (icon, label, val, sub, color) in zip([k1, k2, k3, k4], stats):
        with col:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-icon-wrap' style='background:{color}22;'>
                    <span style='font-size:1.1rem;'>{icon}</span>
                </div>
                <div class='metric-label'>{label}</div>
                <div class='metric-value' style='font-size:1.5rem;'>{val}</div>
                <div class='metric-sub metric-sub-gray'>{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROW 1: Top-20 Bar Chart + TF-IDF Table ──
    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown("<div class='content-card'><div class='card-title'>Top 20 Kata dengan Skor TF-IDF Tertinggi</div></div>",
                    unsafe_allow_html=True)
        top20 = global_scores.head(20).reset_index()
        top20.columns = ["Kata", "Skor"]
        fig = px.bar(top20, x="Skor", y="Kata", orientation="h",
                     color="Skor", color_continuous_scale=["#3B82F6", "#8B5CF6", "#EC4899"],
                     labels={"Skor": "Skor TF-IDF", "Kata": ""})
        fig.update_layout(template="plotly_dark", plot_bgcolor="#161D2B", paper_bgcolor="#161D2B",
                          height=420, margin=dict(l=10, r=20, t=10, b=10),
                          yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        fig.update_traces(hovertemplate="%{y}<br>Skor: %{x:.4f}<extra></extra>")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col2:
        st.markdown("<div class='content-card'><div class='card-title'>Tabel TF-IDF — Top 50 Kata</div></div>",
                    unsafe_allow_html=True)
        tbl = global_scores.head(50).reset_index()
        tbl.columns = ["Kata", "Skor TF-IDF"]
        tbl["Skor TF-IDF"] = tbl["Skor TF-IDF"].round(4)
        tbl.index = tbl.index + 1

        search_word = st.text_input("🔍 Cari kata", placeholder="Ketik kata...", key="tfidf_search")
        if search_word:
            tbl = tbl[tbl["Kata"].str.contains(search_word, case=False)]

        st.dataframe(tbl, use_container_width=True, height=340)
        csv_tbl = tbl.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Download Tabel CSV", data=csv_tbl,
                           file_name="tfidf_table.csv", mime="text/csv")

    # ── ROW 2: Heatmap ──
    st.markdown("<div class='content-card'><div class='card-title'>Heatmap TF-IDF — Top 15 Kata per Tempat Wisata</div><div class='card-sub'>Warna lebih terang = skor lebih tinggi pada tempat tersebut</div></div>",
                unsafe_allow_html=True)

    top15_words = global_scores.head(15).index.tolist()
    place_group = tfidf_df.groupby("place")[top15_words].mean()

    fig_heat = px.imshow(
        place_group.T,
        color_continuous_scale="Purples",
        labels=dict(x="Tempat Wisata", y="Kata", color="Skor"),
        aspect="auto",
    )
    fig_heat.update_layout(template="plotly_dark", paper_bgcolor="#161D2B",
                            height=400, margin=dict(l=10, r=10, t=10, b=80),
                            xaxis_tickangle=-40)
    fig_heat.update_traces(hovertemplate="Tempat: %{x}<br>Kata: %{y}<br>Skor: %{z:.4f}<extra></extra>")
    st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})

    # ── ROW 3: Kata Penting per Tempat (expander) + Alur SNA ──
    col3, col4 = st.columns([3, 2], gap="medium")

    with col3:
        st.markdown("<div class='content-card'><div class='card-title'>📍 Kata Penting per Tempat Wisata (Top 5)</div></div>",
                    unsafe_allow_html=True)
        places_list = sorted(tfidf_df["place"].unique())
        for place in places_list:
            place_rows = tfidf_df[tfidf_df["place"] == place].drop(columns=["place"])
            if place_rows.empty:
                continue
            top_words_place = place_rows.mean().sort_values(ascending=False).head(5)
            with st.expander(f"📍 {place}", expanded=False):
                for rank, (word, score) in enumerate(top_words_place.items(), 1):
                    bar_w = int(score / top_words_place.max() * 100) if top_words_place.max() > 0 else 0
                    st.markdown(f"""
                    <div style='display:flex;align-items:center;gap:10px;margin-bottom:6px;'>
                        <span style='color:#94A3B8;font-size:12px;width:16px;'>{rank}.</span>
                        <span style='color:#F0F6FC;font-size:13px;min-width:110px;'>{word}</span>
                        <div style='flex:1;background:rgba(255,255,255,0.06);border-radius:4px;height:8px;'>
                            <div style='width:{bar_w}%;background:linear-gradient(90deg,#6D28D9,#2563EB);border-radius:4px;height:8px;'></div>
                        </div>
                        <span style='color:#A78BFA;font-size:11px;min-width:50px;text-align:right;'>{score:.4f}</span>
                    </div>
                    """, unsafe_allow_html=True)

    with col4:
        st.markdown("<div class='content-card'><div class='card-title'>🔗 Alur Analisis: TF-IDF → SNA</div><div class='card-sub'>Bagaimana TF-IDF menjadi dasar Social Network Analysis</div></div>",
                    unsafe_allow_html=True)
        st.markdown("""
        <div style='padding:8px 0;'>
            <div style='display:flex;flex-direction:column;gap:0;'>
                <div style='display:flex;align-items:center;gap:12px;padding:10px 14px;background:rgba(109,40,217,0.15);border:1px solid rgba(109,40,217,0.3);border-radius:12px;margin-bottom:4px;'>
                    <span style='font-size:1.3rem;'>📝</span>
                    <div><div style='color:#F0F6FC;font-weight:600;font-size:13px;'>Review / Komentar</div><div style='color:#94A3B8;font-size:11px;'>Raw text dari ulasan wisatawan</div></div>
                </div>
                <div style='text-align:center;color:#475569;font-size:18px;'>↓</div>
                <div style='display:flex;align-items:center;gap:12px;padding:10px 14px;background:rgba(37,99,235,0.15);border:1px solid rgba(37,99,235,0.3);border-radius:12px;margin-bottom:4px;'>
                    <span style='font-size:1.3rem;'>🔧</span>
                    <div><div style='color:#F0F6FC;font-weight:600;font-size:13px;'>Preprocessing</div><div style='color:#94A3B8;font-size:11px;'>Lowercase, remove noise, tokenize</div></div>
                </div>
                <div style='text-align:center;color:#475569;font-size:18px;'>↓</div>
                <div style='display:flex;align-items:center;gap:12px;padding:10px 14px;background:rgba(8,145,178,0.15);border:1px solid rgba(8,145,178,0.3);border-radius:12px;margin-bottom:4px;'>
                    <span style='font-size:1.3rem;'>📊</span>
                    <div><div style='color:#F0F6FC;font-weight:600;font-size:13px;'>TF-IDF Vectorization</div><div style='color:#94A3B8;font-size:11px;'>Term Frequency × Inverse Document Frequency</div></div>
                </div>
                <div style='text-align:center;color:#475569;font-size:18px;'>↓</div>
                <div style='display:flex;align-items:center;gap:12px;padding:10px 14px;background:rgba(5,150,105,0.15);border:1px solid rgba(5,150,105,0.3);border-radius:12px;margin-bottom:4px;'>
                    <span style='font-size:1.3rem;'>📐</span>
                    <div><div style='color:#F0F6FC;font-weight:600;font-size:13px;'>Cosine Similarity</div><div style='color:#94A3B8;font-size:11px;'>Hitung kemiripan antar dokumen wisata</div></div>
                </div>
                <div style='text-align:center;color:#475569;font-size:18px;'>↓</div>
                <div style='display:flex;align-items:center;gap:12px;padding:10px 14px;background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.3);border-radius:12px;margin-bottom:4px;'>
                    <span style='font-size:1.3rem;'>🕸️</span>
                    <div><div style='color:#F0F6FC;font-weight:600;font-size:13px;'>Graph / Network</div><div style='color:#94A3B8;font-size:11px;'>Node = tempat, Edge = kemiripan tinggi</div></div>
                </div>
                <div style='text-align:center;color:#475569;font-size:18px;'>↓</div>
                <div style='display:flex;align-items:center;gap:12px;padding:10px 14px;background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.3);border-radius:12px;'>
                    <span style='font-size:1.3rem;'>📈</span>
                    <div><div style='color:#F0F6FC;font-weight:600;font-size:13px;'>Degree / Betweenness / Closeness</div><div style='color:#94A3B8;font-size:11px;'>Centrality sebagai hasil akhir SNA</div></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── TF-IDF Matrix download ──
    st.markdown("<div class='content-card'><div class='card-title'>📋 TF-IDF Matrix (Sample 20 baris × Top 20 fitur)</div></div>",
                unsafe_allow_html=True)
    matrix_sample = tfidf_df[top15_words + ["place"]].head(20).set_index("place")
    matrix_sample = matrix_sample.round(4)
    st.dataframe(matrix_sample, use_container_width=True, height=280)
    buf = io.BytesIO()
    tfidf_df.to_csv(buf, index=False)
    buf.seek(0)
    st.download_button("⬇ Download TF-IDF Matrix (Full CSV)", data=buf,
                       file_name="tfidf_matrix.csv", mime="text/csv")


# ─────────────────────────────────────────────
# PAGE: DATASET
# ─────────────────────────────────────────────
def page_dataset(filtered):
    st.markdown("<div class='section-title'>Dataset Review Wisata</div>", unsafe_allow_html=True)
    st.dataframe(filtered.reset_index(drop=True), use_container_width=True, height=420)
    c1, c2, _ = st.columns([1,1,3])
    with c1:
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Download CSV", data=csv, file_name="wisata_reviews.csv", mime="text/csv")
    with c2:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as w:
            filtered.to_excel(w, index=False, sheet_name="Dataset")
        buf.seek(0)
        st.download_button("⬇ Download Excel", data=buf, file_name="wisata_reviews.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ─────────────────────────────────────────────
# PAGE: TENTANG
# ─────────────────────────────────────────────
def page_tentang():
    st.markdown("<div class='section-title'>Tentang Dashboard</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='content-card'>
        <div class='card-title'>📊 Dashboard Analisis Tempat Wisata</div>
        <p style='color:#94A3B8;margin-top:10px;line-height:1.7;'>
            Dashboard ini menganalisis ulasan tempat wisata Indonesia, menampilkan insight sentimen,
            kata kunci populer, dan Social Network Analysis antar destinasi wisata.
        </p>
        <hr style='border-color:rgba(255,255,255,0.08);margin:16px 0;'>
        <div class='card-title'>🛠 Teknologi</div>
        <ul style='color:#94A3B8;line-height:2;margin-top:8px;'>
            <li>Streamlit — framework dashboard interaktif</li>
            <li>Plotly — visualisasi data interaktif</li>
            <li>Scikit-Learn — TF-IDF Vectorization & Cosine Similarity</li>
            <li>NetworkX — Social Network Analysis (Degree, Betweenness, Closeness)</li>
            <li>WordCloud — visualisasi kata kunci positif & negatif</li>
            <li>Pandas — manajemen & transformasi data</li>
        </ul>
        <hr style='border-color:rgba(255,255,255,0.08);margin:16px 0;'>
        <div class='card-title'>📂 Dataset</div>
        <p style='color:#94A3B8;margin-top:8px;'>
            300 ulasan dari 30 destinasi wisata Indonesia (Bali, Lombok, Jawa, Sulawesi, Papua, dan lainnya).
            Data sudah di-embed langsung di dalam aplikasi — tidak perlu upload file CSV terpisah.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    inject_css()
    df = load_data()
    df["rating"] = df["rating"].astype(int)

    sel_place, sel_rating, sel_sentiment, search_text = render_sidebar(df)

    # Apply filters
    filtered = df.copy()
    if sel_place != "Semua Tempat":
        filtered = filtered[filtered["place"] == sel_place]
    if sel_rating != "Semua Rating":
        r = int(sel_rating[0])
        filtered = filtered[filtered["rating"] == r]
    if sel_sentiment != "Semua Sentimen":
        filtered = filtered[filtered["sentiment"] == sel_sentiment]
    if search_text:
        filtered = filtered[filtered["comment"].str.contains(search_text, case=False, na=False)]

    render_header()
    total, n_places, avg_r, pos, neg, pos_pct, neg_pct = render_metrics(filtered)

    page = st.session_state.get("selected_page", "Ringkasan")

    if page == "Ringkasan":
        page_ringkasan(filtered, total, pos_pct, neg_pct)
    elif page == "Visualisasi Sentimen":
        page_sentimen(filtered)
    elif page == "WordCloud":
        page_wordcloud(filtered)
    elif page == "TF-IDF":
        page_tfidf(filtered)
    elif page == "Social Network Analysis":
        page_sna(filtered)
    elif page == "Dataset":
        page_dataset(filtered)
    elif page == "Tentang":
        page_tentang()

    st.markdown("""
    <div class='footer-card'>
        Sumber Data: Google Maps Review · Python · Streamlit · Plotly · NetworkX · Scikit-Learn
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
