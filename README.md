# The Cogitors

> “Sıradan algının gözleri uzağı göremez. Çoğu zaman en önemli kararlarımızı yalnızca yüzeysel bilgilere dayanarak alırız.”
> 
> "The eyes of common perception do not see far. Too often we make the most important decisions based only on superficial information."
>
> — Cogitor Kwyna

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg">
    <img alt="The Cogitors" src="assets/logo.svg" width="420">
  </picture>
</p>

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

# The Cogitors (English)

When a critical architecture choice, security review or product decision is on the line, consulting a single AI is risky: a model cannot see its own hallucinations, biases and blind spots, and **it can defend flawed assumptions with complete confidence.**

**The Cogitors** brings three major model families — **Codex (OpenAI)**, **Claude (Anthropic)** and **Antigravity (Google)** — to one deliberation table.
Every model receives the whole task. Over four rounds they analyze independently, read each other's views and answer objections with evidence. In round five the Elder synthesizes one reasoned decision.

> **Core principle:** Consensus is not proof of correctness.
> Reasoned minority views and uncertainties are never suppressed; they are preserved in the final decision.

---

## Four Skills, Two Levels

| Invocation | Behavior |
|---|---|
| `/codex <task>` | Codex only. |
| `/claude <task>` | Claude Code only. |
| `/antigravity <task>` | Antigravity only. |
| `/cogitors <task>` | All three agents run the five-round deliberation protocol together. |

These are not new terminal commands but skill invocations following the **Agent Skills** standard. The agent that starts the session becomes the Elder, runs it **and takes part in the deliberation itself**; no extra fourth model is launched.

---

## Five-Round Protocol

```text
               ┌───────────────────────┐
               │   /cogitors <task>    │
               └───────────┬───────────┘
Round 1: Initial Analysis  ▼
────────────────────────────────────────────────────────
  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
  │    Codex    │   │ Antigravity │   │   Claude    │
  └─────────────┘   └─────────────┘   └─────────────┘
───────────────────────────┬────────────────────────────
                           ▼
               ┌───────────────────────┐
               │    Drafts Unsealed    │
               └───────────┬───────────┘
Round 2: Reconsideration   ▼
────────────────────────────────────────────────────────
  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
  │    Codex    │   │ Antigravity │   │   Claude    │
  └─────────────┘   └─────────────┘   └─────────────┘
───────────────────────────┬────────────────────────────
Round 3: Debate            ▼
────────────────────────────────────────────────────────
  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
  │    Codex    │─x─│ Antigravity │─x─│   Claude    │
  └─────────────┘   └─────────────┘   └─────────────┘
───────────────────────────┬────────────────────────────
Round 4: Final Position    ▼
────────────────────────────────────────────────────────
  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
  │    Codex    │   │ Antigravity │   │   Claude    │
  └─────────────┘   └─────────────┘   └─────────────┘
───────────────────────────┐
Round 5: Synthesis         ▼
────────────────────┬──────────────┐
                    │    Elder     │
                    └──────────────┘
```

1. **Initial Analysis:** All three agents analyze the same task and source files. In this round none of them sees the others' work.
2. **Reconsideration:** Agents read their peers' first-round views and revise their own initial analysis in light of them, or keep it.
3. **Debate:** Each agent defends its view with concrete evidence and objects to other views where it disagrees.
4. **Final Position:** Objections are answered and each agent sets its final stance.
5. **Synthesis:** The Elder combines all rounds and final corrections into one output with the agreements, the dissenting minority views and the uncertainties.

---

## Decision Outputs and Directory Layout

Every session is saved under your project's `docs/cogitors-decisions/` directory:

```text
<project-root>
  docs/cogitors-decisions/20260926-175500-mimir-ui-simplification/
  ├── antigravity-mimir-ui-simplification.md
  ├── brief-mimir-ui-simplification.md
  ├── claude-mimir-ui-simplification.md
  ├── codex-mimir-ui-simplification.md
  ├── decision-mimir-ui-simplification.md
  └── decisions-mimir-ui-simplification.html
```

* **Search Friendly:** Typing `decision` or `mimir codex` takes you straight to the right session and file.
* **Interactive HTML Report:** `decisions-*.html` is a single-file decision panel with no external libraries. The **Summary** tab holds the council table (per-round time and CLI-reported tokens), the Decisions (Consensus, Reasoned Dissent, Uncertainties) and P0/P1/P2 Actions; the **Matrix** tab shows each Cogitor's stance round by round; each Cogitor's own tab holds the full text of all four rounds. Tokens are never estimated: if a CLI did not report them, they are not shown.
* **Lazy Creation:** Cancelled or unstarted sessions leave no empty folders behind; the directory is created the moment the first output is written.
* **Language Preservation & Multilingual Templates:** Whatever language your task or source file is in (Turkish, English, etc.), prompt guides adapt automatically and all agents and the final report use that language.
* **Evidence File:** `--evidence-file report.txt` gives the test/lint output you ran yourself to every advisor from Round 1; it is hashed, and Cogitors never runs commands. It is not redacted.

> [!WARNING]
> Remove any secrets from your evidence file first.

* **Git Integration:** The `--git-diff` or `--git-staged` flags automatically snapshot working-tree or staged changes.
* **Elder Model:** The runner cannot know the Elder's model. The host reports it with `--chair-model`; the report marks it as self-reported.
* **Next Step:** `status.next_action` gives the one safe command for the current state, or the choices to put to the user. It never repeats a call whose outcome is unknown.

---

## Installation and Diagnostics

### Model Discovery and Interactive Selection ([Heimdall](https://github.com/erayendes/app-store-connect-mcp) Style)
No more wrestling with complex JSON:

1. **List Installed Models:**
   ```sh
   python3 skills/cogitors/scripts/cogitor.py models
   ```
   Lists the installed CLIs (`codex`, `claude`, `agy`) and all available models (including the dynamic `agy models` list).

2. **Interactive Model Picker (Heimdall):**
   ```sh
   python3 skills/cogitors/scripts/cogitor.py configure -i
   ```
   A numbered terminal menu lets you choose the model and reasoning effort for Codex, Claude and Antigravity, and saves them to `~/.cogitors/config.json` as your default profile. Every later session uses these preferences automatically.

3. **Direct CLI Flags:**
   ```sh
   python3 skills/cogitors/scripts/cogitor.py init /path/brief.md --chair antigravity --cwd "$PWD" \
     --codex-model o3 --codex-effort high \
     --claude-model sonnet
   ```

### Session Header Banner
Every `init` shows a header banner in the terminal and chat that summarizes the Elder, topic, council members, their models and the working directory. You can call it again at any time:

```sh
python3 skills/cogitors/scripts/cogitor.py banner /path/run [--markdown]
```

### Diagnostics (Doctor)
To confirm every CLI is installed, signed in and ready for a council session:

```sh
python3 skills/cogitors/scripts/cogitor.py doctor
```

### Requirements
* Python 3.9+ (macOS or Linux). **No external pip dependencies.**
* The `codex`, `claude` and `agy` CLIs installed and signed in (two agents are enough for a two-member council).

### Build
To build the four standalone skill packages:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/package_skills.py --output dist
```

This produces 4 installable folders (`cogitors`, `codex`, `claude`, `antigravity`) under `dist/` and a `.skill` zip archive for each.

### Installation Paths
Copy the built folders into your agent's skill directory:

| Agent / Host | Skill Directory |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Antigravity | `~/.gemini/config/skills/` |
| Agent Skills Standard | `~/.agents/skills/` |

---

## Usage Examples

> - `/cogitors` Review this architecture proposal together. Do not change any code, and state unresolved objections explicitly.
> - `/cogitors` `--git-diff HEAD~1` Deliberate on this PR's changes for security and performance.
> - `/codex` List the weaknesses in the authentication flow without changing code.
> - `/claude` Analyze the performance bottlenecks in this PR diff.
> - `/antigravity` Find the contradicting clauses in this technical spec.

---

## Limits, Cost and Safety

* **Bounded Cost:** A full session makes **8 initial external CLI calls** (2 advisors × 4 rounds); approved `extend-timeout` retries add at most 2 per round. Before dispatch, `status.scope` shows the providers, file/byte counts and maximum calls; the user approves once (`approve`). The Elder works inside its own session. There are no infinite loops, hidden retries or silent switches to another model provider.
* **Source Safety:** Deliberation grants no permission to edit source code. Source files are hash-checked between rounds; if a source changes, the session stops.
* **Honest Failures:** If an advisor fails, the user is asked (`continue-partial` or `stop`). A session never continues with fewer than 2 participants.
* **Time Limits:** 180 seconds per call by default and 1800 seconds for the whole session (adjustable with `--timeout` and `--total-timeout`).
* **Single-Step Orchestration:** The per-round `cycle` command records, dispatches and advances safely in one step.

---

## Tests

The whole flow is tested in a local simulated environment without calling any model:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

The 61-test suite verifies the five-round data flow, Elder independence gates, slug generation, process cancellation, doctor diagnostics, the two-member council, the HTML decision viewer and packaging.

## The Story Behind the Name

**Cogitors** are ancient minds in the Dune universe that left their bodies behind and, preserved in a protective fluid, **devote thousands of years to thought**.
They reach a conclusion only after thinking and debating at length, never in haste.
This project takes its name from them: several models think through the same question without haste, questioning themselves and each other.

---

## License

[MIT](LICENSE) © [Eray Endes](https://github.com/erayendes)

---

<p align="center">
  <a href="https://github.com/erayendes/cogitors/issues/new?template=bug_report.yml">Hata bildir · Report a bug</a> ·
  <a href="https://github.com/erayendes/cogitors/issues/new?template=feature_request.yml">Özellik iste · Request a feature</a> ·
  <a href=".github/SUPPORT.md">Destek · Support</a> ·
  <a href=".github/SECURITY.md">Güvenlik · Security</a> ·
  <a href=".github/CONTRIBUTING.md">Katkı · Contributing</a>
</p>
