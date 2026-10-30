# Cogitor

Participation: 3/3 — complete. Chair: codex.

Host: session-contextual (unmetered by runner).

## Answer

Cogitors için doğru sonraki adım yeni özellik yığmak değil, mevcut güven sözleşmesini sağlamlaştırmaktır. Önerilen sıra:

1. P0 — Kod, CLI ve dokümantasyonu eşitleyin. `extend_timeout` tekrar çağrılarının gerçek azami çağrı sayısını ve deadline uzamasını açıkça raporlayın; ikinci retry sırasında dolu `cli-retry` dizini hatasını ve sinyal/iptal davranışını düzeltin. `run.py` tarafından kabul edilen `ultra` effort seçeneğini Cogitors CLI ile uyumlu hale getirin. Sabit model kataloğu açıklamalarını doğrulanmış dinamik veriye dayandırın veya yalnızca öneri olduklarını belirtin. README'deki 47/51 test sayılarını gerçek 52 ile eşitleyin. Her davranış düzeltmesine küçük bir regresyon testi ekleyin.

2. P0 — Veri çıkışı ve çağrı kapsamını dispatch öncesinde görünür yapın. Sağlayıcı adları, gönderilecek dosya sayısı, toplam karakter/bayt, kapsanan turlar ve retry dahil azami çağrı sayısı makine-okunur özet olarak gösterilsin; host bu kapsam için tek ve açık kullanıcı onayı alsın. Bu oturumda kaynak gönderimi ile çapraz-tur metni için ayrı onay gerekmesi, boşluğun gerçek olduğunu gösterdi.

3. P1 — Ampirik kanıtı immutable snapshot'a ekleyin; fakat ilk sürümde Cogitors'a keyfi komut çalıştırmayın. Hostun kullanıcı onayıyla ürettiği test/lint/statik analiz raporu `--evidence-file` ile hash'lenip Tur 1'den itibaren bütün danışmanlara verilsin. Daha sonra gerçek talep oluşursa argv-listesi, timeout ve çıktı sınırı olan bir yürütücü ayrıca tasarlanabilir; shell string kabul edilmemeli.

4. P1 — Yeni bir replay motoru yerine güvenli kurtarma yönlendirmesi ekleyin. `status.next_action`, mevcut state'e göre çalıştırılabilecek tek güvenli sonraki komutu versin. Dispatch edilmemiş tur sürdürülebilir; `dispatched` işareti olup sonuç belirsizse otomatik yeniden çağrı yapılmamalıdır çünkü uzaktaki token tüketimi kanıtlanamaz.

5. P1 — Beş turlu omurgayı koruyun ve yalnızca Tur 3 prompt'unu iyileştirin: ayrışma varsa kaynak referanslı itirazlara odaklansın; ayrışma yoksa ortak varsayımların en zayıfını çürütmeye çalışsın. Erken çıkış eklemeyin.

6. P2 — Önce ölçün, sonra genişletin. 20–30 gerçek oturum boyunca tur başına süre, sağlayıcıların ham usage verisi, görüş değişimi/tekrar oranı ve protokol-uyum başarısı kaydedilsin. Ancak ölçüm desteklerse quick profil, yerel model/exec adapter, ADR, TUI veya GitHub PR botu değerlendirilsin. Sağlayıcı usage şemaları farklı olduğundan kesin para maliyeti veya karşılaştırılabilir toplam token iddiası yapılmamalı.

Kısa karar: İlk sürüm hedefi P0 maddeleri ile `--evidence-file`, `status.next_action` ve küçük Tur 3 prompt değişikliği olmalı. Ollama/vLLM, MCP, TUI, ADR, PR botu, adaptif tur sayısı ve otomatik replay şimdilik eklenmemeli.

## Agreement

Üç katılımcı sabit beş turlu yapının korunması, erken çıkışın reddedilmesi, ağır TUI/pip bağımlılıklarının eklenmemesi ve kararların salt model konsensüsü yerine ampirik kanıtla desteklenmesi gerektiğinde birleşti. Codex ve Claude ayrıca sözleşme-kod tutarsızlıklarını, veri çıkışı özetini, `--evidence-file` yaklaşımını ve `status.next_action` çözümünü aynı öncelik sırasıyla destekledi. Claude testleri sayarak gerçek toplamın 52 olduğunu doğruladı.

## Dissent

Antigravity yakın vadede `--verify-cmd`, otomatik `cogitor resume` ve Ollama/vLLM için CLI adaptörü istiyor. Codex ve Claude keyfi komut yürütmenin yeni güven yüzeyi açacağını, dispatch sonrası uzak tüketimin bilinmediği durumda otomatik resume'un çift çağrı riski taşıdığını ve yeni sağlayıcıların talep/uyum verisi olmadan erken olduğunu savunuyor. Antigravity ayrıca erken çıkış taraftarları bulunduğunu söyledi; nihai Codex ve Claude görüşleri de erken çıkışı reddettiği için bu gerçek bir heyet ayrılığı değildir.

## Uncertainties

Gerçek oturumlardaki tekrar oranı, kalite kazanımı, sağlayıcı bazlı token kullanımı ve para maliyeti ölçülmedi. CLI usage şemaları karşılaştırılabilir olmayabilir. Antigravity iki turda önceki akran bağlamını işlememiş göründü; bunun model uyumu, argv aktarımı veya yanıt kalitesi kaynaklı olup olmadığı ayrı bir conformance testi gerektirir. `--evidence-file` arayüzünün dosya boyutu, redaksiyon ve hassas veri politikası henüz tasarlanmamıştır.

## Comparison Matrix

| Participant | Round 1 Initial Stance | Round 4 Final Position | Status |
|---|---|---|---|
| `codex` | ## Codex bağımsız görüşü | ## Codex — nihai pozisyon | Active |
| `claude` | # Claude — Tur 1: Bağımsız Analiz | # Claude — Tur 4: Nihai Pozisyon | Active |
| `antigravity` | ### Pozisyon | ### İtirazların Değerlendirilmesi | Active |

## Metrics

- **Total Duration:** 496.59s
- **Participants:** 3/3 (complete)
- **Chair:** `codex`
- **`codex`:** host-unmetered
- **`claude`:** R1:42.57s, R2:35.01s, R3:25.41s, R4:27.33s
- **`antigravity`:** R1:19.78s, R2:16.24s, R3:25.72s, R4:14.76s
