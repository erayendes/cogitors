# Cogitor

Participation: 3/3 — complete. Chair: antigravity.

Host: session-contextual (unmetered by runner).

## Answer

The Cogitors protokolünü sıfır bağımlılık (Python 3.9+ stdlib), deterministik kapı denetimi ve 'görüş birliği doğruluk kanıtı değildir' ilkelerinden taviz vermeden geliştirecek 5 maddelik kesin yol haritası belirlenmiştir:

1. **Yapısal İtiraz Kimlikleri ve Sentez Bütünlük Kapısı:** Serbest metin araması yerine, 4. turda çözülememiş her itiraza deterministik bir kimlik (`O-1`, `O-2` vb.) verilmesi; `finish` aşamasında her kimliğin `accepted`, `rejected` veya `unresolved` durumunun aranarak başkanın azınlık görüşlerini bastırmasını engelleyen kod tabanlı bir kapı eklenmesi.
2. **Deterministik İddia Defteri ('Alıntı Eşleşti' Ayrımı):** Ağır sandbox yerine, snapshot üzerinden `source_sha256 + tam_alıntı + alıntı_hash` kontrolü yapan stdlib doğrulayıcı. Epistemolojik sınır gereği çıktı etiketi sahte güven yaratmamak için 'doğrulandı' değil, kesinlikle 'Alıntı Eşleşti (Quote Matched)' olmalıdır.
3. **Güvenli ve Akıllı `resume` Teşhis Komutu:** Model çağırmayan adımları (`check`, `status`, `advance`) otomatik yürüten; yarıda kalmış veya başarısız çağrılarda asla otomatik harcama yapmayıp `extend-timeout` ve `continue-partial` kararlarını kullanıcı onayına sunan bir kurtarma aracı.
4. **Dokümantasyon Dürüstlüğü ve Test Senkronizasyonu:** Dokümandaki çağrı bütçesi ifadesinin '8 ilk çağrı + kullanıcı onaylı retry' olarak düzeltilmesi ve README'deki 47 vs 51 test sayısı çelişkisinin CI/pre-commit test çıktısıyla senkronize edilmesi.
5. **Açık Model ve Sağlayıcı Genişletmesi (Talep Odaklı):** Kabuk (shell) veya karmaşık MCP katmanı yerine; gerçek kullanıcı talebi oluştuğunda dar, argv-listesi ve stdin/stdout sözleşmesiyle çalışan bir CLI adaptörünün (Ollama/vLLM) sisteme eklenmesi.

## Agreement

Üç katılımcı (Codex, Claude, Antigravity) şu konularda tam mutabakata varmıştır:
- Serbest metin aramasıyla sentez denetimi yapılamayacağı, yapısal `objection_id` kimliklerinin zorunlu olduğu.
- Snapshot alıntı kontrolünün iddiayı değil alıntıyı kanıtladığı; etiketin 'doğrulandı' yerine 'Alıntı Eşleşti' olması gerektiği.
- Docker/chroot sandbox'ının sıfır bağımlılığı bozacağı ve ilk aşamada reddedilmesi gerektiği.
- Tur 3'ün (Münazara), modellerin uyum eğilimini (sycophancy) kırmak için protokolün vazgeçilmez omurgası olduğu ve asla atlanamayacağı (Antigravity'nin itirazı sonrası Codex ve Claude tarafından onaylandı).
- `resume` komutunun `dispatched` işaretli işleri asla otomatik tekrarlamaması ve dokümantasyondaki 'en fazla 8 çağrı' ifadesinin '8 ilk çağrı + kullanıcı onaylı retry' olarak düzeltilmesi.
- README'deki Türkçe 47 / İngilizce 51 test sayısı çelişkisinin giderilmesi gerektiği.

## Dissent

Katılımcılar arasında çözülemeyen ayrılıklar ve şerhler:
- **Koşullu Tur 4 Atlama:** Codex ve Claude, 3. tur sonunda açık bir itiraz kalmadığında `init` anında seçilen opt-in bir politikayla 4. turun atlanıp doğrudan Sentez'e geçilebileceğini savunmaktadır. Antigravity ise bu karmaşıklığın getireceği marjinal hız kazancına karşı tavizsiz ve statik 5 tur disiplininin güvenilirlik açısından korunması gerektiğini savunarak şerh koymuştur.
- **`resume` Yetki Sınırı:** Claude `resume`ın yalnızca model çağırmayan adımları işletip durmasını savunurken; Antigravity ve Codex, açık kullanıcı onayları eşliğinde süreci devralan interaktif bir kurtarma sihirbazı olmasını savunmaktadır.
- **Genişletme Mimarisi:** Codex dar bir OOP adaptör arayüzü önerirken, Claude ve Antigravity bunun erken bir soyutlama (YAGNI) olduğunu, sadece basit argv şablonunun yeterli olduğunu savunmuştur.

## Uncertainties

Doğrulanamayan varsayımlar ve açık limitler:
- Kaynak snapshot'ında `cogitor.py` uygulama kodu bulunmadığından, mevcut 4. tur şablonlarının yapısal veri alanlarını destekleme kapasitesi, state atomikliği ve gerçek test sayısı harici olarak doğrulanamamıştır.
- Tur 4'ü atlamanın sağladığı maliyet/zaman tasarrufunun, karar güvenilirliğine ve kod karmaşıklığına etkisi henüz ampirik verilerle ölçülmemiştir.

## Comparison Matrix

| Participant | Round 1 Initial Stance | Round 4 Final Position | Status |
|---|---|---|---|
| `codex` | Benim öncelik sıram şöyledir: | ### Nihai pozisyon | Active |
| `claude` | # Claude — Tur 1: Bağımsız Analiz | # Claude: Tur 4, Nihai Pozisyon | Active |
| `antigravity` | ### Pozisyon ve Temel Tez | ### Nihai Pozisyon ve İtirazlara Yanıtlar | Active |

## Metrics

- **Total Duration:** 194.01s
- **Participants:** 3/3 (complete)
- **Chair:** `antigravity`
- **`codex`:** R1:23.67s, R2:19.39s, R3:21.32s, R4:27.19s
- **`claude`:** R1:30.09s, R2:20.75s, R3:23.33s, R4:22.77s
- **`antigravity`:** host-unmetered
