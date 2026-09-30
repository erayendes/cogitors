# Kurulum

🇬🇧 [English](installation.md) · [← README](README.tr.md)

## Hızlı Kurulum

```sh
npx skills add erayendes/cogitors
```

Dört skill'in hepsini kurun; `/codex`, `/claude` ve `/antigravity` `cogitors` motorunu kullanır.

## Gereksinimler

* Python 3.9+ (macOS veya Linux). **Harici hiçbir pip bağımlılığı yoktur.**
* `codex`, `claude` ve `agy` CLI araçlarının kurulu ve giriş yapılmış olması (en az iki ajan ikili meclis için yeterlidir).

## Tanı (Doctor)

Tüm CLI araçlarının kurulu, giriş yapılmış ve meclis oturumuna hazır olduğunu doğrulamak için:

```sh
npx cogitors doctor
```

`npx cogitors`, motoru npm üzerinden çalıştıran ince bir başlatıcıdır (Python 3.9+ yine gereklidir). Tüm alt komutlar aynı şekilde çalışır. Farklı bir Python kullanmak için `COGITORS_PYTHON` ayarlayın. Repoyu klonladıysanız aynı komutlar `python3 skills/cogitors/scripts/cogitor.py <komut>` ile de çalışır.

## Model Seçimi

1. **Kurulu modelleri listeleme:**
   ```sh
   npx cogitors models
   ```
   Sistemdeki kurulu CLI'ları (`codex`, `claude`, `agy`) ve kullanılabilir tüm modelleri (`agy models` dinamik listesi dahil) listeler.

2. **İnteraktif model seçici:**
   ```sh
   npx cogitors configure -i
   ```
   Numaralı bir terminal menüsüyle Codex, Claude ve Antigravity için model ve reasoning effort (akıl yürütme seviyesi) seçersiniz. Seçimler `~/.cogitors/config.json` içine varsayılan profil olarak kaydedilir; sonraki tüm oturumlar bu tercihleri kullanır.

3. **Doğrudan CLI bayrakları:**
   ```sh
   npx cogitors init /path/brief.md --chair antigravity --cwd "$PWD" \
     --codex-model o3 --codex-effort high \
     --claude-model sonnet
   ```

## Oturum Başlığı

Her `init` komutunda Elder, konu, heyet üyeleri, modelleri ve çalışma dizinini özetleyen bir başlık terminalde ve sohbette gösterilir. İstediğiniz an tekrar çağırabilirsiniz:

```sh
npx cogitors banner /path/run [--markdown]
```

## Elle Kurulum (Build)

Dört bağımsız skill paketini derlemek için repoyu klonlayıp şunu çalıştırın:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/package_skills.py --output dist
```

Bu komut `dist/` altında kurulabilir 4 klasör (`cogitors`, `codex`, `claude`, `antigravity`) ve her birinin `.skill` zip arşivini üretir. Derlenen klasörleri kullandığınız ajanın skill klasörüne kopyalayın:

| Ajan / Ortam | Skill Dizin Yolu |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Antigravity | `~/.gemini/config/skills/` |
| Agent Skills Standardı | `~/.agents/skills/` |
