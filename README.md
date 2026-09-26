# Cogitor

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
  <a href="https://github.com/erayendes/cogitor/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/erayendes/cogitor/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="Python: 3.9+" src="https://img.shields.io/badge/python-3.9+-blue.svg">
  <img alt="Zero dependencies" src="https://img.shields.io/badge/dependencies-0-brightgreen.svg">
  <a href="https://agentskills.io"><img alt="Agent Skills" src="https://img.shields.io/badge/Agent%20Skills-compatible-purple.svg"></a>
</p>

🇹🇷 [Türkçe](#cogitor-t%C3%BCrk%C3%A7e) · 🇬🇧 [English](#cogitor-english)

---

# Cogitor (Türkçe)

Kritik bir mimari tercih, güvenlik denetimi veya ürün kararı gerektiğinde tek bir yapay zekaya danışmak risklidir: Model kendi halüsinasyonlarının, önyargılarının ve kör noktalarının farkına varamaz; hatalı varsayımlarını son derece özgüvenli bir üslupla savunabilir.

**Cogitor**, önde gelen üç büyük model ailesini — **Codex (OpenAI)**, **Claude (Anthropic)** ve **Antigravity (Google)** — tek bir müzakere masasında bir araya getirir. Üç modele de aynı işin tamamı verilir. Dört tur boyunca bağımsız analiz yapar, birbirlerinin görüşlerini okur, itirazlara kanıtla yanıt verir ve beşinci turda başkan tek bir gerekçeli karar sentezler.

> **En önemli ilke:** Görüş birliği (konsensüs) doğruluk kanıtı değildir.
> Makul ve gerekçeli azınlık görüşleri ile belirsizlikler bastırılmaz; nihai kararda aynen korunur.

---

## Dört Skill, İki Seviye

| Çağrı | Davranış |
|---|---|
| `/codex <görev>` | Yalnızca Codex çağrılır. |
| `/claude <görev>` | Yalnızca Claude Code çağrılır. |
| `/antigravity <görev>` | Yalnızca Antigravity çağrılır. |
| `/cogitor <görev>` | Üç ajan birlikte 5 turlu müzakere protokolünü yürütür. |

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
└──────────────────────────────────────────────────────┘
                           │
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
  ├── cogitor-antigravity-mimir-ui-sadelestirme.md
  ├── cogitor-claude-mimir-ui-sadelestirme.md
  ├── cogitor-codex-mimir-ui-sadelestirme.md
  ├── cogitor-final-mimir-ui-sadelestirme.json
  └── cogitor-final-mimir-ui-sadelestirme.md
```

* **Arama Dostu:** IDE'nizde (`Cmd+P`) `cogitor final` veya `mimir codex` yazdığınızda doğrudan ilgili oturuma ve dosyaya ulaşırsınız.
* **Lazy Creation:** İptal edilen veya başlamayan oturumlar arkasında boş klasör bırakmaz; dizin ilk çıktının başarıyla yazıldığı an açılır.
* **Dil Koruma:** Göreviniz veya kaynak dosyanız hangi dildeyse (Türkçe, İngilizce vb.), tüm ajanlar ve nihai rapor o dilde üretilir.

---

## Kurulum ve Paketleme

### Gereksinimler
* Python 3.9+ (macOS veya Linux). **Harici hiçbir pip bağımlılığı yoktur.**
* `codex`, `claude` ve `agy` CLI araçlarının kurulu ve giriş yapılmış olması.

### Derleme (Build)
Dört bağımsız skill paketini derlemek için:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/package_skills.py --output dist
```

Bu komut `dist/` klasörü altına kurulabilir 4 klasör (`cogitor`, `codex`, `claude`, `antigravity`) ve her birinin `.skill` zip arşivini üretir.

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
/cogitor Bu mimari öneriyi birlikte inceleyin. Kodları değiştirmeyin ve çözülemeyen itirazları açıkça belirtin.
/codex Kimlik doğrulama akışındaki açıkları kod değiştirmeden listele.
/claude Bu PR diff'indeki performans darboğazlarını analiz et.
/antigravity Bu teknik şartnamede çelişen maddeleri bul.
```

---

## Sınırlar, Maliyet ve Güvenlik

* **Sınırlandırılmış Maliyet:** Tam bir oturum en fazla **8 harici CLI çağrısı** yapar (2 danışman × 4 tur). Başkan kendi oturumunda çalışır. Sonsuz döngü, gizli retry veya başka bir model sağlayıcısına sessizce geçiş yoktur.
* **Kaynak Güvenliği:** Deliberasyon kaynak kodları doğrudan düzenleme yetkisi vermez. Kaynak dosyalar turlar arasında hash kontrolünden geçer; kaynak değişirse oturum durdurulur.
* **Dürüst Hata:** Bir danışman çökerse kullanıcıya sorulur (`continue-partial` veya `stop`). En az 2 katılımcı olmadan oturum sürdürülmez.
* **Zaman Sınırı:** Çağrı başına varsayılan 180 saniye, toplam oturum için 1800 saniye (`--timeout` ve `--total-timeout` ile ayarlanabilir).

---

## Testler

Tüm akış, model çağrısı yapmadan yerel simüle ortamda test edilir:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

41 testlik süit; beş tur veri akışını, başkan bağımsızlık kapılarını, slug üretimini, süreç iptallerini ve paketlemeyi doğrular.

---

# Cogitor (English)

When a critical architecture choice, security review, or product decision is on the line, consulting a single AI model is risky: a solitary model cannot see its own blind spots, hallucinations, or biases, often defending flawed premises with persuasive confidence.

**Cogitor** convenes the industry's three leading frontier models — **Codex (OpenAI)**, **Claude (Anthropic)**, and **Antigravity (Google)** — around a single deliberative table. Each participant receives the entire task. Across four rounds they analyze independently, critique peer positions, address objections with evidence, and in round five the chair synthesizes one defensible decision.

> **Core Principle:** Consensus is not proof of correctness. Reasoned minority opinions and explicit uncertainties are never suppressed; they are preserved in the final synthesis.

---

## Four Skills, Two Levels

| Invocation | Behavior |
|---|---|
| `/codex <task>` | Codex only. |
| `/claude <task>` | Claude Code only. |
| `/antigravity <task>` | Antigravity only. |
| `/cogitor <task>` | All three participants, using the five-round protocol. |

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
├── cogitor-antigravity-mimir-ui-simplification.md
├── cogitor-claude-mimir-ui-simplification.md
├── cogitor-codex-mimir-ui-simplification.md
├── cogitor-final-mimir-ui-simplification.json
└── cogitor-final-mimir-ui-simplification.md
```

* **Fuzzy-Search Friendly:** Typing `cogitor final` or `mimir codex` in your editor quick-open (`Cmd+P`) jumps directly to the right decision.
* **Lazy Creation:** Aborted or cancelled sessions leave no empty directories behind; the folder is created only when the first completed round is written.
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

This outputs four ready-to-install folders (`cogitor`, `codex`, `claude`, `antigravity`) and their `.skill` ZIP archives in `dist/`.

### Installation Paths

| Agent / Host | Skill Directory |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Antigravity | `~/.gemini/config/skills/` |
| Agent Skills Standard | `~/.agents/skills/` |

---

## Bounded Cost, Safety & Honest Failures

* **Bounded Cost:** At most **eight external CLI invocations** per session (2 advisors × 4 rounds). The chair deliberates within its existing host. No recursive delegation, no automatic retries, and no silent provider fallbacks.
* **Source Integrity:** Deliberation does not authorize file edits. Source snapshots are verified between rounds; any modified source blocks further dispatch.
* **Honest Failures:** If an external advisor fails, the host pauses for the user's decision (`continue-partial` or `stop`). Fewer than two participants halts deliberation.
* **Budgets:** Default 180s per call, 1800s total dispatch deadline (configurable via `--timeout` and `--total-timeout`).

---

## Development & Verification

Run the full offline test suite:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

The 41 unit tests verify round sequencing, host independence gates, slug extraction, process cleanup, and portable packaging without calling any live AI APIs.

---

## Acknowledgments & Inspiration

Named after the contemplative philosophers in Frank Herbert's *Dune*. Independent project inspired by [claude-council](https://github.com/hex/claude-council), [cc-debate](https://github.com/STRML/cc-debate), [LLM Council](https://github.com/karpathy/llm-council), and [CouncilKit](https://github.com/albertofettucini/CouncilKit).

---

## License

[MIT](LICENSE) © [Eray Endes](https://github.com/erayendes)
