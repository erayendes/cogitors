# The Cogitors

> “Sıradan algının gözleri uzağı göremez. Çoğu zaman en önemli kararlarımızı yalnızca yüzeysel bilgilere dayanarak alırız.”
> 
> — Cogitor Kwyna

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/logo-dark.svg">
    <img alt="The Cogitors" src="../assets/logo.svg" width="420">
  </picture>
</p>

<p align="center">
  <a href="../LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
  <a href="https://milowda.com"><img alt="Yerli üretim" src="https://img.shields.io/badge/YERL%C4%B0%20%C3%9CRET%C4%B0M-red?style=flat&label=%F0%9F%A4%9D&color=red&link=https%3A%2F%2Fmilowda.com"></a>
  <a href="https://github.com/erayendes/cogitors/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/erayendes/cogitors/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="Python: 3.9+" src="https://img.shields.io/badge/python-3.9+-blue.svg">
  <img alt="Zero dependencies" src="https://img.shields.io/badge/dependencies-0-brightgreen.svg">
  <a href="https://agentskills.io"><img alt="Agent Skills" src="https://img.shields.io/badge/Agent%20Skills-compatible-purple.svg"></a>
</p>

🇬🇧 [English](../README.md)

---

Kritik bir mimari tercih, güvenlik denetimi veya ürün kararı gerektiğinde tek bir yapay zekaya danışmak risklidir: Model kendi halüsinasyonlarının, önyargılarının ve kör noktalarının farkına varamaz; **hatalı varsayımlarını son derece özgüvenli bir üslupla savunabilir.**

**The Cogitors**, üç büyük model ailesini — **Codex (OpenAI)**, **Claude (Anthropic)** ve **Antigravity (Google)** — tek bir müzakere masasında bir araya getirir. 
Üç modele de aynı işin tamamı verilir. Dört tur boyunca bağımsız analiz yapar, birbirlerinin görüşlerini okur, itirazlara kanıtla yanıt verirler. Beşinci turda Elder tek bir gerekçeli karar sentezler.

> **En önemli ilke:** Görüş birliği (konsensüs) doğruluk kanıtı değildir.
> Makul ve gerekçeli azınlık görüşleri ile belirsizlikler bastırılmaz; nihai kararda aynen korunur.

---

## Dört Skill, İki Seviye

| Çağrı | Davranış |
|---|---|
| `/codex <görev>` | Yalnızca Codex çağrılır. |
| `/claude <görev>` | Yalnızca Claude Code çağrılır. |
| `/antigravity <görev>` | Yalnızca Antigravity çağrılır. |
| `/cogitors <görev>` | Üç ajan birlikte 5 turlu müzakere protokolünü yürütür. |

Bunlar yeni terminal komutları değil, **Agent Skills** standartlı skill çağrılarıdır. Oturumu başlatan ajan Elder olur, oturumu yönetir **ve müzakereye bizzat katılır**; fazladan dördüncü bir kopya model çalıştırılmaz.

---

## Beş Tur Protokolü

```text
                 ┌───────────────────────┐
                 │    /cogitors <task>   │
                 └───────────┬───────────┘
Tur 1: Bağımsız Analiz       ▼
──────────────────────────────────────────────────────────
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │    Codex    │   │ Antigravity │   │   Claude    │
   └─────────────┘   └─────────────┘   └─────────────┘
─────────────────────────────┬────────────────────────────
                             ▼
                 ┌───────────────────────┐
                 │  Taslakların Açılması │
                 └───────────┬───────────┘
Tur 2: Yeniden Değerlendirme ▼
──────────────────────────────────────────────────────────
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │    Codex    │   │ Antigravity │   │   Claude    │
   └─────────────┘   └─────────────┘   └─────────────┘
─────────────────────────────┬────────────────────────────
Tur 3: Münazara              ▼
──────────────────────────────────────────────────────────
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │    Codex    │─x─│ Antigravity │─x─│   Claude    │
   └─────────────┘   └─────────────┘   └─────────────┘
─────────────────────────────┬────────────────────────────
Tur 4: Nihai Pozisyon        ▼
──────────────────────────────────────────────────────────
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │    Codex    │   │ Antigravity │   │   Claude    │
   └─────────────┘   └─────────────┘   └─────────────┘
─────────────────────────────┐
Tur 5: Sentez                ▼
──────────────────────┬──────────────┐
                      │    Elder     │
                      └──────────────┘
```

1. **Bağımsız Analiz:** Üç ajan da aynı görev ve kaynak dosyalar üzerinde analizini yapar. Bu turda hiçbiri diğerinin çalışmasını görmez.
2. **Yeniden Değerlendirme:** Ajanlar ilk turdaki akran görüşlerini okur. Kendi ön analizlerini akranların görüşlerine göre revize eder ya da etmez.
3. **Münazara:** Her bir ajan kendi görüşünü somut kanıtlarla savunur. Varsa diğer görüşlere itiraz eder.
4. **Nihai Pozisyon:** İtirazlara cevap verilir ve son duruş belirlenir.
5. **Sentez:** Elder ajan tüm turları ve son düzeltmeleri birleştirerek; uzlaşmaları, ayrışan azınlık görüşlerini ve belirsizlikleri tek bir çıktıda toplar.

---

## Karar Çıktıları ve Dizin Yapısı

Her oturum, projenizin `docs/cogitors-decisions/` dizini altında saklanır:

```text
<project-root>
  docs/cogitors-decisions/20260926-175500-mimir-ui-sadelestirme/
  ├── antigravity-mimir-ui-sadelestirme.md
  ├── brief-mimir-ui-sadelestirme.md
  ├── claude-mimir-ui-sadelestirme.md
  ├── codex-mimir-ui-sadelestirme.md
  ├── decision-mimir-ui-sadelestirme.md
  └── decisions-mimir-ui-sadelestirme.html
```

* **Arama Dostu:** `decision` veya `mimir codex` yazdığınızda doğrudan ilgili oturuma ve dosyaya ulaşırsınız.
* **İnteraktif HTML Raporu:** `decisions-*.html` tek dosyalık, harici kütüphanesiz bir karar paneli sunar. **Özet** sekmesinde heyet tablosu (tur başına süre ve CLI'ın raporladığı token), Kararlar (Uzlaşı, Gerekçeli Ayrışma, Belirsizlikler) ve P0/P1/P2 Aksiyonlar; **Matrix** sekmesinde her Cogitor'ın tur tur duruşu; her Cogitor'ın kendi sekmesinde dört turun tam metni yer alır. Token tahmin edilmez: CLI raporlamadıysa gösterilmez.
* **Lazy Creation:** İptal edilen veya başlamayan oturumlar arkasında boş klasör bırakmaz; dizin ilk çıktının başarıyla yazıldığı an açılır.
* **Dil Koruma & Çok Dilli Şablonlar:** Göreviniz veya kaynak dosyanız hangi dildeyse (Türkçe, İngilizce vb.), prompt kılavuzları otomatik uyarlanır, tüm ajanlar ve nihai rapor o dilde üretilir.
* **Kanıt Dosyası:** `--evidence-file rapor.txt` ile kendi çalıştırdığınız test/lint çıktısı Tur 1'den itibaren tüm danışmanlara verilir; hash'lenir, Cogitors komut çalıştırmaz. Redaksiyon yapılmaz.

> [!WARNING]
> Dosyanızda varsa gizli veriyi önceden temizleyin.

* **Git Entegrasyonu:** `--git-diff` veya `--git-staged` bayraklarıyla çalışma dizini veya stage edilmiş değişiklikler otomatik olarak snapshot alınır.
* **Elder Modeli:** Runner, Elder'ın modelini bilemez. `--chair-model` ile host kendi modelini bildirir; raporda "host bildirdi" olarak işaretlenir.
* **Sıradaki Adım:** `status.next_action` mevcut duruma göre tek güvenli komutu ya da kullanıcıya sorulacak seçenekleri verir. Sonucu belirsiz bir çağrıyı asla otomatik tekrarlamaz.

---

## Kurulum ve Tanı

### Model Keşfi ve İnteraktif Seçim ([Heimdall](https://github.com/erayendes/app-store-connect-mcp) Tarzı)
Artık karmaşık JSON yapılarıyla uğraşmak zorunda değilsiniz:

1. **Kurulu Modelleri Listeleme:**
   ```sh
   python3 skills/cogitors/scripts/cogitor.py models
   ```
   Sistemdeki kurulu CLI'ları (`codex`, `claude`, `agy`) ve kullanılabilir tüm modelleri (`agy models` dinamik listesi dahil) listeler.

2. **İnteraktif Model Seçici (Heimdall):**
   ```sh
   python3 skills/cogitors/scripts/cogitor.py configure -i
   ```
   Terminalde numaralı menü ile Codex, Claude ve Antigravity için tercih ettiğiniz model ve reasoning effort (akıl yürütme seviyesi) ayarlarını seçmenizi sağlar ve `~/.cogitors/config.json` içine varsayılan profil olarak kaydeder. Sonraki tüm oturumlar bu tercihleri otomatik kullanır!

3. **Doğrudan CLI Bayrakları:**
   ```sh
   python3 skills/cogitors/scripts/cogitor.py init /path/brief.md --chair antigravity --cwd "$PWD" \
     --codex-model o3 --codex-effort high \
     --claude-model sonnet
   ```

### Oturum Başlık Banner'ı (Session Header)
Her `init` komutunda Elder, konu, heyet üyeleri, modelleri ve çalışma dizinini özetleyen şık bir Header Banner terminalde ve sohbette otomatik gösterilir. İstenildiği an tekrar çağrılabilir:

```sh
python3 skills/cogitors/scripts/cogitor.py banner /path/run [--markdown]
```

### Tanı Aracı (Doctor)
Tüm CLI araçlarının kurulu, giriş yapılmış ve meclis oturumuna hazır olduğunu doğrulamak için:

```sh
python3 skills/cogitors/scripts/cogitor.py doctor
```

### Gereksinimler
* Python 3.9+ (macOS veya Linux). **Harici hiçbir pip bağımlılığı yoktur.**
* `codex`, `claude` ve `agy` CLI araçlarının kurulu ve giriş yapılmış olması (en az iki ajan ikili meclis için yeterlidir).

### Derleme (Build)
Dört bağımsız skill paketini derlemek için:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/package_skills.py --output dist
```

Bu komut `dist/` klasörü altına kurulabilir 4 klasör (`cogitors`, `codex`, `claude`, `antigravity`) ve her birinin `.skill` zip arşivini üretir.

### Yükleme Konumları
Derlenen klasörleri kullandığınız ajanın skill klasörüne kopyalamanız yeterlidir:

| Ajan / Ortam | Skill Dizin Yolu |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Antigravity | `~/.gemini/config/skills/` |
| Agent Skills Standardı | `~/.agents/skills/` |

---

## Kullanım Örnekleri

> - `/cogitors` Bu mimari öneriyi birlikte inceleyin. Kodları değiştirmeyin ve çözülemeyen itirazları açıkça belirtin.
> - `/cogitors` `--git-diff HEAD~1` Bu PR'daki değişiklikleri güvenlik ve performans açısından müzakere edin.
> - `/codex` Kimlik doğrulama akışındaki açıkları kod değiştirmeden listele.
> - `/claude` Bu PR diff'indeki performans darboğazlarını analiz et.
> - `/antigravity` Bu teknik şartnamede çelişen maddeleri bul.

---

## Sınırlar, Maliyet ve Güvenlik

* **Sınırlandırılmış Maliyet:** Tam bir oturum **8 ilk harici CLI çağrısı** yapar (2 danışman × 4 tur); onaylı `extend-timeout` retry'ları tur başına en fazla 2 kez eklenir. Gönderim öncesi `status.scope` sağlayıcıları, dosya/bayt sayısını ve azami çağrıyı gösterir; kullanıcı tek seferde onaylar (`approve`). Elder kendi oturumunda çalışır. Sonsuz döngü, gizli retry veya başka bir model sağlayıcısına sessizce geçiş yoktur.
* **Kaynak Güvenliği:** Deliberasyon kaynak kodları doğrudan düzenleme yetkisi vermez. Kaynak dosyalar turlar arasında hash kontrolünden geçer; kaynak değişirse oturum durdurulur.
* **Dürüst Hata:** Bir danışman çökerse kullanıcıya sorulur (`continue-partial` veya `stop`). En az 2 katılımcı olmadan oturum sürdürülmez.
* **Zaman Sınırı:** Çağrı başına varsayılan 180 saniye, toplam oturum için 1800 saniye (`--timeout` ve `--total-timeout` ile ayarlanabilir).
* **Tek Adımlı Orkestrasyon:** Tur başına `cycle` komutuyla kayıt, çalıştırma ve ilerletme tek adımda güvenle yürütülebilir.

---

## Testler

Tüm akış, model çağrısı yapmadan yerel simüle ortamda test edilir:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

61 testlik süit; beş tur veri akışını, Elder bağımsızlık kapılarını, slug üretimini, süreç iptallerini, doktor tanısını, ikili meclisi, HTML karar görselleştiricisini ve paketlemeyi doğrular.

## Meraklısına İsmin Hikayesi

**Cogitor**'lar, Dune evreninde bedenlerinden ayrılıp koruyucu bir sıvı içinde **binlerce yılı düşünmeye adayan** kadim zihinlerdir. 
Bir sonuca acele etmeden, uzun uzun düşünüp tartıştıktan sonra varırlar. 
Bu proje de adını onlardan alıyor: birden fazla model aynı soruyu acele etmeden, kendilerini ve birbirlerini sorgulayarak düşünür. 

---

## Lisans

[MIT](../LICENSE) © [Eray Endes](https://github.com/erayendes)

---

<p align="center">
  <a href="https://github.com/erayendes/cogitors/issues/new?template=bug_report.yml">Hata bildir</a> ·
  <a href="https://github.com/erayendes/cogitors/issues/new?template=feature_request.yml">Özellik iste</a> ·
  <a href="../.github/SUPPORT.md">Destek</a> ·
  <a href="../.github/SECURITY.md">Güvenlik</a> ·
  <a href="../.github/CONTRIBUTING.md">Katkı</a>
</p>
