# Kurulum

🇬🇧 [English](installation.md) · [← README](README.tr.md)

## Hızlı Kurulum

```sh
npx skills add erayendes/cogitors
```

Altı skill'in hepsini kurun; `/codex`, `/claude`, `/antigravity`, `/voltron` ve `/lions` `cogitors` motorunu kullanır.

## Gereksinimler

* Python 3.9+ (macOS veya Linux). **Harici hiçbir pip bağımlılığı yoktur.**
* `codex`, `claude` ve `agy` CLI araçlarının kurulu ve giriş yapılmış olması (en az iki ajan ikili meclis için yeterlidir).

## Ek Hesaplar (Voltron)

`/voltron` ve `/lions`, Elder'ın kendi oturumu dışındaki her CLI'yi çalıştırır. Claude ya da Codex'in ikinci bir girişini ayrı bir aslan olarak eklemek için `~/.cogitors/config.json` dosyasında o girişin yapılandırma klasörünü verin. Hesaplar yalnızca bu genel dosyadan okunur, projedeki `.cogitors.json` dosyasından okunmaz; böylece klonlanan bir depo, bir CLI'nin hangi hesap klasörünü yükleyeceğini seçemez:

```json
{"accounts": {"claude-alt": {"agent": "claude", "config_dir": "~/.claude-alt"},
              "codex-alt": {"agent": "codex", "config_dir": "~/.codex-alt"}}}
```

Bir hesap kendi `model` ve `effort` değerini de belirleyebilir; belirlemezse kayıtlı modeller kullanılır. Voltron'u oluşturan beş aslan gibi, aynı anda en fazla beş aslan çalışır; `--exclude AD` bir aslanı dışarıda bırakır. `cogitor.py voltron --elder claude --check` model çağırmadan aslanları listeler ve girişlerini kontrol eder.

## Kota ve Yönlendirme (isteğe bağlı)

`cogitor.py quota [--json]` her aslanın kalan kotasını gösterir; model çağırmaz, ağa çıkmaz, token okumaz. `~/.cogitors/config.json` içindeki iki isteğe bağlı bölüm bunu besler:

```json
{"usage": {"claude": "~/.claude/statusline-usage.json"},
 "routing": {"light": {"codex": {"model": "gpt-6-luna", "effort": "low"}},
             "deep": {"codex": {"model": "gpt-6.2-astra", "effort": "high"}}}}
```

* `usage`, bir Claude aslanını (`claude` ya da bir Claude hesabı) durum çubuğunuzun yazdığı Claude Code status-line JSON anlık görüntüsüne bağlar. Dosyada `rate_limits.five_hour` ve `rate_limits.seven_day` bulunur; her biri `used_percentage` ve `resets_at` (epoch saniye) içerir, pencerelerden biri eksik olabilir. Durum çubuğu yalnızca etkileşimli oturumlarda çalışır; yalnızca aslan olarak kullanılan bir hesabın anlık görüntüsü eskir ve `unknown` görünür. Her hesaba ayrı bir yol verin (örneğin `CLAUDE_CONFIG_DIR`'e göre).
* `routing`, bir katmanı (`light`, `standard`, `deep`) ve bir ajanı (`codex`, `claude`, `antigravity`) bir `model` ve `effort` değerine bağlar; tüm alanlar isteğe bağlıdır. Planda `tier` taşıyan aslan modelini ve effort'unu buradan alır; plandaki açık `model` ya da `effort` önceliklidir. Bir katman sıralı bir yedek listesi de olabilir, `[{"lion": "codex", "model": "...", "effort": "high"}, {"lion": "claude", "model": "opus"}]`: plandaki aslan kendi adımının ayarlarını alır, kesin bir kota hatasından sonra Elder parçayı kotası tükenmemiş ve kendisi olmayan ilk adıma verir. Liste sırası, kotası en erken yenilenen aslanı seçme kuralından önce gelir. `quota --json` her listeyi `fallbacks` altında gösterir.
* Codex için ayar gerekmez: kota, yerleşik `codex` aslanı için `~/.codex`, ek hesaplar için hesabın `config_dir` klasöründeki `sessions/` altında en yeni altı `rollout-*.jsonl` dosyasındaki en son hesap geneli ölçümden (`limit_id` `codex`) okunur.
* Antigravity: kotasını okumak için `usage`'a `"antigravity": "acp"` ekleyin. Motor `agy acp`'yi yaklaşık iki saniye açar, agy'nin yerel dil sunucusundan kendi kota özetini ister (model çağrısı yok, token okunmaz; servise agy kendisi bağlanır), boş oturumu siler ve sonucu `~/.cogitors/agy-quota.json`'da beş dakika saklar. Model–kota grubu eşlemesi sabit model adlarıyla değil, doğrudan agy'nin kendi kota özetinden ve `agy models` görünen adlarından türetilir; böylece yeni modeller kendiliğinden doğru gruba düşer. Bu ayar yoksa yalnızca bekleme süreleri (cooldown) uygulanır.
* Bir aslan kesin bir kota hatası alırsa motor, `~/.cogitors/quota.json` dosyasına (mod 0600) bir cooldown yazar; süreyi hata metnindeki sıfırlanma zamanından alır, yoksa bir saat varsayar; daha uzun bir kayıt varsa o korunur, süre belirtmeyen bir 429 ya da bir dakikadan kısa süren geçici kısıtlama kaydedilmez. Dosyada hata metninin tamamı değil, yalnızca kota ifadesi tutulur. Süresi dolan cooldown'lar yok sayılır; hepsini temizlemek için dosyayı silin.

`cogitor.py voltron`, kotası tükenmiş bir plan aslanını hiçbir model çalışmadan reddeder. Her çalışma, `~/.cogitors/runs.jsonl` dosyasına aslan başına bir satır ekler (ayarlar, durum, süre, varsa usage, yoksa `unknown`; istem, yanıt ya da hata metni yazılmaz). Her `/voltron` ya da `/lions` önerisi ve kullanıcı yanıtı `cogitor.py proposal --kind voltron|lions --answer accepted|declined` ile kaydedilir; böylece öneri eşiği ve Elder yedeği verilere göre ayarlanabilir. `cogitor.py metrics` çalışmaları aslan ve model başına ortalama süre, başarı ve kota oranı olarak özetler ve `proposals` altında türe göre kabul edilen ve reddedilen sayılarını bildirir.

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

Altı bağımsız skill paketini derlemek için repoyu klonlayıp şunu çalıştırın:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/package_skills.py --output dist
```

Bu komut `dist/` altında kurulabilir 6 klasör (`cogitors`, `codex`, `claude`, `antigravity`, `voltron`, `lions`) ve her birinin `.skill` zip arşivini üretir. Derlenen klasörleri kullandığınız ajanın skill klasörüne kopyalayın:

| Ajan / Ortam | Skill Dizin Yolu |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Antigravity | `~/.gemini/config/skills/` |
| Agent Skills Standardı | `~/.agents/skills/` |
