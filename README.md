# The Cogitors

> “Sıradan algının gözleri uzağı göremez. Çoğu zaman en önemli kararlarımızı yalnızca yüzeysel bilgilere dayanarak alırız.”
> 
> "The eyes of common perception do not see far. Too often we make the most important decisions based only on superficial information."
>
> — Cogitor Kwyna

Codex, Claude ve Antigravity aynı görevi bağımsız inceler, birbirine meydan okur ve tek bir gerekçeli karar üretir.  
*Codex, Claude and Antigravity independently examine the same task, challenge each other across five rounds, and synthesize one supported decision.*

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
  <a href="https://milowda.com"><img alt="Yerli üretim" src="https://img.shields.io/badge/YERL%C4%B0%20%C3%9CRET%C4%B0M-red?style=flat&label=%F0%9F%A4%9D&color=red&link=https%3A%2F%2Fmilowda.com"></a>
  <a href="https://github.com/erayendes/cogitors/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/erayendes/cogitors/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="Python: 3.9+" src="https://img.shields.io/badge/python-3.9+-blue.svg">
  <img alt="Zero dependencies" src="https://img.shields.io/badge/dependencies-0-brightgreen.svg">
  <a href="https://agentskills.io"><img alt="Agent Skills" src="https://img.shields.io/badge/Agent%20Skills-compatible-purple.svg"></a>
</p>

🇹🇷 [Türkçe](#the-cogitors-t%C3%BCrk%C3%A7e) · 🇬🇧 [English](#the-cogitors-english)

---

# The Cogitors (Türkçe)

Kritik bir mimari tercih, güvenlik denetimi veya ürün kararı gerektiğinde tek bir yapay zekaya danışmak risklidir: Model kendi halüsinasyonlarının, önyargılarının ve kör noktalarının farkına varamaz; hatalı varsayımlarını son derece özgüvenli bir üslupla savunabilir.

**The Cogitors**, sektörün önde gelen üç büyük model ailesini — **Codex (OpenAI)**, **Claude (Anthropic)** ve **Antigravity (Google)** — tek bir müzakere masasında bir araya getirir. Üç modele de aynı işin tamamı verilir. Dört tur boyunca bağımsız analiz yapar, birbirlerinin görüşlerini okur, itirazlara kanıtla yanıt verir ve beşinci turda başkan tek bir gerekçeli karar sentezler.

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

Bunlar yeni terminal komutları değil, **Agent Skills** standartlı skill çağrılarıdır. Oturumu başlatan ajan oturuma başkanlık eder **ve müzakereye bizzat katılır**; fazladan dördüncü bir kopya model çalıştırılmaz.

---

## Beş Tur Protokolü

```text
               ┌───────────────────────┐
               │    Kullanıcı Görevi   │
               └───────────┬───────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Round 1:     │    │ Round 1:     │    │ Round 1:     │
│ Codex        │    │ Claude       │    │ Antigravity  │
│ (Bağımsız)   │    │ (Bağımsız)   │    │ (Bağımsız)   │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
┌──────────────────────────────────────────────────────┐
│ Round 2: Yeniden Değerlendirme                       │
│ Codex               Claude              Antigravity  │
│ (Bağımsız)          (Bağımsız)          (Bağımsız)   │
└──────────────────────────┬───────────────────────────┘
                           ▼
               ┌───────────────────────┐
               │ Round 3: Münazara &   │
               │ İtirazlar             │
               └───────────┬───────────┘
                           ▼
               ┌───────────────────────┐
               │ Round 4: Nihai        │
               │ Pozisyonlar           │
               └───────────┬───────────┘
                           ▼
               ┌───────────────────────┐
               │ Round 5: Başkan       │
               │ Sentezi (Tek Karar)   │
               └───────────────────────┘
```

1. **Bağımsız Analiz:** Üç ajan da aynı görev ve kaynak dosyalar üzerinde analizini yapar; akran yanıtları bu turda gizlidir.
2. **Yeniden Değerlendirme:** Ajanlar ilk turdaki akran görüşlerini okur; neyin değiştiğini veya neden değişmediğini gerekçeleriyle açıklar.
3. **Münazara (Meydan Okuma):** İddialar somut kanıtlarla ve doğrudan sorularla test edilir.
4. **Nihai Pozisyon:** İtirazlara cevap verilir ve son duruş belirlenir.
5. **Sentez:** Başkan rolündeki ajan tüm turları ve son düzeltmeleri birleştirerek; uzlaşmaları, ayrışan azınlık görüşlerini ve belirsizlikleri tek bir çıktıda toplar.

---

## Karar Çıktıları ve Dizin Yapısı

Her oturum, projenizin `docs/cogitors-decisions/` dizini altında tarih ve konu slug'ı ile adlandırılmış bir klasörde saklanır:

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

* **Arama Dostu:** IDE'nizde (`Cmd+P`) `decision` veya `mimir codex` yazdığınızda doğrudan ilgili oturuma ve dosyaya ulaşırsınız.
* **İnteraktif HTML Raporu & .MD Dışa Aktarma:** `decisions-*.html` tek dosyalık, harici kütüphanesiz bir karar paneli sunar. Cihaz temasına otomatik uyum (dark/light), karşılaştırma matrisi, zengin biçimlendirilmiş münazara zaman tüneli ve doğrudan `.md` indirme/kopyalama butonları içerir.
* **Lazy Creation:** İptal edilen veya başlamayan oturumlar arkasında boş klasör bırakmaz; dizin ilk çıktının başarıyla yazıldığı an açılır.
* **Dil Koruma & Çok Dilli Şablonlar:** Göreviniz veya kaynak dosyanız hangi dildeyse (Türkçe, İngilizce vb.), prompt kılavuzları otomatik uyarlanır, tüm ajanlar ve nihai rapor o dilde üretilir.
* **Kanıt Dosyası:** `--evidence-file rapor.txt` ile kendi çalıştırdığınız test/lint çıktısı Tur 1'den itibaren tüm danışmanlara verilir; hash'lenir, Cogitors komut çalıştırmaz. Redaksiyon yapılmaz, gizli veriyi önceden temizleyin.
* **Git Entegrasyonu:** `--git-diff` veya `--git-staged` bayraklarıyla çalışma dizini veya stage edilmiş değişiklikler otomatik olarak snapshot alınır.

---

## Kurulum ve Tanı

### Model Keşfi ve İnteraktif Seçim (Heimdall Tarzı)
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
Her `init` komutunda oturum başkanı, konu, heyet üyeleri, modelleri ve çalışma dizinini özetleyen şık bir Header Banner terminalde ve sohbette otomatik gösterilir. İstenildiği an tekrar çağrılabilir:

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

```text
/cogitors Bu mimari öneriyi birlikte inceleyin. Kodları değiştirmeyin ve çözülemeyen itirazları açıkça belirtin.
/cogitors --git-diff HEAD~1 Bu PR'daki değişiklikleri güvenlik ve performans açısından müzakere edin.
/codex Kimlik doğrulama akışındaki açıkları kod değiştirmeden listele.
/claude Bu PR diff'indeki performans darboğazlarını analiz et.
/antigravity Bu teknik şartnamede çelişen maddeleri bul.
```

---

## Sınırlar, Maliyet ve Güvenlik

* **Sınırlandırılmış Maliyet:** Tam bir oturum **8 ilk harici CLI çağrısı** yapar (2 danışman × 4 tur); onaylı `extend-timeout` retry'ları tur başına en fazla 2 kez eklenir. Gönderim öncesi `status.scope` sağlayıcıları, dosya/bayt sayısını ve azami çağrıyı gösterir; kullanıcı tek seferde onaylar (`approve`). Başkan kendi oturumunda çalışır. Sonsuz döngü, gizli retry veya başka bir model sağlayıcısına sessizce geçiş yoktur.
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

60 testlik süit; beş tur veri akışını, başkan bağımsızlık kapılarını, slug üretimini, süreç iptallerini, doktor tanısını, ikili meclisi, HTML karar görselleştiricisini ve paketlemeyi doğrular.

---

# The Cogitors (English)

When a critical architecture choice, security review, or product decision is on the line, consulting a single AI model is risky: a solitary model cannot see its own blind spots, hallucinations, or biases, often defending flawed premises with persuasive confidence.

**The Cogitors** convenes the industry's three leading frontier models — **Codex (OpenAI)**, **Claude (Anthropic)**, and **Antigravity (Google)** — around a single deliberative table. Each participant receives the entire task. Across four rounds they analyze independently, critique peer positions, address objections with evidence, and in round five the chair synthesizes one defensible decision.

> **Core Principle:** Consensus is not proof of correctness. Reasoned minority opinions and explicit uncertainties are never suppressed; they are preserved in the final synthesis.

---

## Four Skills, Two Levels

| Invocation | Behavior |
|---|---|
| `/codex <task>` | Codex only. |
| `/claude <task>` | Claude Code only. |
| `/antigravity <task>` | Antigravity only. |
| `/cogitors <task>` | All three participants, using the five-round protocol. |

These are skill invocations conforming to the **Agent Skills** specification. The invoking agent chairs the session **and participates**; no fourth phantom model is launched.

---

## Five-Round Deliberation Protocol

1. **Independent Analysis:** Each participant analyzes the task and shared source snapshot without seeing peer opinions.
2. **Reconsideration:** Participants read the initial views and state what changed or remained unchanged, citing reasons.
3. **Debate:** Specific disputed claims are challenged directly with evidence and focused counter-questions.
4. **Final Positions:** Objections are accepted or rejected with justification, submitting a definitive stance.
5. **Synthesis:** The chair combines all final positions, explicitly reporting consensus, reasoned dissent, uncertainties, and participation status.

---

## Decision Artifacts & Directory Layout

Every session is saved under your project's `docs/cogitors-decisions/` directory, labeled with a timestamp and a descriptive topic slug:

```text
docs/cogitors-decisions/20260926-175500-mimir-ui-simplification/
├── antigravity-mimir-ui-simplification.md
├── brief-mimir-ui-simplification.md
├── claude-mimir-ui-simplification.md
├── codex-mimir-ui-simplification.md
├── decision-mimir-ui-simplification.md
└── decisions-mimir-ui-simplification.html
```

* **Fuzzy-Search Friendly:** Typing `decision` or `mimir codex` in your editor quick-open (`Cmd+P`) jumps directly to the right decision.
* **Interactive HTML Report & .MD Export:** `decisions-*.html` provides a standalone zero-dependency decision dashboard with automatic device dark/light theme, comparison matrix, rich-formatted timeline, and direct `.md` export.
* **Lazy Creation:** Aborted or cancelled sessions leave no empty directories behind; the folder is created only when the first completed round is written.
* **Evidence Files:** `--evidence-file report.txt` shares your own test/lint output with every advisor from round 1; it is hashed and frozen, and Cogitors never runs commands. It is not redacted; strip secrets first.
* **Language Preservation:** Whatever language your task or source file uses, all advisors and the final synthesis respond in that same language.

---

## Requirements & Packaging

### Requirements
* Python 3.9+ on macOS or Linux. **Zero external pip package dependencies.**
* Authenticated `codex`, `claude`, and `agy` CLIs installed locally.

### Build Portable Bundles
To package all four self-contained skills:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/package_skills.py --output dist
```

This outputs four ready-to-install folders (`cogitors`, `codex`, `claude`, `antigravity`) and their `.skill` ZIP archives in `dist/`.

### Installation Paths

| Agent / Host | Skill Directory |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Antigravity | `~/.gemini/config/skills/` |
| Agent Skills Standard | `~/.agents/skills/` |

---

## Bounded Cost, Safety & Honest Failures

* **Bounded Cost:** **Eight initial external CLI invocations** per session (2 advisors × 4 rounds), plus at most 2 user-approved `extend-timeout` retries per round. Before dispatch, `status.scope` lists providers, file/byte counts and the maximum call count; the user consents once (`approve`). The chair deliberates within its existing host. No recursive delegation, no automatic retries, and no silent provider fallbacks.
* **Source Integrity:** Deliberation does not authorize file edits. Source snapshots are verified between rounds; any modified source blocks further dispatch.
* **Honest Failures:** If an external advisor fails, the host pauses for the user's decision (`continue-partial` or `stop`). Fewer than two participants halts deliberation.
* **Budgets:** Default 180s per call, 1800s total dispatch deadline (configurable via `--timeout` and `--total-timeout`).
* **Streamlined Orchestration:** The `cycle` command runs host recording, dispatch, and advance in one atomic step per round.
* **Diagnostics:** `python3 skills/cogitors/scripts/cogitor.py doctor` verifies CLI presence and authentication across all providers.
* **Model Discovery & Heimdall Config:** `python3 skills/cogitors/scripts/cogitor.py models` lists installed CLIs and available models; `configure -i` provides an interactive terminal picker to save default preferences. Direct CLI flags (`--codex-model`, `--claude-model`, etc.) allow effortless overrides.
* **Session Header Banner:** `init` prints a formatted session banner (with chair, topic, participants, and models) to stderr and chat; view anytime with `banner RUN_DIR [--markdown]`.

---

## Development & Verification

Run the full offline test suite:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

The 60 unit tests verify round sequencing, host independence gates, slug extraction, process cleanup, doctor preflights, two-agent council, interactive HTML decision viewer, model configuration catalogs, session banners, and portable packaging without calling any live AI APIs.

---

## Acknowledgments & Inspiration

Named after the contemplative philosophers in Frank Herbert's *Dune*. 

---

## License

[MIT](LICENSE) © [Eray Endes](https://github.com/erayendes)
