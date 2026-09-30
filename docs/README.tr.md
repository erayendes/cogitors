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
  <a href="https://www.npmjs.com/package/cogitors"><img alt="npm" src="https://img.shields.io/npm/v/cogitors.svg"></a>
  <img alt="Python: 3.9+" src="https://img.shields.io/badge/python-3.9+-blue.svg">
  <img alt="Zero dependencies" src="https://img.shields.io/badge/dependencies-0-brightgreen.svg">
  <a href="https://agentskills.io"><img alt="Agent Skills" src="https://img.shields.io/badge/Agent%20Skills-compatible-purple.svg"></a>
</p>

🇬🇧 [English](../README.md)

---

Kritik bir mimari tercih, güvenlik denetimi veya ürün kararı gerektiğinde tek bir yapay zekaya danışmak risklidir: Model kendi halüsinasyonlarının, önyargılarının ve kör noktalarının farkına varamaz; **hatalı varsayımlarını son derece özgüvenli bir üslupla savunabilir.**

## Üç Model

**The Cogitors**, üç model ailesini — **Codex (OpenAI)**, **Claude (Anthropic)** ve **Antigravity (Google)** — tek bir müzakere masasında bir araya getirir. 
Üç modele de aynı işin tamamı verilir. Dört tur boyunca bağımsız analiz yapar, birbirlerinin görüşlerini okur, itirazlara kanıtla yanıt verirler. Beşinci turda Elder tek bir gerekçeli karar sentezler.

> **En önemli ilke:** Görüş birliği (konsensüs) doğruluk kanıtı değildir.
> Makul ve gerekçeli azınlık görüşleri ile belirsizlikler bastırılmaz; nihai kararda aynen korunur.

---

## Dört Skill

`/<model> <görev>` Codex, Antgravity ya da Claude göreve çağırılır ve arka planda işini halleder.

Ama `/cogitors <görev>` başka. Bu üç ajan birlikte 5 turlu müzakere protokolünü başlatır.

```text
- /antigravity Bu teknik şartnamede çelişen maddeleri bul.
- /claude Bu PR diff'indeki performans darboğazlarını analiz et.
- /codex Kimlik doğrulama akışındaki açıkları kod değiştirmeden listele.

- /cogitors Bu mimari öneriyi birlikte inceleyin. Kodları değiştirmeyin ve çözülemeyen itirazları açıkça belirtin.
- /cogitors --git-diff HEAD~1 Bu PR'daki değişiklikleri güvenlik ve performans açısından müzakere edin.
```

> [!NOTE]
> Bunlar yeni terminal komutları değil, standart **Agent Skills** çağrılarıdır. Oturumu başlatan ajan **Elder** olur, oturumu yönetir **ve müzakereye bizzat katılır**; fazladan dördüncü bir kopya model çalıştırılmaz.

---

## Beş Tur

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

1. **Bağımsız Analiz:** Her ajan görevi tek başına, diğerlerini görmeden inceler.
2. **Yeniden Değerlendirme:** Ajanlar birbirinin taslağını okur, isterse görüşünü günceller.
3. **Münazara:** Her ajan görüşünü kanıtla savunur ve katılmadığı görüşlere itiraz eder.
4. **Nihai Pozisyon:** İtirazlar yanıtlanır, her ajan son duruşunu belirler.
5. **Sentez:** Elder, uzlaşmaları, azınlık görüşlerini ve belirsizlikleri tek kararda toplar.

---

## Karar Çıktıları ve Dizin Yapısı

Her oturum, görevin dilinde, projenizin `docs/cogitors-decisions/` dizinine kaydedilir:

```text
<project-root>
  docs/cogitors-decisions/<time-stamp>-<slug>/
  ├── antigravity-<slug>.md
  ├── brief-<slug>.md
  ├── claude-<slug>.md
  ├── codex-<slug>.md
  ├── decision-<slug>.md
  └── decisions-<slug>.html
```

---

## Hızlı Kurulum

`npx skills add erayendes/cogitors` komutunu kullanın ve dört skill'in hepsini kurun. Detaylar [burada](installation.tr.md).

---

## Sınırlar, Maliyet ve Güvenlik

- **Maliyet:** Bir oturum 8 harici model çağrısı yapar (onayladığınız zaman aşımı tekrarları hariç); çağrılar başlamadan önce kapsamı siz onaylarsınız.
- **Kaynak kod:** Müzakere kodu değiştirmez; bir kaynak dosya değişirse oturum durur.
- **Katılım:** Bir ajan başarısız olursa size sorulur; 2 katılımcının altında oturum sürmez.
- **Süre:** Çağrı başına 180 saniye, oturum başına 1800 saniye (`--timeout`, `--total-timeout`).

## Meraklısına İsmin Hikayesi

**Cogitor**'lar, Dune evreninde bedenlerinden ayrılıp koruyucu bir sıvı içinde **binlerce yılı düşünmeye adayan** kadim zihinlerdir. 
Bir sonuca acele etmeden, uzun uzun düşünüp tartıştıktan sonra varırlar. 
Bu proje de adını onlardan alıyor: birden fazla model aynı soruyu acele etmeden, kendilerini ve birbirlerini sorgulayarak düşünür. 

---

[Hata bildir](https://github.com/erayendes/cogitors/issues/new?template=bug_report.yml) · [Özellik iste](https://github.com/erayendes/cogitors/issues/new?template=feature_request.yml) · [Destek](../.github/SUPPORT.md) · [Güvenlik](../.github/SECURITY.md) · [Katkı](../.github/CONTRIBUTING.md) | [MIT](../LICENSE) © [Eray Endes](https://github.com/erayendes)